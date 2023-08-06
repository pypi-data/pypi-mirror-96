# Copyright 2015 Planet Labs, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import os
import re
from os import environ
from six.moves.urllib.parse import urlparse
from memoized_property import memoized_property
import simplejson as json
from datalake import (
    File,
    StreamingFile,
    StreamingHTTPFile,
)
from .common.errors import InsufficientConfiguration
from .common import Metadata
import requests
from io import BytesIO
import errno

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.s3.connection import NoHostProvided
import math
from logging import getLogger
log = getLogger('datalake-archive')

# The name in s3 of the datalake metadata document
METADATA_NAME = 'datalake'

MB_B = 1024 ** 2


# S3 limit for PUT request is 5GB
# S3 limit for minimum multipart upload size is 5MB
def CHUNK_SIZE():
    return int(float(os.getenv('DATALAKE_CHUNK_SIZE_MB', 100)) * MB_B)


_connect_timeout = None
_read_timeout = None


def TIMEOUT():
    """
    A tuple of the connect and read timeout, with defaults using the
    recommendations from the requests docs:
     https://requests.readthedocs.io/en/master/user/advanced/#timeouts

    :return: tuple of floats
    """
    return CONNECT_TIMEOUT(), READ_TIMEOUT(),


def CONNECT_TIMEOUT():
    global _connect_timeout
    if _connect_timeout is None:
        _connect_timeout = float(os.getenv('DATALAKE_CONNECT_TIMEOUT_S', 3.05))
    return _connect_timeout


def READ_TIMEOUT():
    global _read_timeout
    if _read_timeout is None:
        _read_timeout = float(os.getenv('DATALAKE_READ_TIMEOUT_S', 31))
    return _read_timeout


class UnsupportedStorageError(Exception):
    pass


class DatalakeHttpError(Exception):
    pass


class InvalidDatalakePath(Exception):
    pass


class Archive(object):

    def __init__(self, storage_url=None, http_url=None):
        self.storage_url = storage_url or environ.get('DATALAKE_STORAGE_URL')
        self._validate_storage_url()
        self._http_url = http_url

    def _validate_storage_url(self):
        if not self.storage_url:
            raise UnsupportedStorageError('Please specify a storage URL')

        if not self._parsed_storage_url.scheme == 's3':
            msg = 'Unsupported storage scheme ' + \
                self._parsed_storage_url.scheme
            raise UnsupportedStorageError(msg)

        self.storage_url = self.storage_url.rstrip('/')

    @property
    def _parsed_storage_url(self):
        return urlparse(self.storage_url)

    def list(self, what, start=None, end=None, where=None, work_id=None):
        '''list metadata records for specified files

        Args:
          what: what kind of file to list (e.g., syslog, nginx)

          start: List only files after this time. This argument is
          polymorphic. datetimes are accepted. Strings will be converted to
          datetimes, so inputs like `2015-12-21` and `2015-12-21T09:11:14.08Z`
          are acceptable. Floats will be interpreted as UTC seconds since the
          epoch. Integers will be interpreted as milliseconds since the epoch.

          end: List only files before this time. Same semantics as start.

          where: List only files from this host.

          work_id: Show only files with this work id.

        returns a generator that lists records of the form:
            {
                'url': <url>,
                'metadata': <metadata>,
            }
        '''
        url = self.http_url + '/v0/archive/files/'
        params = dict(
            what=what,
            start=None if start is None else Metadata.normalize_date(start),
            end=None if end is None else Metadata.normalize_date(end),
            where=where,
            work_id=work_id,
        )
        response = self._requests_get(url, params=params)

        while True:
            self._check_http_response(response)
            response = response.json()
            for record in response['records']:
                yield record
            if response['next']:
                response = self._requests_get(response['next'])
            else:
                break

    def latest(self, what, where, lookback=None):
        url = self.http_url + '/v0/archive/latest/{}/{}'.format(what, where)
        params = dict(
            lookback=lookback,
        )
        response = self._requests_get(url, params=params)
        self._check_http_response(response)
        return response.json()

    @property
    def http_url(self):
        self._http_url = self._http_url or environ.get('DATALAKE_HTTP_URL')
        if self._http_url is None:
            raise InsufficientConfiguration('Please specify DATALAKE_HTTP_URL')
        return self._http_url.rstrip('/')

    def _check_http_response(self, response):
        if response.status_code in (400, 404):
            err = response.json()
            msg = '{} ({})'.format(err['message'], err['code'])
            raise DatalakeHttpError(msg)

        elif response.status_code != 200:
            msg = 'Datalake HTTP API failed: {} ({})'
            msg = msg.format(response.content, response.status_code)
            raise DatalakeHttpError(msg)

    def prepare_metadata_and_push(self, filename, **metadata_fields):
        '''push a file to the archive with the specified metadata

        Args:
            filename: path of the file to push

            metadata_fields: metadata fields for file. Missing fields will be
            added if they can be determined. Othwerise, InvalidDatalakeMetadata
            will be raised.

        returns the url to which the file was pushed.
        '''
        f = File.from_filename(filename, **metadata_fields)
        return self.push(f)

    def push(self, f):
        '''push a file f to the archive

        Args:
            f is a datalake.File

        returns the url to which the file was pushed.
        '''
        self._upload_file(f)
        return self.url_from_file(f)

    def _upload_file(self, f):
        key = self._s3_key_from_metadata(f)

        spos = f.tell()
        f.seek(0, os.SEEK_END)
        f_size = f.tell()
        # seek back to the correct position.
        f.seek(spos)

        num_chunks = int(math.ceil(f_size / float(CHUNK_SIZE())))
        log.info("Uploading {} ({} B / {} chunks)".format(
            key.name, f_size, num_chunks))
        if num_chunks <= 1:
            key.set_metadata(METADATA_NAME, json.dumps(f.metadata))
            completed_size = key.set_contents_from_file(f)
            log.info("Upload of {} complete (1 part / {} B).".format(
                key.name, completed_size))
            return
        completed_size = 0
        chunk = 0
        mp = key.bucket.initiate_multipart_upload(
            key.name, metadata={
                METADATA_NAME: json.dumps(f.metadata)
            })
        try:
            for chunk in range(1, num_chunks + 1):
                part = mp.upload_part_from_file(
                    f, chunk, size=CHUNK_SIZE())
                completed_size += part.size
                log.debug("Uploaded chunk {}/{} ({}B)".format(
                    chunk, num_chunks, part.size))
        except:  # NOQA
            # Any exception we want to attempt to cancel_upload, otherwise
            # AWS will bill us every month indefnitely for storing the
            # partial-uploaded chunks.
            log.exception("Upload of {} failed on chunk {}".format(
                key.name, chunk))
            mp.cancel_upload()
            raise
        else:
            completed = mp.complete_upload()
            log.info("Upload of {} complete ({} parts / {} B).".format(
                completed.key_name, chunk, completed_size))

    def url_from_file(self, f):
        return self._get_s3_url(f)

    _URL_FORMAT = 's3://{bucket}/{key}'

    def fetch(self, url, stream=False):
        '''fetch the specified url and return it as a datalake.File

        Args:

        url: the url to fetch. Both s3 and http(s) are supported.
        stream: if true, return a StreamingFile
        '''
        if url.startswith('s3://'):
            return self._fetch_s3_url(url, stream=stream)
        elif self._is_valid_http_url(url):
            return self._fetch_http_url(url, stream=stream)
        else:
            msg = '{} does not appear to be a fetchable url'
            msg = msg.format(url)
            raise InvalidDatalakePath(msg)

    def _is_valid_http_url(self, url):
        return url.startswith('http') and url.endswith('/data')

    def _fetch_s3_url(self, url, stream=False):
        k = self._get_key_from_url(url)
        m = self._get_metadata_from_key(k)
        if stream:
            return StreamingFile(k, **m)
        fd = BytesIO()
        k.get_contents_to_file(fd)
        fd.seek(0)
        return File(fd, **m)

    def _fetch_http_url(self, url, stream=False):
        m = self._get_metadata_from_http_url(url)
        k = self._stream_http_url(url)
        if stream:
            return StreamingHTTPFile(k, **m)
        fd = BytesIO()
        for block in k.iter_content(1024):
            fd.write(block)
        fd.seek(0)
        return File(fd, **m)

    def _stream_http_url(self, url):
        response = self._requests_get(url, stream=True)
        self._check_http_response(response)
        return response

    def _get_metadata_from_http_url(self, url):
        self._validate_fetch_url(url)
        p = re.compile('/data$')
        url = p.sub('/metadata', url)
        response = self._requests_get(url, stream=True)
        self._check_http_response(response)
        return response.json()

    def fetch_to_filename(self, url, filename_template=None):
        '''fetch the specified url and write it to a file

        Args:

        url: the url to fetch

        filename_template: a template describing where to store files. For
        example, to store a file based on `what` it is, you could pass
        something like {what}.log. Or if you gathering many `what`'s that
        originate from many `where`'s you might want to use something like
        {where}/{what}-{start}.log. If filename_template is None (the default),
        files are stored in the current directory and the filenames are the ids
        from the metadata.

        Returns the filename written.
        '''
        k = None
        if url.startswith('s3://'):
            k = self._get_key_from_url(url)
            m = self._get_metadata_from_key(k)
        else:
            m = self._get_metadata_from_http_url(url)
        fname = self._get_filename_from_template(filename_template, m)
        dname = os.path.dirname(fname)
        self._mkdirs(dname)
        if k:
            k.get_contents_to_filename(fname)
        else:
            with open(fname, 'wb') as fh:
                for buf in self.fetch(url, stream=True).iter_content():
                    fh.write(buf)
        return fname

    def _mkdirs(self, path):
        if path == '':
            return
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def _get_key_from_url(self, url):
        self._validate_fetch_url(url)
        key_name = self._get_key_name_from_url(url)
        k = self._s3_bucket.get_key(key_name)
        if k is None:
            msg = 'Failed to find {} in the datalake.'.format(url)
            raise InvalidDatalakePath(msg)
        return k

    def _get_metadata_from_key(self, key):
        m = key.get_metadata(METADATA_NAME)
        return Metadata.from_json(m)

    def _get_filename_from_template(self, template, metadata):
        if template is None:
            template = '{id}'
        try:
            return template.format(**metadata)
        except KeyError as e:
            m = '"{}" does not appear in the datalake metadata'
            m = m.format(str(e))
            raise InvalidDatalakePath(m)
        except ValueError as e:
            raise InvalidDatalakePath(str(e))

    def _get_key_name_from_url(self, url):
        parts = urlparse(url)
        if not parts.path:
            msg = '{} is not a valid datalake url'.format(url)
            raise InvalidDatalakePath(msg)

        return parts.path

    def _validate_fetch_url(self, url):
        valid_base_urls = (self.storage_url, self.http_url)
        if not [u for u in valid_base_urls if url.startswith(u)]:
            msg = 'url {} does not start with the configured storage urls {}.'
            msg = msg.format(url, valid_base_urls)
            raise InvalidDatalakePath(msg)

    def _get_s3_url(self, f):
        key = self._s3_key_from_metadata(f)
        return self._URL_FORMAT.format(bucket=self._s3_bucket_name,
                                       key=key.name)

    @property
    def _s3_bucket_name(self):
        return self._parsed_storage_url.netloc

    @memoized_property
    def _s3_bucket(self):
        # Note: we pass validate=False because we may just have push
        # permissions. If validate is not False, boto tries to list the
        # bucket. And this will 403.
        return self._s3_conn.get_bucket(self._s3_bucket_name, validate=False)

    _KEY_FORMAT = '{id}/data'

    def _s3_key_from_metadata(self, f):
        # For performance reasons, s3 keys should start with a short random
        # sequence:
        # https://aws.amazon.com/blogs/aws/amazon-s3-performance-tips-tricks-seattle-hiring-event/
        # http://docs.aws.amazon.com/AmazonS3/latest/dev/request-rate-perf-considerations.html
        key_name = self._KEY_FORMAT.format(**f.metadata)
        return Key(self._s3_bucket, name=key_name)

    @property
    def _s3_host(self):
        r = environ.get('AWS_REGION') or environ.get('AWS_DEFAULT_REGION')
        if r is not None:
            return 's3-' + r + '.amazonaws.com'
        else:
            return NoHostProvided

    @property
    def _s3_conn(self):
        if not hasattr(self, '_conn'):
            k = environ.get('AWS_ACCESS_KEY_ID')
            s = environ.get('AWS_SECRET_ACCESS_KEY')
            self._conn = S3Connection(aws_access_key_id=k,
                                      aws_secret_access_key=s,
                                      host=self._s3_host)
        return self._conn

    def _requests_get(self, url, **kwargs):
        return self._session.get(url, timeout=TIMEOUT(), **kwargs)

    @memoized_property
    def _session(self):
        return requests.Session()

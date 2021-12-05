import copy
import json
import unittest
from typing import Dict
from urllib.parse import urlparse, parse_qs

import httpretty
import jwt
from hamcrest import assert_that, instance_of, is_, starts_with, has_entry

from media_platform.auth.app_authenticator import AppAuthenticator
from media_platform.http_client.authenticated_http_client import AuthenticatedHTTPClient
from media_platform.metadata.video.transparency import Transparency
from media_platform.service.callback import Callback
from media_platform.service.destination import Destination
from media_platform.service.file_descriptor import FileDescriptor, FileType, FileMimeType, ACL
from media_platform.service.file_service.attachment import Attachment
from media_platform.service.file_service.extract_metadata_request import Detection
from media_platform.service.file_service.file_service import FileService
from media_platform.service.file_service.inline import Inline
from media_platform.service.file_service.upload_configuration import UploadConfiguration
from media_platform.service.lifecycle import Lifecycle, Action
from media_platform.service.list_request import OrderBy
from media_platform.service.rest_result import RestResult
from media_platform.service.source import Source

metadata_response = RestResult(0, 'OK', {
    'mediaType': 'video',
    'fileDescriptor': {
        'acl': 'private',
        'hash': None,
        'id': '2de4305552004e0b9076183651030646',
        'mimeType': 'video/mp4',
        'path': '/videos/animals/cat.mp4',
        'size': 15431333,
        'type': '-'
    },
    'basic': {
        'interlaced': False,
        'videoStreams': [
            {
                'codecLongName': 'MPEG-4 part 2',
                'height': 720,
                'duration': 59351,
                'bitrate': 1950467,
                'index': 0,
                'rFrameRate': '3000/100',
                'codecTag': 'mp4v',
                'avgFrameRate': '2997/100',
                'codecName': 'mpeg4',
                'width': 1280,
                'sampleAspectRatio': '1:1',
                'displayAspectRatio': '16:9',
                'fieldOrder': None,
                'disposition': []
            }
        ],
        'audioStreams': [
            {
                'codecLongName': 'AAC (Advanced Audio Coding)',
                'index': 1,
                'codecTag': 'mp4a',
                'codecName': 'aac',
                'duration': 59351,
                'bitrate': 128322
            }
        ],
        'format': {
            'duration': 59351,
            'formatLongName': 'QuickTime / MOV',
            'bitrate': 2085272,
            'size': 15476893
        }
    }
})

metadata_response_with_transparency = copy.deepcopy(metadata_response)
metadata_response_with_transparency.payload['basic']['transparency'] = Transparency.video_alpha


class TestFileService(unittest.TestCase):
    authenticator = AppAuthenticator('app', 'secret')
    authenticated_http_client = AuthenticatedHTTPClient(authenticator)

    file_service = FileService('fish.barrel', authenticated_http_client, 'app', authenticator)

    @httpretty.activate
    def test_file_request(self):
        payload = FileDescriptor('/fish.txt', 'file-id', FileType.file, 'text/plain', 123).serialize()
        response_body = RestResult(0, 'OK', payload)
        httpretty.register_uri(
            httpretty.GET,
            'https://fish.barrel/_api/files?path=%2Ffist.txt',
            body=json.dumps(response_body.serialize())
        )

        file_descriptor = self.file_service.file_request().set_path('/fish.txt').execute()

        assert_that(file_descriptor.serialize(), is_(payload))
        assert_that(file_descriptor, instance_of(FileDescriptor))
        assert_that(httpretty.last_request().querystring, is_({
            'path': ['/fish.txt']
        }))

    @httpretty.activate
    def test_delete_file_request(self):
        response_body = RestResult(0, 'OK', None)
        httpretty.register_uri(
            httpretty.DELETE,
            'https://fish.barrel/_api/files?path=%2Ffist.txt',
            body=json.dumps(response_body.serialize())
        )

        self.file_service.delete_file_request().set_path('/fish.txt').execute()

        assert_that(httpretty.last_request().querystring, is_({
            'path': ['/fish.txt']
        }))

    @httpretty.activate
    def test_create_file_request(self):
        payload = FileDescriptor('/fish', 'file-id', FileType.directory, FileMimeType.directory, 0).serialize()
        response_body = RestResult(0, 'OK', payload)
        httpretty.register_uri(
            httpretty.POST,
            'https://fish.barrel/_api/files',
            body=json.dumps(response_body.serialize())
        )

        file_descriptor = self.file_service.create_file_request().set_path('/fish').execute()

        assert_that(file_descriptor.serialize(), is_(payload))
        assert_that(file_descriptor, instance_of(FileDescriptor))
        assert_that(json.loads(httpretty.last_request().body),
                    is_({
                        'mimeType': FileMimeType.directory,
                        'path': '/fish',
                        'size': 0,
                        'type': FileType.directory,
                        'acl': ACL.public,
                        'id': None,
                        'bucket': None
                    }))

    @httpretty.activate
    def test_create_files_request(self):
        expected_file_descriptor = FileDescriptor('/fish', 'file-id', FileType.directory, FileMimeType.directory, 0)
        expected_response_body = RestResult(0, 'OK', expected_file_descriptor.serialize())

        httpretty.register_uri(
            httpretty.POST,
            'https://fish.barrel/_api/files',
            body=json.dumps(expected_response_body.serialize())
        )

        response = self.file_service.create_files_request().add_file(
            self.file_service.create_file_request().set_path('/fish')
        ).execute()

        self.assertEqual(1, len(response.file_descriptors))
        self.assertIsInstance(response.file_descriptors, list)
        self.assertIsInstance(response.file_descriptors[0], FileDescriptor)
        self.assertEqual(expected_file_descriptor.serialize(), response.file_descriptors[0].serialize())

        self.assertEqual(
            {
                'mimeType': FileMimeType.directory,
                'path': '/fish',
                'size': 0,
                'type': FileType.directory,
                'acl': ACL.public,
                'id': None,
                'bucket': None
            },
            json.loads(httpretty.last_request().body)
        )

    @httpretty.activate
    def test_update_file_request(self):
        payload = FileDescriptor('/fish.txt', 'file-id', FileType.file, 'text/plain', 18).serialize()
        response_body = RestResult(0, 'OK', payload)
        httpretty.register_uri(
            httpretty.PUT,
            'https://fish.barrel/_api/files',
            body=json.dumps(response_body.serialize())
        )

        file_descriptor = self.file_service.update_file_request().set_path('/fish.txt'). \
            set_acl(ACL.public).set_mime_type('image/jpg').execute()

        assert_that(file_descriptor.serialize(), is_(payload))
        assert_that(file_descriptor, instance_of(FileDescriptor))
        assert_that(json.loads(httpretty.last_request().body),
                    is_({
                        'path': '/fish.txt',
                        'id': None,
                        'acl': 'public',
                        'mimeType': 'image/jpg'
                    }))

    @httpretty.activate
    def test_upload_configuration_request(self):
        response_body = RestResult(0, 'OK', {
            'uploadUrl': 'url'
        })
        httpretty.register_uri(
            httpretty.POST,
            'https://fish.barrel/_api/v3/upload/configuration',
            body=json.dumps(response_body.serialize())
        )

        upload_configuration = self.file_service.upload_configuration_request().set_path('/fish.txt').execute()

        assert_that(upload_configuration, instance_of(UploadConfiguration))
        assert_that(upload_configuration.upload_url, is_('url'))
        assert_that(json.loads(httpretty.last_request().body),
                    is_({
                        'mimeType': None,
                        'bucket': None,
                        'path': '/fish.txt',
                        'size': None,
                        'acl': None,
                        'callback': None,
                        'protocol': None
                    }))

    @httpretty.activate
    def test_upload_configuration_request_tus(self):
        response_body = RestResult(0, 'OK', {
            'uploadUrl': 'url'
        })
        httpretty.register_uri(
            httpretty.POST,
            'https://fish.barrel/_api/v3/upload/configuration',
            body=json.dumps(response_body.serialize())
        )

        upload_configuration = self.file_service.upload_configuration_request().set_path('/fish.txt').set_protocol(
            'tus'
        ).execute()

        assert_that(upload_configuration, instance_of(UploadConfiguration))
        assert_that(upload_configuration.upload_url, is_('url'))
        assert_that(json.loads(httpretty.last_request().body),
                    is_({
                        'mimeType': None,
                        'bucket': None,
                        'path': '/fish.txt',
                        'size': None,
                        'acl': None,
                        'callback': None,
                        'protocol': 'tus'
                    }))

    @httpretty.activate
    def test_upload_file_request(self):
        url_response_body = RestResult(0, 'OK', {
            'uploadUrl': 'https://fish.barrel/v3/cryptic-path'
        })
        httpretty.register_uri(
            httpretty.POST,
            'https://fish.barrel/_api/v3/upload/configuration',
            body=json.dumps(url_response_body.serialize())
        )

        upload_mime_type = 'text/plain'
        upload_response_body = RestResult(0, 'OK',
                                          FileDescriptor('/fish.txt', 'file-id', FileType.file, upload_mime_type,
                                                         123).serialize()
                                          )
        httpretty.register_uri(
            httpretty.PUT,
            'https://fish.barrel/v3/cryptic-path',
            body=json.dumps(upload_response_body.serialize())
        )

        upload_content = 'some content'
        upload_lifecycle = Lifecycle(age=30, action=Action.delete)
        file_descriptor = self.file_service.upload_file_request() \
            .set_acl(ACL.private).set_path('/fish.txt').set_content(upload_content).set_mime_type(upload_mime_type) \
            .set_lifecycle(upload_lifecycle).set_filename('fishenzon').execute()

        assert_that(file_descriptor, instance_of(FileDescriptor))
        assert_that(file_descriptor.path, is_('/fish.txt'))

    @httpretty.activate
    def test_import_file_request(self):
        payload = {
            'status': 'pending',
            'specification': {
                'sourceUrl': 'http://source.url/filename.txt',
                'destination': {
                    'directory': '/fish',
                    'acl': 'public'
                }
            },
            'dateCreated': '2017-05-23T08:34:43Z',
            'sources': [],
            'result': None,
            'id': '71f0d3fde7f348ea89aa1173299146f8_19e137e8221b4a709220280b432f947f',
            'dateUpdated': '2017-05-23T08:34:43Z',
            'type': 'urn:job:import.file',
            'groupId': '71f0d3fde7f348ea89aa1173299146f8',
            'issuer': 'urn:app:app-id-1'
        }
        response_body = RestResult(0, 'OK', payload)
        httpretty.register_uri(
            httpretty.POST,
            'https://fish.barrel/_api/import/file',
            body=json.dumps(response_body.serialize())
        )

        import_file_job = self.file_service.import_file_request().set_destination(
            Destination('/img.png')
        ).set_source_url(
            'source-url'
        ).set_job_callback(Callback('http://callback.com', {'key': 'value'})
                           ).execute()

        self.assertEqual('71f0d3fde7f348ea89aa1173299146f8_19e137e8221b4a709220280b432f947f', import_file_job.id)
        self.assertEqual({'sourceUrl': 'source-url',
                          'destination': {
                              'directory': None,
                              'path': '/img.png',
                              'lifecycle': None,
                              'acl': 'public',
                              'bucket': None
                          },
                          'externalAuthorization': None,
                          'jobCallback': {
                              'url': 'http://callback.com',
                              'attachment': {'key': 'value'},
                              'headers': None,
                              'passthrough': False
                          }
                          }, json.loads(httpretty.last_request().body))

    @httpretty.activate
    def test_sync_import_file_request(self):
        file_descriptor = FileDescriptor('/img.png', 'file-id', FileType.file, 'image/png', 123).serialize()
        response_body = RestResult(0, 'OK', file_descriptor)
        httpretty.register_uri(
            httpretty.PUT,
            'https://fish.barrel/_api/import/file',
            body=json.dumps(response_body.serialize())
        )

        imported_file = self.file_service.sync_import_file_request().set_destination(
            Destination('/img.png')
        ).set_source_url(
            'source-url'
        ).execute()

        self.assertEqual(
            {
                'destination': {
                    'acl': 'public',
                    'bucket': None,
                    'directory': None,
                    'lifecycle': None,
                    'path': '/img.png'
                },
                'externalAuthorization': None,
                'sourceUrl': 'source-url'
            },
            json.loads(httpretty.last_request().body)
        )
        self.assertEqual(file_descriptor, imported_file.serialize())

    @httpretty.activate
    def test_copy_file_request(self):
        response_body = RestResult(0, 'OK', FileDescriptor('/file.copy.txt', 'file-new-id', FileType.file, 'text/plain',
                                                           123).serialize())
        httpretty.register_uri(
            httpretty.POST,
            'https://fish.barrel/_api/copy/file',
            body=json.dumps(response_body.serialize())
        )

        file_descriptor = self.file_service.copy_file_request().set_source(
            Source('/file.txt')
        ).set_destination(
            Destination('/file.copy.txt')
        ).execute()

        assert_that(file_descriptor, instance_of(FileDescriptor))
        assert_that(file_descriptor.path, is_('/file.copy.txt'))
        assert_that(json.loads(httpretty.last_request().body),
                    is_({
                        'source': {
                            'path': '/file.txt',
                            'fileId': None
                        },
                        'destination': {
                            'directory': None,
                            'path': '/file.copy.txt',
                            'lifecycle': None,
                            'acl': 'public',
                            'bucket': None
                        }
                    }))

    @httpretty.activate
    def test_download_file_request__attachment(self):
        httpretty.register_uri(
            httpretty.GET,
            'https://fish.barrel/file.txt?filename=attachment-filename.txt',
            body='barks!',
            adding_headers={'Content-Disposition': 'attachment; filename*=UTF-8\'\'attachment-filename.txt'}
        )

        with self.file_service.download_file_request().set_path('/file.txt'). \
                set_attachment(Attachment('attachment-filename.txt')).execute() as response:
            dogs = next(response.iter_lines())

            assert_that(dogs.decode('utf-8'), is_('barks!'))
            assert_that(response.headers['Content-Disposition'],
                        is_('attachment; filename*=UTF-8\'\'attachment-filename.txt'))

    @httpretty.activate
    def test_download_file_request__inline_with_filename(self):
        httpretty.register_uri(
            httpretty.GET,
            'https://fish.barrel/file.txt',
            body='barks!',
            adding_headers={'Content-Disposition': 'inline; filename*=UTF-8\'\'inline-filename.txt'}
        )

        download_request = self.file_service.download_file_request(). \
            set_path('/file.txt'). \
            set_inline(Inline('inline-filename.txt'))

        with download_request.execute() as response:
            dogs = next(response.iter_lines())

            assert_that(dogs.decode('utf-8'), is_('barks!'))
            assert_that(response.headers['Content-Disposition'], is_('inline; filename*=UTF-8\'\'inline-filename.txt'))

    def test_download_file_request_url_attachment(self):
        file_name = 'file-name'
        signed_url = self.file_service.download_file_request().set_path('/file.txt'). \
            set_attachment(Attachment(file_name)).url()

        assert_that(signed_url, starts_with('https://fish.barrel/file.txt?token='))

        claims = self._parse_download_url_token(signed_url)
        attachment = claims['attachment']
        assert_that(attachment, has_entry('filename', file_name))

    def test_download_file_request_url_inline(self):
        file_name = 'file-name'
        signed_url = self.file_service.download_file_request().set_path('/file.txt'). \
            set_inline(Inline(file_name)).url()

        assert_that(signed_url, starts_with('https://fish.barrel/file.txt?token='))

        claims = self._parse_download_url_token(signed_url)
        inline = claims['inline']
        assert_that(inline, has_entry('filename', file_name))

    def _parse_download_url_token(self, signed_url: str) -> Dict:
        parse_result = urlparse(signed_url)
        query_params = parse_qs(parse_result.query)
        token_data = query_params.get('token')
        return jwt.decode(token_data[0], options={"verify_signature": False})

    @httpretty.activate
    def test_download_file_request(self):
        httpretty.register_uri(
            httpretty.GET,
            'https://fish.barrel/file.txt',
            body='barks!'
        )

        with self.file_service.download_file_request().set_path('/file.txt').execute() as response:
            dogs = next(response.iter_lines())

            assert_that(dogs.decode('utf-8'), is_('barks!'))

    @httpretty.activate
    def test_file_list_request(self):
        response_body = RestResult(0, 'OK', {
            'nextPageToken': 'next page',
            'files': [FileDescriptor('/fish.txt', 'file-id', FileType.file, 'text/plain', 123).serialize()]
        })
        httpretty.register_uri(
            httpretty.GET,
            'https://fish.barrel/_api/files/ls_dir',
            body=json.dumps(response_body.serialize())
        )

        file_list = self.file_service.file_list_request().set_path('/files').set_next_page_token('next') \
            .set_order_by(OrderBy.name).set_page_size(12).set_recursive(True).set_type(FileType.file).execute()

        assert_that(file_list.next_page_token, is_('next page'))
        assert_that(httpretty.last_request().querystring, is_({
            'nextPageToken': ['next'],
            'orderBy': ['name'],
            'pageSize': ['12'],
            'r': ['yes'],
            'path': ['/files'],
            'type': ['-'],
            'orderDirection': ['des']
        }))

    @httpretty.activate
    def test_file_metadata_request(self):
        httpretty.register_uri(
            httpretty.GET,
            'https://fish.barrel/_api/files/metadata',
            body=json.dumps(metadata_response.serialize())
        )

        file_metadata = self.file_service.file_metadata_request().set_path('/videos/animals/cat.mp4').execute()

        assert_that(file_metadata.file_descriptor.file_id, is_('2de4305552004e0b9076183651030646'))
        assert_that(httpretty.last_request().querystring), is_({
            'path': ['/videos/animals/cat.mp4'],
        })

    @httpretty.activate
    def test_extract_metadata_request(self):
        httpretty.register_uri(
            httpretty.GET,
            'https://fish.barrel/_api/files/metadata/extract',
            body=json.dumps(metadata_response.serialize())
        )

        file_metadata = self.file_service.extract_metadata_request().set_path('/videos/animals/cat.mp4').execute()

        assert_that(file_metadata.file_descriptor.file_id, is_('2de4305552004e0b9076183651030646'))
        assert_that(httpretty.last_request().querystring), is_({
            'path': ['/videos/animals/cat.mp4'],
        })

    @httpretty.activate
    def test_extract_metadata_request__with_transparency_detection(self):
        httpretty.register_uri(
            httpretty.GET,
            'https://fish.barrel/_api/files/metadata/extract',
            body=json.dumps(metadata_response_with_transparency.serialize())
        )

        file_metadata = self.file_service.extract_metadata_request(). \
            set_path('/videos/animals/cat.mp4'). \
            add_detection(Detection.transparency). \
            execute()

        assert_that(file_metadata.basic.transparency, is_(Transparency.video_alpha))

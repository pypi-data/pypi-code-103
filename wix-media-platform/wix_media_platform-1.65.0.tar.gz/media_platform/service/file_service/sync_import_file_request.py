from __future__ import annotations

from typing import cast, Dict

from media_platform.http_client.authenticated_http_client import AuthenticatedHTTPClient
from media_platform.service.destination import Destination
from media_platform.service.file_descriptor import FileDescriptor
from media_platform.service.file_service.external_authorization import ExternalAuthorization
from media_platform.service.media_platform_request import MediaPlatformRequest


class SyncImportFileRequest(MediaPlatformRequest):
    def __init__(self, authenticated_http_client: AuthenticatedHTTPClient, base_url: str):
        super().__init__(authenticated_http_client, 'PUT', base_url + '/import/file', FileDescriptor)
        self.source_url = None
        self.external_authorization = None
        self.destination = None

    def set_source_url(self, source_url: str) -> SyncImportFileRequest:
        self.source_url = source_url
        return self

    def set_external_authorization(self, external_authorization: ExternalAuthorization) -> SyncImportFileRequest:
        self.external_authorization = external_authorization
        return self

    def set_destination(self, destination: Destination) -> SyncImportFileRequest:
        self.destination = destination
        return self

    def execute(self) -> FileDescriptor:
        return cast(FileDescriptor, super().execute())

    def _params(self) -> Dict:
        return {
            'sourceUrl': self.source_url,
            'externalAuthorization': self.external_authorization.serialize() if self.external_authorization else None,
            'destination': self.destination.serialize(),
        }

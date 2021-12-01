from typing import Optional, List, Tuple, Any, BinaryIO
from requests import Response

from vectice.api._auth import Auth
from .output.attachments_output import AttachmentOutput
from .output.paged_response import PagedResponse


class AttachmentApi(Auth):
    def __init__(self, _token: Optional[str] = None, auto_connect=True):
        super().__init__(_token=_token, auto_connect=auto_connect)
        self._attachment_path = "/metadata/entityfiles/"

    @property
    def api_base_path(self) -> str:
        return self._attachment_path

    def get_attachment(self, artifact_type: str, artifact_version: int, file_id: int):
        return self._get_attachment(self._attachment_path + f"{artifact_type}/{artifact_version}/{file_id}")

    def create_attachments(
        self, artifact_type: str, artifact_version: int, files: Optional[List[Tuple[str, Tuple[Any, BinaryIO]]]] = None
    ) -> Optional[Response]:
        return self._post_attachments(self._attachment_path + f"{artifact_type}/{artifact_version}/", files)

    def update_attachment(
        self, artifact_type: str, artifact_version: int, files: Optional[List[Tuple[str, Tuple[Any, BinaryIO]]]] = None
    ) -> Optional[Response]:
        if files and len(files) == 1:
            return self._post_attachments(self._attachment_path + f"{artifact_type}/{artifact_version}/", files)
        elif files and len(files) > 1:
            for file in files:
                self._post_attachments(self._attachment_path + f"{artifact_type}/{artifact_version}/", [file])
        return None

    def delete_attachment(self, artifact_type: str, artifact_version: int, file_id: int):
        return self._delete_attachment(self._attachment_path + f"{artifact_type}/{artifact_version}/{file_id}")

    def list_attachments(self, artifact_type: str, artifact_version: int) -> PagedResponse[AttachmentOutput]:
        attachments = self._list_attachments(self._attachment_path + f"{artifact_type}/{artifact_version}/")
        return PagedResponse(
            item_cls=AttachmentOutput,
            total=len(attachments),
            page={},
            items=attachments,
        )

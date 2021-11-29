import logging
import os
from mimetypes import guess_type
from typing import Optional, List

try:
    from oauth2client.client import GoogleCredentials
    from oauth2client.service_account import ServiceAccountCredentials
    from googleapiclient.discovery import build, Resource
    from googleapiclient.http import MediaFileUpload
except ImportError as e:
    raise ImportError('Please install "google" extra packages.') from e

LOGGER = logging.getLogger(__name__)


class DriveError(Exception):
    pass


class DriveWrapper(object):

    scopes = [
        'https://www.googleapis.com/auth/drive',
    ]

    def __init__(self, client: Resource, default_folder_id: Optional[str] = None):
        if not client.__class__.__name__ == 'Resource':
            raise ValueError('"client" argument must be a Google Drive "Resource" instance')
        self.client = client
        self.default_folder_id = default_folder_id

    @classmethod
    def from_params(cls, default_folder_id: Optional[str] = None, auth_file: str = None):
        if auth_file:
            if not os.path.exists(auth_file):
                raise FileNotFoundError(f'Authentication file does not exist: {auth_file}')
            credentials = ServiceAccountCredentials.from_json_keyfile_name(auth_file, scopes=cls.scopes)
        else:
            credentials = GoogleCredentials.get_application_default().create_scoped(cls.scopes)
        client = build('drive', version='v3', credentials=credentials, cache_discovery=False)
        return cls(client, default_folder_id=default_folder_id)

    def _require_folder_id(self, folder_id: Optional[str] = None) -> str:
        folder_id = folder_id or self.default_folder_id
        if not folder_id:
            raise ValueError('You need to specify a "folder_id", either at wrapper level or function level')
        return folder_id

    def _find_all(self, filename: str, folder_id: str) -> List[dict]:
        query = f"'{folder_id}' in parents and name = '{filename}'"
        results = self.client.files().list(q=query).execute()
        return results.get('files', [])

    def file_exists(self, filename: str, folder_id: Optional[str] = None) -> bool:
        """
        Returns True if a file named like filename is already present in the folder.
        :param filename: name of the file to check the existence of
        :param folder_id: unique ID of the distant folder. If not specified, the default folder ID is used
        """
        folder_id = self._require_folder_id(folder_id)
        files = self._find_all(filename, folder_id)
        return len(files) > 0

    def find_file(self, filename: str, folder_id: Optional[str] = None) -> Optional[str]:
        """
        Find the ID of a file by its name. Raises if multiple files have the searched name.
        :param filename: (str) name of the files to search for (several files can have the same name).
        :param folder_id: (str) unique ID of the distant folder. If not specified, the default folder ID is used
        :return: id of the file when it is found, None otherwise
        """
        folder_id = self._require_folder_id(folder_id)
        file_ids = [item['id'] for item in self._find_all(filename, folder_id)]
        if len(file_ids) == 0:
            return None
        elif len(file_ids) > 1:
            raise DriveError(f'Multiple files with name "{filename}" in folder "{folder_id}": {", ".join(file_ids)}')
        else:
            return file_ids[0]

    def delete_file(self, filename: str, folder_id: Optional[str] = None) -> None:
        """
        Deletes a file with a specific name, in the specified folder or the default one. If several files have the same
        name, they will all be deleted.
        :param filename: (str) name of the file to delete
        :param folder_id: (str) unique ID of the distant folder. If not specified, the default folder ID is used
        :return: None
        """
        folder_id = self._require_folder_id(folder_id)
        files = self._find_all(filename, folder_id)
        if not files:
            LOGGER.info(f'Could not find "{filename}" in directory "{folder_id}"')
        else:
            LOGGER.info(f'Deleting {len(files)} file{"s" if len(files) > 1 else ""}...')
        for file in files:
            self.client.files().delete(fileId=file['id']).execute()

    def give_ownership(self, file_id: str, new_owner_email: str) -> None:
        """
        Gives a user ownership rights on a specific file.
        :param file_id: unique ID of the file. Can be found using "find_file" method
        :param new_owner_email: email address of the user to give ownership rights to
        :return: None
        """
        batch = self.client.new_batch_http_request()
        user_permission = {
            'type': 'user',
            'role': 'owner',
            'emailAddress': new_owner_email
        }
        client_permission = self.client.permissions().create(
            fileId=file_id,
            body=user_permission,
            fields='id'
        )
        batch.add(client_permission)
        batch.execute()
        LOGGER.info(f"Ownership of file {file_id} was given to {new_owner_email}")

    def _upload(self, filename: str, folder_id: Optional[str] = None, mimetype: Optional[str] = None) -> str:
        folder_id = self._require_folder_id(folder_id)
        file_metadata = {
            'name': filename,
            'mimeType': mimetype,
            'field': 'id',
            'parents': [folder_id]
        }
        mimetype = mimetype or guess_type(filename)[0]
        media = MediaFileUpload(filename, mimetype=mimetype, resumable=True)
        created_file = self.client.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = created_file.get('id')
        LOGGER.info(f'File "{filename}" with ID "{file_id}" successfully uploaded in folder "{folder_id}"')
        return file_id

    def upload_file(self, filename: str, folder_id: Optional[str] = None, mimetype: Optional[str] = None,
                    if_exists: str = 'fail') -> str:
        """
        Send a file from current directory to Google Drive.
        TODO: Support uploading files from other directories than working directory
        :param filename: (str) local filename to send (must be in working directory)
        :param folder_id: (str) target folder ID. If not specified, the default folder ID is used
        :param mimetype: (str) MIME type of the file to send. If None, then auto-detect is used
        :param if_exists: (str) action to take if this filename already exists. Should be in ('fail', 'replace')
        :return: file_id of the uploaded file
        """
        folder_id = self._require_folder_id(folder_id)
        if self.file_exists(filename, folder_id):
            if if_exists == 'fail':
                raise DriveError('File already exists and "if_exists" set to "fail". Upload cancelled')
            elif if_exists == 'replace':
                LOGGER.warning(f'File "{filename}" will be replaced')
                self.delete_file(filename, folder_id)
            else:
                raise NotImplementedError('"if_exists" argument must be in ("fail", "duplicate")')
        LOGGER.info(f'Adding new file "{filename}"...')
        file_id = self._upload(filename, folder_id, mimetype)
        return file_id

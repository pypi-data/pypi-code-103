import requests
from typing import Dict, List
from classy_sdk import ApiManager
from classy_sdk.utils import convert_image, join_url


class ClassySDK:
    """
    Queries Classy API endpoints.

    Args:
        source:
            A user/client name, e.g. 'dev.cz'.
        api_url (optional):
            A url to Classy API. It can be supplied
            as an argument or through environment variables.
        api_token (optional):
            An authorization token. It can be supplied
            as an argument or through environment variables.
        timeout (optional):
            A server response timeout in seconds, defaults to 30.

    Attributes:
        api:
            An instance of ApiManager to handle API setup and queries.
        source:
            A user/client name, e.g. 'dev.cz'.
        url:
            An API base url.

    Methods:
        list_cases:
            Retrieves a list of cases within an indicated time period.
        get_case:
            Retrieves one particular case.
        create_case:
            Creates a new case.
        update_case:
            Updates the case name as displayed in the Classy interface.
        upload_photo:
            Uploads a photo in base64 format to the case.
        upload_photo_from_file:
            Uploads a photo file to the case.
        list_exports:
            Retrieves a list of performed exports.
        get_export:
            Retrieves one particular export.
        get_export_csv:
            Retrieves a csv file with requested export.
        get_export_download_url:
            Retrieves a csv download url for the requested export.
        list_inspections:
            Retrieves a list of performed inspections.
    """

    def __init__(
        self,
        source: str,
        api_url: str = None,
        api_token: str = None,
        timeout: int = 30,
    ) -> None:
        self.api = ApiManager(api_url, api_token, timeout)
        self.source = source
        self.url = self.api.api_url
        self._cases_url = "/cases"
        self._exports_url = "/exports"
        self._inspections_url = "/inspections"

    def list_cases(self, from_time: str, to_time: str) -> list:
        """Retrieves a list of cases within an indicated time period.

        Args:
            from_time:
                Start time, e.g. '2021-09-01T13:00:00.000Z'.
            to_time:
                End time, e.g. '2021-09-01T15:00:00.000Z'.

        Returns:
            A list of cases.
        """
        url = join_url(self.url, self._cases_url)
        params = {"from": from_time, "to": to_time, "source": self.source}
        return self.api.query("GET", url, params=params).json()

    def get_case(self, case_id: str) -> dict:
        """Retrieves one particular case.

        Atrs:
            case_id:
                A Searpent case id.

        Returns:
            Metadata related to the case.
        """
        url = join_url(self.url, self._cases_url, case_id)
        response = self.api.query("GET", url)
        return response.json()

    def create_case(self, name: str) -> str:
        """Creates a new case.

        The user provides their own case name, based on which Classy
        assigns and sends back a new internal id (case_id).

        name:
            An arbitrary case name as defined by the user.

        Returns:
            A new Searpent case id.
        """
        url = join_url(self.url, self._cases_url)
        data = {"name": name, "source": self.source}
        response = self.api.query("POST", url, data)
        return response.json()

    def update_case(self, case_id: str, name: str) -> requests.Response:
        """Updates the case name as displayed in the Classy interface.

        Args:
            case_id:
                A Searpent case id.
            name:
                A new case name.

        Returns:
            The response object can be used to verify the status code
            (response.status_code) which should equal to 200.
        """
        url = join_url(self.url, self._cases_url, case_id)
        data = {"name": name}
        return self.api.query("PATCH", url, data)

    def upload_photo(
        self, case_id: str, base64_photo: bytes, filename: str, photo_id: str
    ) -> str:
        """Uploads a photo in base64 format to the case.

        Args:
            case_id:
                A Searpent case id.
            base64_photo:
                A photo represented as base64.
            filename:
                A photo filename.
            photo_id:
                An arbitrary photo name as defined by the user.

        Returns:
            A photo id assigned by the API.
        """
        url = join_url(self.url, self._cases_url, case_id, "/upload")
        data = {
            "photo": base64_photo.decode(),
            "photo_id": photo_id,
            "filename": filename,
            "source": self.source,
        }
        response = self.api.query("PATCH", url, data)
        return response.json()

    def upload_photo_from_file(
        self, case_id: str, file_path: str, filename: str, photo_id: str
    ) -> str:
        """Uploads a photo file to the case.

        Args:
            case_id:
                A Searpent case id.
            file_path:
                A file path.
            filename:
                A photo filename.
            photo_id:
                An arbitrary photo name as defined by the user.

        Returns:
            A photo id assigned by the API.
        """
        url = join_url(self.url, self._cases_url, case_id, "/upload")
        data = {
            "photo": convert_image(file_path),
            "photo_id": photo_id,
            "filename": filename,
            "source": self.source,
        }
        response = self.api.query("PATCH", url, data)
        return response.json()

    def list_exports(
        self, exp_type: str, from_time: str = None, to_time: str = None
    ) -> list:
        """Retrieves a list of performed exports.

        There are two types of exports to pick from: 'regular' or 'custom'.

        Args:
            exp_type:
                The export type with 'regular' or 'custom' value.
            from_time (optional):
                Start time, e.g. '2021-09-01T13:00:00.000Z'.
            to_time (optional):
                End time, e.g. '2021-09-01T15:00:00.000Z'.

        Returns:
            A list of exports performed by the user.
        """
        url = join_url(self.url, self._exports_url)
        from_time = None if from_time is None else from_time
        to_time = None if to_time is None else to_time
        params = {
            "from": from_time,
            "to": to_time,
            "source": self.source,
            "type": exp_type,
        }
        return self.api.query("GET", url, params=params).json()

    def get_export(self, exp_id: str) -> dict:
        """Retrieves one particular export.

        Args:
            exp_id:
                The export id.

        Returns:
            Metadata related to the export.
        """
        url = join_url(self.url, self._exports_url, exp_id)
        response = self.api.query("GET", url)
        return response.json()

    def get_export_csv(self, exp_id: str, file_path: str = None) -> None:
        """Retrieves a csv file with requested export.

        Args:
            exp_id:
                The export id.
            file_path (optional):
                A file path to store the result.
        """
        response = self.api.query(
            "GET", join_url(self.url, self._exports_url, exp_id, "/download")
        )
        default_name = f"searpent-classy-{self.source}-{exp_id}.csv"
        path = default_name if file_path is None else file_path

        with open(path, "w", encoding="utf-8") as file:
            file.write(response.text)

    def get_export_download_url(self, exp_id: str) -> str:
        """Retrieves a csv download url for the requested export.

        Args:
            exp_id:
                The export id.

        Returns:
            A csv download url.
        """
        url = join_url(self.url, self._exports_url, exp_id)
        response = self.api.query("GET", url)
        content = response.json()
        return content.get("url")

    def list_inspections(
        self, from_time: str = None, to_time: str = None
    ) -> list:
        """Retrieves a list of performed inspections.

        Args:
            from_time (optional):
                Start time, e.g. '2021-09-01T15:00:00.000Z'.
            to_time (optional):
                End time, e.g. '2021-09-01T15:00:00.000Z'.

        Returns:
            A list of inspections performed by the user.
        """
        url = join_url(self.url, self._inspections_url)
        from_time = None if from_time is None else from_time
        to_time = None if to_time is None else to_time
        params = {"from": from_time, "to": to_time, "source": self.source}
        return self.api.query("GET", url, params=params).json()

    def create_inspection(
        self,
        name: str,
        phone: str,
        required_fields: List[Dict[str, str]] = None,
        message: str = None,
    ) -> str:
        """Creates a new inspection.

        Args:
            name:
                An insuser inspection name.
            phone:
                A phone number of the recipient.
            required_fields (optional):
                One or multiple fields specific to the insurer in a form
                of a list of dictionaries. It has to contain the
                "fieldId" and "requiredText" keys as presented below:
                [
                    {
                    "fieldId": "policy number",
                    "requiredText": "c-0001"
                    },
                    {
                    "fieldId": "surname",
                    "requiredText": "doe"
                    }
                ]
            message (optional):
                An invitation message sent to the recipient, it has
                to include the '%s' string that will be replaced
                with an inspection url, e.g. "Please click on %s
                to start inspection".

        Returns:
            An inspection.
        """
        url = join_url(self.url, self._inspections_url)
        data = {"name": name, "phone": phone, "source": self.source}
        if required_fields is not None:
            data.update({"requiredFields": required_fields})
        if message is not None:
            data.update({"invitationMessage": message})
        response = self.api.query("POST", url, data)
        return response.json()

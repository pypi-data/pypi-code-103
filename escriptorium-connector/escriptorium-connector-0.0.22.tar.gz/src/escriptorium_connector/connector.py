# TODO: I am in the middle of a big refactor.
# The goal is to have a Python class in the ./models
# folder that can be used for input/output for all of
# the functions in the connector instead of using bespoke
# objects as we do now, which give no help to users, who
# need to know exactly waht data to submit and who would like
# to know what sort of data will be returned.

# TODO: We should add a full testing suite for the connector.
# See ../../tests/test_documents.py


# region General Imports
from io import BytesIO
from typing import Any, Union, List, Dict, Type, TypeVar
from lxml import html
import requests
from requests.packages.urllib3.util import Retry
import logging
import websocket
import dataclasses
import json

# endregion

# region LocalImports
from .dtos import (
    GetDocument,
    GetDocuments,
    PostDocument,
    PutDocument,
    GetAnnotationTaxonomy,
    GetAnnotationTaxonomies,
    PostAnnotationTaxonomy,
    PagenatedResponse,
    GetUser,
)

# endregion

# region HTTP Adapter

# Default timeouts for http requests
# See https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/
from requests.adapters import HTTPAdapter


DEFAULT_HTTP_TIMEOUT = 5  # seconds


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_HTTP_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


# endregion

logger = logging.getLogger(__name__)

# Typing info
P = TypeVar("P", bound=PagenatedResponse)

# JSON dataclass support (See: https://stackoverflow.com/questions/51286748/make-the-python-json-encoder-support-pythons-new-dataclasses)
class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


class EscriptoriumConnector:
    # region Init
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        api_url: str = None,
        project: str = None,
    ):
        """Simplified access to eScriptorium

        The eScriptorium connector is a class that enables convenient access to
        an online instance of the eScriptorium platform's HTTP API. After creating an
        EscriptoriumConnector object, the object can be used to interact with the API
        by means of the various functions it provides.

        Args:
            base_url (str): The base url of the eScriptorium server you wish to connect to (trailing / is optional)
            username (str): The username used to logon to the eScriptorium website
            password (str): The password used to logon to the eScriptorium website
            api_url (str, optional): The url path to the api (trailing / is optional). Defaults to {base_url}api/
            project (str, optional): The name of the eScriptorium project to use by default. Defaults to None.

        Raises:
            EscriptoriumConnectorHttpError: A description of the error returned from the eScriptorium HTTP API

        Examples:
            Creating the connector and performing operations:

            >>> from escriptorium_connector import EscriptoriumConnector
            >>> from escriptorium_connector.dtos import (
            ...     PostDocument,
            ...     ReadDirection,
            ...     LineOffset,
            ... )

            >>> url = "https://www.escriptorium.fr"
            >>> username = "my_username"
            >>> password = "my_password"
            >>>
            >>> connector = EscriptoriumConnector(url, username, password)
            >>> new_project_name = "test_project"
            >>> user_data = connector.get_user()
            >>> user_id = user_data.count
            >>> new_project = connector.create_project({"name": new_project_name, "slug": new_project_name, "owner": user_id})
            >>> new_document = PostDocument(
            ...     "test-doc", project_name, "Latin", ReadDirection.LTR, LineOffset.BASELINE, []
            ... )
            >>> my_doc = connector.create_document(new_document)
        """

        # Setup retries and timeouts for HTTP requests
        retry_strategy = Retry(
            total=5,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=[  # Used method_whitelist instead of methods_available for backwards compatability
                "HEAD",
                "GET",
                "POST",
                "PUT",
                "DELETE",
                "OPTIONS",
                "TRACE",
            ],
            backoff_factor=1,
        )
        adapter = TimeoutHTTPAdapter(max_retries=retry_strategy)

        def assert_status_hook(response, *args, **kwargs):
            try:
                response.raise_for_status()
            except requests.HTTPError as err:
                EscriptoriumConnectorHttpError(err.response.text, err)

        self.http = requests.Session()
        self.http.hooks["response"] = [assert_status_hook]
        self.http.mount("https://", adapter)
        self.http.mount("http://", adapter)

        # Make sure the urls terminates with a front slash
        self.base_url = base_url if base_url[-1] == "/" else base_url + "/"
        self.api_url = (
            f"""{self.base_url}api/"""
            if api_url is None
            else api_url
            if api_url[-1] == "/"
            else f"""{api_url}/"""
        )

        self.http.headers.update({"Accept": "application/json"})

        login_url = f"""{self.base_url}login/"""
        result = self.http.get(login_url)
        tree = html.fromstring(result.text)
        self.csrfmiddlewaretoken = list(
            set(tree.xpath("//input[@name='csrfmiddlewaretoken']/@value"))
        )[0]
        payload = {
            "username": username,
            "password": password,
            "csrfmiddlewaretoken": self.csrfmiddlewaretoken,
        }
        result = self.http.post(
            login_url, data=payload, headers={**self.http.headers, "referer": login_url}
        )
        self.cookie = "; ".join(
            [f"""{k}={v}""" for k, v in self.http.cookies.get_dict().items()]
        )
        result = self.http.get(self.base_url + "profile/apikey/")
        tree = html.fromstring(result.text)
        api_key = list(set(tree.xpath("//button[@id='api-key-clipboard']/@data-key")))[
            0
        ]
        self.http.headers.update({"Authorization": f"""Token {api_key}"""})

        self.project_name = project
        self.project = self.get_project_pk_by_name(self.project_name)

    # endregion

    # region Websockets (not used)
    def __on_message(self, ws, message):
        logging.debug(message)

    def __on_error(self, ws, error):
        logging.debug(error)

    def __on_close(self, ws, close_status_code, close_msg):
        logging.debug("### websocket closed ###")
        logging.debug(close_status_code)
        logging.debug(close_msg)

    def __on_open(self, ws):
        logging.debug("### websocket opened ###")

    # endregion

    # region HTTP calls
    def __get_url(self, url: str) -> requests.Response:
        return self.http.get(url)

    def __post_url(
        self, url: str, payload: dict, files: object = None
    ) -> requests.Response:
        prepared_payload = json.loads(json.dumps(payload, cls=EnhancedJSONEncoder))
        return (
            self.http.post(url, data=prepared_payload, files=files)
            if files is not None
            else self.http.post(url, json=prepared_payload)
        )

    def __put_url(
        self, url: str, payload: dict, files: object = None
    ) -> requests.Response:
        prepared_payload = json.loads(json.dumps(payload, cls=EnhancedJSONEncoder))
        return (
            self.http.put(url, data=prepared_payload, files=files)
            if files is not None
            else self.http.put(url, json=prepared_payload)
        )

    def __delete_url(self, url: str) -> requests.Response:
        return self.http.delete(url)

    def __get_paginated_response(self, url: str, cls: Type[P]) -> P:
        r = self.__get_url(url)
        all_docs = cls(**json.loads(r.text))
        info = all_docs
        while info.next is not None:
            r = self.__get_url(info.next)
            info = cls(**json.loads(r.text))
            all_docs.results = all_docs.results + info.results

        return all_docs

    # endregion

    # region Project API
    def set_connector_project_by_name(self, project_name: str):
        self.project_name = project_name
        self.project = self.get_project_pk_by_name(self.project_name)

    def set_connector_project_by_pk(self, project_pk: int):
        self.project = project_pk
        self.project_name = self.get_project(self.project)["name"]

    def get_projects(self):
        r = self.__get_url(f"{self.api_url}projects/")
        info = r.json()
        documents = info["results"]
        while info["next"] is not None:
            r = self.__get_url(info["next"])
            info = r.json()
            documents = documents + info["results"]

        return documents

    def get_project(self, pk: int):
        r = self.__get_url(f"{self.api_url}projects/{pk}")
        return r.json()

    def get_project_pk_by_name(
        self, project_name: Union[str, None]
    ) -> Union[int, None]:
        if project_name is None or project_name == "":
            return None

        all_projects = self.get_projects()
        matching_projects = [x for x in all_projects if x["name"] == project_name]
        return matching_projects[0]["id"] if matching_projects else None

    def create_project(self, project_data: object):
        return self.__post_url(f"{self.api_url}projects/", project_data)

    def update_project(self, project_data: object):
        return self.__put_url(f"{self.api_url}projects/", project_data)

    def delete_project(self, project_pk: int):
        return self.__delete_url(f"{self.api_url}projects/{project_pk}")

    def verify_project_exists(self, project_pk):
        try:
            self.get_project(project_pk)
            return True
        except:
            return False

    # endregion

    # region Document API
    def get_documents(self) -> GetDocuments:
        return self.__get_paginated_response(f"{self.api_url}documents/", GetDocuments)

    def get_document(self, pk: int) -> GetDocument:
        r = self.__get_url(f"{self.api_url}documents/{pk}/")
        return GetDocument(**r.json())

    def create_document(self, doc_data: PostDocument) -> GetDocument:
        r = self.__post_url(f"{self.api_url}documents/", doc_data.__dict__)
        r_json = r.json()
        return GetDocument(**r_json)

    def update_document(self, doc_data: PutDocument) -> GetDocument:
        r = self.__put_url(f"{self.api_url}documents/", doc_data.__dict__)
        r_json = r.json()
        return GetDocument(**r_json)

    def delete_document(self, pk: int):
        return self.__delete_url(f"{self.api_url}documents/{pk}")

    # endregion

    # region Part API
    def get_document_parts(self, doc_pk: int):
        return self.get_document_images(doc_pk)

    def get_document_part(self, doc_pk: int, part_pk: int):
        r = self.__get_url(f"{self.api_url}documents/{doc_pk}/parts/{part_pk}/")
        return r.json()

    def delete_document_parts(self, document_pk: int, start: int, end: int):
        parts = self.get_document_images(document_pk)
        for part in parts[start:end]:
            r = self.__delete_url(
                f'{self.api_url}documents/{document_pk}/parts/{part["pk"]}/'
            )

    # endregion

    # region Up/Download API

    # region Text Up/Download
    def download_part_alto_transcription(
        self,
        document_pk: int,
        part_pk: Union[List[int], int],
        transcription_pk: int,
    ) -> Union[bytes, None]:
        """Download one or more ALTO/XML files from the document.

        Args:
            document_pk (int): Desired document
            part_pk (Union[List[int], int]): Desired document part or parts
            transcription_pk (int): The desired transcription

        Returns:
            Union[bytes, None]: The response is None if the XML could not be downloaded.
            Otherwise it is a bytes object with the contents of the downloaded zip file.
            You will need to unzip these bytes in order to access the XML data (zipfile can do this).
        """

        return self.__download_part_output_transcription(
            document_pk, part_pk, transcription_pk, "alto"
        )

    def download_part_pagexml_transcription(
        self,
        document_pk: int,
        part_pk: Union[List[int], int],
        transcription_pk: int,
    ) -> Union[bytes, None]:
        """Download one or more PageXML files from the document.

        Args:
            document_pk (int): Desired document
            part_pk (Union[List[int], int]): Desired document part or parts
            transcription_pk (int): The desired transcription

        Returns:
            Union[bytes, None]: The response is None if the XML could not be downloaded.
            Otherwise it is a bytes object with the contents of the downloaded zip file.
            You will need to unzip these bytes in order to access the XML data (zipfile can do this).
        """

        return self.__download_part_output_transcription(
            document_pk, part_pk, transcription_pk, "pagexml"
        )

    def download_part_text_transcription(
        self,
        document_pk: int,
        part_pk: Union[List[int], int],
        transcription_pk: int,
    ) -> Union[bytes, None]:
        """Download one or more TXT files from the document.

        Args:
            document_pk (int): Desired document
            part_pk (Union[List[int], int]): Desired document part or parts
            transcription_pk (int): The desired transcription

        Returns:
            Union[bytes, None]: The response is None if the XML could not be downloaded.
            Otherwise it is a bytes object with the contents of the downloaded zip file.
            You will need to unzip these bytes in order to access the XML data (zipfile can do this).
        """

        return self.__download_part_output_transcription(
            document_pk, part_pk, transcription_pk, "text"
        )

    def __download_part_output_transcription(
        self,
        document_pk: int,
        part_pk: Union[List[int], int],
        transcription_pk: int,
        output_type: str,
    ) -> Union[bytes, None]:
        if self.cookie is None:
            raise Exception("Must use websockets to download ALTO exports")

        download_link = None
        ws = websocket.WebSocket()
        ws.connect(
            f"{self.base_url.replace('http', 'ws')}ws/notif/", cookie=self.cookie
        )
        self.__post_url(
            f"{self.api_url}documents/{document_pk}/export/",
            {
                "task": "export",
                "csrfmiddlewaretoken": self.csrfmiddlewaretoken,
                "transcription": transcription_pk,
                "file_format": output_type,
                "region_types": [
                    x["pk"] for x in self.get_document_region_types(document_pk)
                ],
                "document": document_pk,
                "parts": part_pk,
            },
        )

        message = ws.recv()
        ws.close()
        logging.debug(message)
        msg = json.loads(message)
        if "export" in msg["text"].lower():
            for entry in msg["links"]:
                if entry["text"].lower() == "download":
                    download_link = entry["src"]

        if download_link is None:
            logging.warning(
                f"Did not receive a link to download ALTO export for {document_pk}, {part_pk}, {transcription_pk}"
            )
            return None
        alto_request = self.__get_url(f"{self.base_url}{download_link}")

        if alto_request.status_code != 200:
            return None

        return alto_request.content

    def upload_part_transcription(
        self,
        document_pk: int,
        transcription_name: str,
        filename: str,
        file_data: BytesIO,
        override: str = "off",
    ):
        """Upload a txt, PageXML, or ALTO file.

        Args:
            document_pk (int): Document PK
            transcription_name (str): Transcription name
            filename (str): Filename
            file_data (BytesIO): File data as a BytesIO
            override (str): Whether to override existing segmentation data ("on") or not ("off", default)

        Returns:
            null: Nothing
        """

        request_payload = {"task": "import-xml", "name": transcription_name}
        if override == "on":
            request_payload["override"] = "on"

        return self.__post_url(
            f"{self.api_url}documents/{document_pk}/imports/",
            request_payload,
            {"upload_file": (filename, file_data)},
        )

    # endregion

    # region Image Up/Download

    def get_document_images(self, document_pk: int):
        r = self.__get_url(f"{self.api_url}documents/{document_pk}/parts/")
        image_info = r.json()
        image_names = image_info["results"]
        while image_info["next"] is not None:
            r = self.__get_url(image_info["next"])
            image_info = r.json()
            image_names = image_names + image_info["results"]

        return image_names

    def get_image(self, img_url: str):
        r = self.__get_url(f"{self.base_url}{img_url}")
        return r.content

    def create_image(
        self, document_pk: int, image_data_info: object, image_data: bytes
    ):
        return self.__post_url(
            f"{self.api_url}documents/{document_pk}/parts/",
            image_data_info,
            {"image": (image_data_info["filename"], image_data)},
        )

    # endregion

    # endregion

    # region Line API

    def get_document_part_line(self, doc_pk: int, part_pk: int, line_pk: int):
        r = self.__get_url(
            f"{self.api_url}documents/{doc_pk}/parts/{part_pk}/lines/{line_pk}/"
        )
        return r.json()

    def get_document_part_lines(self, doc_pk: int, part_pk: int):
        r = self.__get_url(f"{self.api_url}documents/{doc_pk}/parts/{part_pk}/lines/")
        line_info = r.json()
        lines = line_info["results"]
        while line_info["next"] is not None:
            r = self.__get_url(line_info["next"])
            line_info = r.json()
            lines = lines + line_info["results"]

        return lines

    def create_document_part_line(self, doc_pk: int, part_pk: int, new_line: object):
        r = self.__post_url(
            f"{self.api_url}documents/{doc_pk}/parts/{part_pk}/lines/", new_line
        )
        return r

    def delete_document_part_line(self, doc_pk: int, part_pk: int, line_pk: int):
        r = self.__delete_url(
            f"{self.api_url}documents/{doc_pk}/parts/{part_pk}/lines/{line_pk}"
        )
        return r

    # endregion

    # region Line Type API

    def get_line_types(self):
        r = self.__get_url(f"{self.api_url}types/line/")
        line_type_info = r.json()
        line_types = line_type_info["results"]
        while line_type_info["next"] is not None:
            r = self.__get_url(line_type_info["next"])
            line_type_info = r.json()
            line_types = line_types + line_type_info["results"]

        return line_types

    def create_line_type(self, line_type: object):
        r = self.__post_url(f"{self.api_url}types/line/", line_type)
        return r

    # endregion

    # region Region API

    def get_document_part_region(self, doc_pk: int, part_pk: int, region_pk: int):
        regions = self.get_document_part_regions(doc_pk, part_pk)
        region = [x for x in regions if x["pk"] == region_pk]
        return region[0] if region else None

    def get_document_part_regions(self, doc_pk: int, part_pk: int):
        r = self.__get_url(f"{self.api_url}documents/{doc_pk}/parts/{part_pk}")
        part = r.json()
        return part["regions"]

    def create_document_part_region(self, doc_pk: int, part_pk: int, region: object):
        if not isinstance(region["box"], str):
            region["box"] = json.dumps(region["box"])

        r = self.__post_url(
            f"{self.api_url}documents/{doc_pk}/parts/{part_pk}/blocks/",
            region,
        )
        return r

    # endregion

    # region Region Type API

    def get_region_types(self):
        r = self.__get_url(f"{self.api_url}types/block/")
        block_type_info = r.json()
        block_types = block_type_info["results"]
        while block_type_info["next"] is not None:
            r = self.__get_url(block_type_info["next"])
            block_type_info = r.json()
            block_types = block_types + block_type_info["results"]

        return block_types

    def get_document_region_types(self, document_pk: int) -> List[Dict[str, int]]:
        doc_data = self.get_document(document_pk)
        return [x for x in doc_data["valid_block_types"]]

    def create_region_type(self, region_type: object):
        r = self.__post_url(f"{self.api_url}types/block/", region_type)
        return r

    # endregion

    # region Transcription API
    def get_document_part_line_transcription(
        self, doc_pk: int, part_pk: int, line_pk: int, line_transcription_pk: int
    ):
        transcriptions = self.get_document_part_line_transcriptions(
            doc_pk, part_pk, line_pk
        )
        transcription = [x for x in transcriptions if x["pk"] == line_transcription_pk]
        return transcription[0] if transcription else None

    def get_document_part_line_transcription_by_transcription(
        self, doc_pk: int, part_pk: int, line_pk: int, transcription_pk: int
    ):
        transcriptions = self.get_document_part_line_transcriptions(
            doc_pk, part_pk, line_pk
        )
        transcription = [
            x for x in transcriptions if x["transcription"] == transcription_pk
        ]
        return transcription[0] if transcription else None

    def get_document_part_line_transcriptions(
        self, doc_pk: int, part_pk: int, line_pk: int
    ):
        line = self.get_document_part_line(doc_pk, part_pk, line_pk)
        return line["transcriptions"]

    def get_document_transcription(self, doc_pk: int, transcription_pk: int):
        r = self.__get_url(
            f"{self.api_url}documents/{doc_pk}/transcriptions/{transcription_pk}/"
        )
        return r.json()

    def create_document_transcription(self, doc_pk: int, transcription_name: str):
        r = self.__post_url(
            f"{self.api_url}documents/{doc_pk}/transcriptions/",
            {"name": transcription_name},
        )
        return r.json()

    def delete_document_transcription(self, doc_pk: int, transcription_pk: int):
        r = self.__delete_url(
            f"{self.api_url}documents/{doc_pk}/transcriptions/{transcription_pk}/"
        )
        return r.json()

    def get_document_transcriptions(self, doc_pk: int):
        r = self.__get_url(f"{self.api_url}documents/{doc_pk}/transcriptions/")
        return r.json()

    def create_document_line_transcription(
        self,
        doc_pk: int,
        parts_pk: int,
        line_pk: int,
        transcription_pk: int,
        transcription_content: str,
        graphs: Union[Any, None],
    ):
        payload = {
            "line": line_pk,
            "transcription": transcription_pk,
            "content": transcription_content,
        }
        if graphs is not None:
            payload["graphs"] = graphs
        r = self.__post_url(
            f"{self.api_url}documents/{doc_pk}/parts/{parts_pk}/transcriptions/",
            payload,
        )
        return r.json()

    def get_document_part_transcriptions(self, doc_pk: int, part_pk: int):
        get_url = f"{self.api_url}documents/{doc_pk}/parts/{part_pk}/transcriptions/"
        r = self.__get_url(get_url)
        transcriptions_info = r.json()
        transcriptions = transcriptions_info["results"]
        while transcriptions_info["next"] is not None:
            r = self.__get_url(transcriptions_info["next"])
            transcriptions_info = r.json()
            transcriptions = transcriptions + transcriptions_info["results"]
        return transcriptions

    def create_document_part_transcription(
        self, doc_pk: int, part_pk: int, transcription: object
    ):
        r = self.__post_url(
            f"{self.api_url}documents/{doc_pk}/parts/{part_pk}/transcriptions/",
            transcription,
        )
        return r

    # endregion

    # region Annotation API
    def get_document_annotations(self, doc_pk: int) -> GetAnnotationTaxonomies:
        return self.__get_paginated_response(
            f"""{self.api_url}documents/{doc_pk}/taxonomies/annotations/""",
            GetAnnotationTaxonomies,
        )

    def get_document_annotation(
        self, doc_pk: int, annotation_pk
    ) -> GetAnnotationTaxonomy:
        r = self.__get_url(
            f"""{self.api_url}documents/{doc_pk}/taxonomies/annotations/{annotation_pk}""",
        )
        r_json = r.json()
        return GetAnnotationTaxonomy(**r_json)

    def create_document_annotation(
        self, doc_pk: int, annotation: PostAnnotationTaxonomy
    ) -> GetAnnotationTaxonomy:
        r = self.__post_url(
            f"{self.api_url}documents/{doc_pk}/taxonomies/annotations/",
            annotation.__dict__,
        )
        r_json = r.json()
        print(r_json)
        return GetAnnotationTaxonomy(**r_json)

    def update_document_annotation(
        self, doc_pk: int, annotation_pk, annotation: PostAnnotationTaxonomy
    ) -> GetAnnotationTaxonomy:
        r = self.__put_url(
            f"{self.api_url}documents/{doc_pk}/taxonomies/annotations/{annotation_pk}",
            annotation.__dict__,
        )
        r_json = r.json()
        return GetAnnotationTaxonomy(**r_json)

    def delete_document_annotation(self, doc_pk: int, annotation_pk):
        self.__delete_url(
            f"{self.api_url}documents/{doc_pk}/taxonomies/annotations/{annotation_pk}"
        )

    # endregion

    # region User API
    def get_user(self) -> GetUser:
        return self.__get_paginated_response(f"""{self.api_url}user""", GetUser)

    # endregion


# region Package Errors
class EscriptoriumConnectorHttpError(BaseException):
    def __init__(self, error_message: str, http_error: requests.HTTPError):
        self.django_error = error_message
        self.error = http_error

    def __str__(self):
        return self.django_error

    def __repr__(self):
        nl = "\n"
        return f"""{self.django_error}{nl}{repr(self.error)}"""


# endregion

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    source_url = str(os.getenv("ESCRIPTORIUM_URL"))
    source_api = f"{source_url}api/"
    username = str(os.getenv("ESCRIPTORIUM_USERNAME"))
    password = str(os.getenv("ESCRIPTORIUM_PASSWORD"))
    project = str(os.getenv("ESCRIPTORIUM_PROJECT"))
    source = EscriptoriumConnector(source_url, source_api, username, password, project)
    print(source.get_documents())

from . import *
from dnastack import constants
from pandas import DataFrame
from getpass import getpass
from typing import Any, Optional, Union, List
import json

from .base_client import BaseServiceClient, ServiceType
from .utils import get_audience_from_url, get_audience_for_wallet


class PublisherClient:
    def __init__(
        self,
        email: str = None,
        personal_access_token: str = None,
        dataconnect_url: str = None,
        collections_url: str = None,
        wes_url: str = None,
        auth_params: dict = default_auth,
    ):

        self.dataconnect = self.dataconnect(self, dataconnect_url, auth_params)
        self.collections = self.collections(self, collections_url, auth_params)
        self.wes = self.wes(self, wes_url, auth_params)
        self.auth = self.auth(personal_access_token, email, self)

    def get_services(self) -> List[BaseServiceClient]:
        return [self.dataconnect, self.collections, self.wes]

    def get_service(self, service_type: Union[str, ServiceType]) -> BaseServiceClient:
        if type(service_type) == str:
            service_type = ServiceType.from_string(service_type)

        if service_type == ServiceType.DATACONNECT:
            return self.dataconnect
        elif service_type == ServiceType.COLLECTIONS:
            return self.collections
        elif service_type == ServiceType.WES:
            return self.wes
        else:
            raise Exception(f"Could not find service of service type [{service_type}]")

    class dataconnect(BaseServiceClient):
        def __init__(self, parent, service_url: str, auth_params: dict = default_auth):
            super().__init__(
                parent,
                service_url=service_url,
                service_type=ServiceType.DATACONNECT,
                auth_params=auth_params,
            )

        def query(self, q: str, download: bool = False):
            return json.loads(
                dataconnect_client.query(
                    self.service_url,
                    q,
                    download,
                    oauth_token=self.get_client_oauth_token(),
                )
            )

        def list_tables(self):
            return json.loads(
                dataconnect_client.list_tables(
                    dataconnect_url=self.service_url,
                    oauth_token=self.get_client_oauth_token(),
                )
            )

        def get_table(self, table_name: str):
            return json.loads(
                dataconnect_client.get_table(
                    dataconnect_url=self.service_url,
                    table_name=table_name,
                    oauth_token=self.get_client_oauth_token(),
                )
            )

    class collections(BaseServiceClient):
        def __init__(self, parent, service_url: str, auth_params: dict = default_auth):
            super().__init__(
                parent,
                service_url=service_url,
                service_type=ServiceType.COLLECTIONS,
                auth_params=auth_params,
            )

        def list(self):
            return collections_client.list_collections(collections_url=self.service_url)

        def list_tables(self, collection_name: str):
            return collections_client.list_tables(
                collections_url=self.service_url, collection_name=collection_name
            )

        def query(self, collection_name: str, query: str):
            return json.loads(
                collections_client.query(
                    collections_url=self.service_url,
                    collection_name=collection_name,
                    query=query,
                )
            )

    class wes(BaseServiceClient):
        def __init__(self, parent, service_url: str, auth_params: dict = default_auth):
            super().__init__(
                parent,
                service_url=service_url,
                service_type=ServiceType.WES,
                auth_params=auth_params,
            )

        def info(self):
            return get_service_info(
                wes_url=self.service_url,
                oauth_token=self.get_client_oauth_token(),
                auth_params=self.auth_params,
            )

        def execute(
            self,
            workflow_url,
            attachment_files: Any = None,
            input_params_file: Any = None,
            engine_param: Any = None,
            engine_params_file: Any = None,
            tag: Any = None,
            tags_file: Any = None,
        ):
            return submit_workflow(
                wes_url=self.service_url,
                workflow_url=workflow_url,
                oauth_token=self.get_client_oauth_token(),
                auth_params=self.auth_params,
                attachment_files=attachment_files,
                input_params_file=input_params_file,
                engine_param=engine_param,
                engine_params_file=engine_params_file,
                tag=tag,
                tags_file=tags_file,
            )

        def list(self):
            return get_list_of_workflows_executed(
                wes_url=self.service_url,
                oauth_token=self.get_client_oauth_token(),
                auth_params=self.auth_params,
            )

        def get(self, run_id: str, status_only: bool = False):
            return get_run_details(
                wes_url=self.service_url,
                run_id=run_id,
                oauth_token=self.get_client_oauth_token(),
                auth_params=self.auth_params,
                status_only=status_only,
            )

        def cancel(self, run_id: str):
            return cancel_run(
                wes_url=self.service_url,
                run_id=run_id,
                oauth_token=self.get_client_oauth_token(),
                auth_params=self.auth_params,
            )

        def run_logs(
            self,
            run_id: str,
            stderr: bool = False,
            stdout: bool = False,
            url: Any = None,
            task: Any = None,
            index: int = 0,
        ):
            return get_run_logs(
                wes_url=self.service_url,
                run_id=run_id,
                oauth_token=self.get_client_oauth_token(),
                auth_params=self.auth_params,
                stderr=stderr,
                stdout=stdout,
                url=url,
                task=task,
                index=index,
            )

    class auth:
        def __init__(
            self,
            personal_access_token=None,
            email=None,
            parent=None,
        ):
            self.oauth = {}
            self.personal_access_token = personal_access_token
            self.email = email
            self.parent = parent

        def login_for_drs(self, drs_server: str, auth_params: dict = default_auth):
            wallet_url = auth_params["url"]
            audience = [get_audience_from_url(drs_server)]

            self.oauth[wallet_url] = login_with_personal_access_token(
                audience=audience,
                email=self.email,
                personal_access_token=self.personal_access_token,
                auth_params=auth_params,
            )

        def login_for_service(self, service: Union[str, ServiceType]):

            primary_service = self.parent.get_service(service)
            wallet_url = primary_service.get_wallet_url()

            audience = [
                get_audience_from_url(serv.service_url)
                for serv in self.parent.get_services()
                if serv.service_url and serv.get_wallet_url() == wallet_url
            ]

            self.oauth[wallet_url] = login_with_personal_access_token(
                audience=audience,
                email=self.email,
                personal_access_token=self.personal_access_token,
                auth_params=primary_service.auth_params,
            )

        def set_refresh_token_for_service(
            self, service_type: Union[str, ServiceType], token: str
        ):
            service = self.parent.get_service(service_type)
            service.set_refresh_token(token)

        def refresh_token_for_service(self, service_type: Union[str, ServiceType]):
            service = self.parent.get_service(service_type)
            if (
                not service.get_client_oauth_token()
                or "refresh_token" not in service.get_client_oauth_token().keys()
            ):
                raise Exception("There is no refresh token configured.")

            self.oauth[service.get_wallet_url()] = login_refresh_token(
                token=service.get_client_oauth_token(), auth_params=service.auth_params
            )

    def load(
        self, urls, output_dir=downloads_directory, auth_params: dict = default_auth
    ):
        download_content = []
        download_files(
            urls=urls,
            output_dir=output_dir,
            oauth_token=self.auth.oauth.get(auth_params["url"]),
            quiet=True,
            out=download_content,
        )
        return download_content

    def download(
        self, urls, output_dir=downloads_directory, auth_params: dict = default_auth
    ):
        return download_files(
            urls=urls,
            output_dir=output_dir,
            oauth_token=self.auth.oauth.get(auth_params["url"]),
            quiet=True,
        )

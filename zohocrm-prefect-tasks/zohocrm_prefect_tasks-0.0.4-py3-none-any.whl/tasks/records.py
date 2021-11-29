from zcrmsdk.src.com.zoho.crm.api.record import *
from zcrmsdk.src.com.zoho.crm.api import HeaderMap, ParameterMap

from prefect import Task
from prefect.utilities.tasks import defaults_from_attrs
from typing import Any

from ..client import ApiClient


class Create(Task):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    @defaults_from_attrs()
    def run(self, log_path: str = "ZOHO_LOG_PATH", store_path: str = "ZOHO_STORE_PATH",
            resource_path: str = "ZOHO_RESOURCE_PATH", email: str = "ZOHO_USER_ID", env: str = "ZOHO_DATA_CENTER",
            client_id: str = "ZOHO_CLIENT_ID", client_secret: str = "ZOHO_CLIENT_SECRET",
            refresh_token: str = "ZOHO_REFRESH_TOKEN", module_name: str = None, body: dict = None):
        if log_path is None:
            raise ValueError("A log path must be provided.")

        if store_path is None:
            raise ValueError("A store path must be provided.")

        if resource_path is None:
            raise ValueError("A resource path must be provided.")

        if email is None:
            raise ValueError("An email must be provided.")

        if client_id is None:
            raise ValueError("A client id must be provided.")

        if client_secret is None:
            raise ValueError("A client secret must be provided")

        if refresh_token is None:
            raise ValueError("A refresh token must be provided")

        if module_name is None:
            raise ValueError("A module name must be provided")

        if body is None:
            raise ValueError("An object must be provided")

        if "data" not in body or not isinstance(body.get("data"), list):
            raise ValueError("An object must be provided")

        try:
            api_client = ApiClient(log_path, store_path, resource_path, email, env, client_id, client_secret,
                                   refresh_token)

            request = BodyWrapper()

            records = []

            for elem in body.get("data"):
                rec = Record()
                for key in elem:
                    rec.add_key_value(key, elem.get(key))
                records.append(rec)

            request.set_data(records)

            triggers = []
            if "triggers" in body:
                triggers = body.get("triggers")

            request.set_trigger(triggers)

            response = RecordOperations().create_records(module_api_name=module_name, request=request)
            return response
        except Exception as error:
            print(error)
            raise error


class List(Task):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    @defaults_from_attrs()
    def run(self, log_path: str = "ZOHO_LOG_PATH", store_path: str = "ZOHO_STORE_PATH",
            resource_path: str = "ZOHO_RESOURCE_PATH", email: str = "ZOHO_USER_ID", env: str = "ZOHO_DATA_CENTER",
            client_id: str = "ZOHO_CLIENT_ID", client_secret: str = "ZOHO_CLIENT_SECRET",
            refresh_token: str = "ZOHO_REFRESH_TOKEN", module_name: str = None, headers_map: dict = None,
            params_map: dict = None):
        if log_path is None:
            raise ValueError("A log path must be provided.")

        if store_path is None:
            raise ValueError("A store path must be provided.")

        if resource_path is None:
            raise ValueError("A resource path must be provided.")

        if email is None:
            raise ValueError("An email must be provided.")

        if client_id is None:
            raise ValueError("A client id must be provided.")

        if client_secret is None:
            raise ValueError("A client secret must be provided")

        if refresh_token is None:
            raise ValueError("A refresh token must be provided")

        if module_name is None:
            raise ValueError("A module name must be provided")

        if headers_map is None:
            headers_map = {}

        if params_map is None:
            params_map = {}

        try:
            api_client = ApiClient(log_path, store_path, resource_path, email, env, client_id, client_secret,
                                   refresh_token)

            headers = HeaderMap()
            for key in headers_map:
                headers.add(key, headers_map.get(key))

            params = ParameterMap()
            for key in params_map:
                params.add(key, params_map.get(key))

            response = RecordOperations().get_records(module_api_name=module_name, param_instance=params,
                                                      header_instance=headers)
            return response
        except Exception as error:
            print(error)
            raise error


class Fetch(Task):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    @defaults_from_attrs()
    def run(self, log_path: str = "ZOHO_LOG_PATH", store_path: str = "ZOHO_STORE_PATH",
            resource_path: str = "ZOHO_RESOURCE_PATH", email: str = "ZOHO_USER_ID", env: str = "ZOHO_DATA_CENTER",
            client_id: str = "ZOHO_CLIENT_ID", client_secret: str = "ZOHO_CLIENT_SECRET",
            refresh_token: str = "ZOHO_REFRESH_TOKEN", module_name: str = None, record_id: int = None,
            headers_map: dict = None, params_map: dict = None):
        if log_path is None:
            raise ValueError("A log path must be provided.")

        if store_path is None:
            raise ValueError("A store path must be provided.")

        if resource_path is None:
            raise ValueError("A resource path must be provided.")

        if email is None:
            raise ValueError("An email must be provided.")

        if client_id is None:
            raise ValueError("A client id must be provided.")

        if client_secret is None:
            raise ValueError("A client secret must be provided")

        if refresh_token is None:
            raise ValueError("A refresh token must be provided")

        if module_name is None:
            raise ValueError("A module name must be provided")

        if record_id is None:
            raise ValueError("A record ID must be provided")

        if headers_map is None:
            headers_map = {}

        if params_map is None:
            params_map = {}

        try:
            api_client = ApiClient(log_path, store_path, resource_path, email, env, client_id, client_secret,
                                   refresh_token)

            headers = HeaderMap()
            for key in headers_map:
                headers.add(key, headers_map.get(key))

            params = ParameterMap()
            for key in params_map:
                params.add(key, params_map.get(key))

            response = RecordOperations().get_record(id=record_id, module_api_name=module_name, param_instance=params,
                                                     header_instance=headers)
            return response
        except Exception as error:
            print(error)
            raise error


class Update(Task):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    @defaults_from_attrs()
    def run(self, log_path: str = "ZOHO_LOG_PATH", store_path: str = "ZOHO_STORE_PATH",
            resource_path: str = "ZOHO_RESOURCE_PATH", email: str = "ZOHO_USER_ID", env: str = "ZOHO_DATA_CENTER",
            client_id: str = "ZOHO_CLIENT_ID", client_secret: str = "ZOHO_CLIENT_SECRET",
            refresh_token: str = "ZOHO_REFRESH_TOKEN", module_name: str = None, body: dict = None,
            headers_map: dict = None):
        if log_path is None:
            raise ValueError("A log path must be provided.")

        if store_path is None:
            raise ValueError("A store path must be provided.")

        if resource_path is None:
            raise ValueError("A resource path must be provided.")

        if email is None:
            raise ValueError("An email must be provided.")

        if client_id is None:
            raise ValueError("A client id must be provided.")

        if client_secret is None:
            raise ValueError("A client secret must be provided")

        if refresh_token is None:
            raise ValueError("A refresh token must be provided")

        if module_name is None:
            raise ValueError("A module name must be provided")

        if headers_map is None:
            headers_map = {}

        if body is None:
            raise ValueError("An object must be provided")

        if "data" not in body or not isinstance(body.get("data"), list):
            raise ValueError("An object must be provided")

        try:
            api_client = ApiClient(log_path, store_path, resource_path, email, env, client_id, client_secret,
                                   refresh_token)

            headers = HeaderMap()
            for key in headers_map:
                headers.add(key, headers_map.get(key))

            request = BodyWrapper()

            records = []

            for elem in body.get("data"):
                rec = Record()
                rec.set_id(elem.get("id"))
                elem.remove("id")
                for key in elem:
                    rec.add_key_value(key, elem.get(key))
                records.append(rec)

            request.set_data(records)

            triggers = []
            if "triggers" in body:
                triggers = body.get("triggers")

            request.set_trigger(trigger=triggers)

            response = RecordOperations().update_records(module_api_name=module_name, request=request,
                                                         header_instance=headers)
            return response
        except Exception as error:
            print(error)
            raise error


class Upsert(Task):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    @defaults_from_attrs()
    def run(self, log_path: str = "ZOHO_LOG_PATH", store_path: str = "ZOHO_STORE_PATH",
            resource_path: str = "ZOHO_RESOURCE_PATH", email: str = "ZOHO_USER_ID", env: str = "ZOHO_DATA_CENTER",
            client_id: str = "ZOHO_CLIENT_ID", client_secret: str = "ZOHO_CLIENT_SECRET",
            refresh_token: str = "ZOHO_REFRESH_TOKEN", module_name: str = None, body: dict = None,
            headers_map: dict = None):
        if log_path is None:
            raise ValueError("A log path must be provided.")

        if store_path is None:
            raise ValueError("A store path must be provided.")

        if resource_path is None:
            raise ValueError("A resource path must be provided.")

        if email is None:
            raise ValueError("An email must be provided.")

        if client_id is None:
            raise ValueError("A client id must be provided.")

        if client_secret is None:
            raise ValueError("A client secret must be provided")

        if refresh_token is None:
            raise ValueError("A refresh token must be provided")

        if module_name is None:
            raise ValueError("A module name must be provided")

        if headers_map is None:
            headers_map = {}

        if body is None:
            raise ValueError("An object must be provided")

        if "data" not in body or not isinstance(body.get("data"), list):
            raise ValueError("An object must be provided")

        if "duplicate_check_fields" not in body or not isinstance(body.get("duplicate_check_fields"), list):
            raise ValueError("An object must be provided")

        try:
            api_client = ApiClient(log_path, store_path, resource_path, email, env, client_id, client_secret,
                                   refresh_token)

            headers = HeaderMap()
            for key in headers_map:
                headers.add(key, headers_map.get(key))

            request = BodyWrapper()

            records = []

            for elem in body.get("data"):
                rec = Record()
                for key in elem:
                    rec.add_key_value(key, elem.get(key))
                records.append(rec)

            request.set_data(records)
            request.set_duplicate_check_fields(body.get("duplicate_check_fields"))

            triggers = []
            if "triggers" in body:
                triggers = body.get("triggers")

            request.set_trigger(trigger=triggers)

            response = RecordOperations().upsert_records(module_api_name=module_name, request=request,
                                                         header_instance=headers)
            return response
        except Exception as error:
            print(error)
            raise error


class Delete(Task):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    @defaults_from_attrs()
    def run(self, log_path: str = "ZOHO_LOG_PATH", store_path: str = "ZOHO_STORE_PATH",
            resource_path: str = "ZOHO_RESOURCE_PATH", email: str = "ZOHO_USER_ID", env: str = "ZOHO_DATA_CENTER",
            client_id: str = "ZOHO_CLIENT_ID", client_secret: str = "ZOHO_CLIENT_SECRET",
            refresh_token: str = "ZOHO_REFRESH_TOKEN", module_name: str = None, record_ids: list = None,
            params_map: dict = None, headers_map: dict = None):
        if log_path is None:
            raise ValueError("A log path must be provided.")

        if store_path is None:
            raise ValueError("A store path must be provided.")

        if resource_path is None:
            raise ValueError("A resource path must be provided.")

        if email is None:
            raise ValueError("An email must be provided.")

        if client_id is None:
            raise ValueError("A client id must be provided.")

        if client_secret is None:
            raise ValueError("A client secret must be provided")

        if refresh_token is None:
            raise ValueError("A refresh token must be provided")

        if module_name is None:
            raise ValueError("A module name must be provided")

        if record_ids is None or not isinstance(record_ids, list):
            raise ValueError("A list of record IDs must be provided")

        if headers_map is None:
            headers_map = {}

        if params_map is None:
            params_map = {}

        try:
            api_client = ApiClient(log_path, store_path, resource_path, email, env, client_id, client_secret,
                                   refresh_token)

            headers = HeaderMap()
            for key in headers_map:
                headers.add(key, headers_map.get(key))

            params = ParameterMap()
            for key in params_map:
                params.add(key, params_map.get(key))

            params.add(DeleteRecordsParam.wf_trigger, "true")

            for record_id in record_ids:
                params.add(DeleteRecordsParam.ids, record_id)

            response = RecordOperations().delete_records(module_api_name=module_name, param_instance=params,
                                                         header_instance=headers)
            return response
        except Exception as error:
            print(error)
            raise error


class ListDeleted(Task):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    @defaults_from_attrs()
    def run(self, log_path: str = "ZOHO_LOG_PATH", store_path: str = "ZOHO_STORE_PATH",
            resource_path: str = "ZOHO_RESOURCE_PATH", email: str = "ZOHO_USER_ID", env: str = "ZOHO_DATA_CENTER",
            client_id: str = "ZOHO_CLIENT_ID", client_secret: str = "ZOHO_CLIENT_SECRET",
            refresh_token: str = "ZOHO_REFRESH_TOKEN", module_name: str = None, params_map: dict = None,
            headers_map: dict = None):
        if log_path is None:
            raise ValueError("A log path must be provided.")

        if store_path is None:
            raise ValueError("A store path must be provided.")

        if resource_path is None:
            raise ValueError("A resource path must be provided.")

        if email is None:
            raise ValueError("An email must be provided.")

        if client_id is None:
            raise ValueError("A client id must be provided.")

        if client_secret is None:
            raise ValueError("A client secret must be provided")

        if refresh_token is None:
            raise ValueError("A refresh token must be provided")

        if module_name is None:
            raise ValueError("A module name must be provided")

        if headers_map is None:
            headers_map = {}

        if params_map is None:
            params_map = {}

        try:
            api_client = ApiClient(log_path, store_path, resource_path, email, env, client_id, client_secret,
                                   refresh_token)

            headers = HeaderMap()
            for key in headers_map:
                headers.add(key, headers_map.get(key))

            params = ParameterMap()
            for key in params_map:
                params.add(key, params_map.get(key))

            response = RecordOperations().get_deleted_records(module_api_name=module_name, param_instance=params,
                                                              header_instance=headers)
            return response
        except Exception as error:
            print(error)
            raise error


class Search(Task):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    @defaults_from_attrs()
    def run(self, log_path: str = "ZOHO_LOG_PATH", store_path: str = "ZOHO_STORE_PATH",
            resource_path: str = "ZOHO_RESOURCE_PATH", email: str = "ZOHO_USER_ID", env: str = "ZOHO_DATA_CENTER",
            client_id: str = "ZOHO_CLIENT_ID", client_secret: str = "ZOHO_CLIENT_SECRET",
            refresh_token: str = "ZOHO_REFRESH_TOKEN", module_name: str = None, params_map: dict = None,
            headers_map: dict = None):
        if log_path is None:
            raise ValueError("A log path must be provided.")

        if store_path is None:
            raise ValueError("A store path must be provided.")

        if resource_path is None:
            raise ValueError("A resource path must be provided.")

        if email is None:
            raise ValueError("An email must be provided.")

        if client_id is None:
            raise ValueError("A client id must be provided.")

        if client_secret is None:
            raise ValueError("A client secret must be provided")

        if refresh_token is None:
            raise ValueError("A refresh token must be provided")

        if module_name is None:
            raise ValueError("A module name must be provided")

        if headers_map is None:
            headers_map = {}

        if params_map is None:
            params_map = {}

        try:
            api_client = ApiClient(log_path, store_path, resource_path, email, env, client_id, client_secret,
                                   refresh_token)

            headers = HeaderMap()
            for key in headers_map:
                headers.add(key, headers_map.get(key))

            params = ParameterMap()
            for key in params_map:
                params.add(key, params_map.get(key))

            response = RecordOperations().get_deleted_records(module_api_name=module_name, param_instance=params,
                                                              header_instance=headers)
            return response
        except Exception as error:
            print(error)
            raise error
import re
from typing import Dict, Union

import numpy as np
import pandas as pd

from .data_grid_type import use_field_names_in_headers_arg_parser
from ...delivery.data._data_provider import request_method_value
from ...delivery.data.endpoint import RequestMethod
from ...content._content_provider import (
    DataProvider,
    RequestFactory,
    ResponseFactory,
    ContentValidator,
)
from ...fin_coder_layer import ADC_PATTERN
from ...tools import universe_arg_parser, fields_arg_parser


# --------------------------------------------------------------------------------------
#   Response
# --------------------------------------------------------------------------------------


def convert_json_rdp_to_pandas(
    json_data: dict, use_title: bool = False
) -> Union[None, pd.DataFrame]:
    if "headers" not in json_data:
        return None

    data = json_data.get("data")
    name_title = "name" if use_title else "title"
    columns = [field[name_title] for field in json_data["headers"]]
    if data:
        np_array = np.array(data)
        df = pd.DataFrame(np_array, columns=columns)
        if not df.empty:
            df = df.convert_dtypes()
    else:
        df = pd.DataFrame([], columns=columns)

    return df


class DataGridRDPResponseFactory(ResponseFactory):
    def create_success(self, *args, **kwargs):
        data = args[0]
        inst = self.response_class(is_success=True, **data)
        content_data = data.get("content_data")
        use_field_names_in_headers = kwargs.get("use_field_names_in_headers")
        dataframe = convert_json_rdp_to_pandas(content_data, use_field_names_in_headers)
        inst.data = self.data_class(content_data, dataframe)
        return inst


def convert_json_udf_to_pandas(
    json_data: dict, use_field: bool = False
) -> Union[None, pd.DataFrame]:
    if "headers" not in json_data:
        return None

    use_field = "field" if use_field else "displayName"
    headers = [
        header.get(use_field) or header.get("displayName")
        for header in json_data["headers"][0]
    ]

    get_value = lambda value: value["value"] if value is dict else value
    data = np.array([list(map(get_value, row)) for row in json_data.get("data", [])])
    if len(data):
        df = pd.DataFrame(data, columns=headers)
        df = df.apply(pd.to_numeric, errors="ignore")
        if not df.empty:
            df = df.convert_dtypes()
    else:
        df = pd.DataFrame([], columns=headers)

    return df


class DataGridUDFResponseFactory(ResponseFactory):
    def create_success(self, *args, **kwargs):
        data = args[0]
        inst = self.response_class(is_success=True, **data)
        content_data = data.get("content_data")
        responses: Dict = content_data.get("responses")[0]
        use_field_names_in_headers = kwargs.get("use_field_names_in_headers")
        dataframe = convert_json_udf_to_pandas(responses, use_field_names_in_headers)
        inst.data = self.data_class(responses, dataframe)
        return inst


# --------------------------------------------------------------------------------------
#   Request
# --------------------------------------------------------------------------------------


def validate_correct_format_parameters(*_, **kwargs) -> dict:
    parameters = kwargs.get("parameters")
    extended_params = kwargs.get("extended_params")
    universe = kwargs.get("universe")
    fields = kwargs.get("fields")
    use_field_names_in_headers = kwargs.get("use_field_names_in_headers")

    if parameters is not None and not isinstance(parameters, dict):
        raise ValueError(f"Arg parameters must be a dictionary")
    extended_params = extended_params or {}
    universe = extended_params.get("universe") or universe
    universe = universe_arg_parser.get_list(universe)
    universe = [value.upper() if value.islower() else value for value in universe]
    fields = fields_arg_parser.get_list(fields)
    use_field_names_in_headers = use_field_names_in_headers_arg_parser.get_bool(
        use_field_names_in_headers
    )

    kwargs.update(
        {
            "universe": universe,
            "fields": fields,
            "parameters": parameters,
            "use_field_names_in_headers": use_field_names_in_headers,
            "extended_params": extended_params,
        }
    )
    return kwargs


class DataGridRDPRequestFactory(RequestFactory):
    def get_body_parameters(self, *_, **kwargs) -> dict:
        kwargs = validate_correct_format_parameters(*_, **kwargs)
        body_parameters = {}

        universe = kwargs.get("universe")
        if universe:
            body_parameters["universe"] = universe

        fields = kwargs.get("fields")
        if fields:
            body_parameters["fields"] = fields

        parameters = kwargs.get("parameters")
        if parameters:
            body_parameters["parameters"] = parameters

        output = kwargs.get("output")
        if output:
            body_parameters["output"] = output

        return body_parameters

    def get_request_method(self, *_, **kwargs) -> RequestMethod:
        return RequestMethod.POST


class DataGridUDFRequestFactory(RequestFactory):
    def create(self, *args, **kwargs):
        session = args[0]
        url_root = session._get_rdp_url_root()
        url = url_root.replace("rdp", "udf")

        method = self.get_request_method(*args, **kwargs)
        header_parameters = kwargs.get("header_parameters") or {}
        extended_params = kwargs.get("extended_params") or {}
        body_parameters = self.get_body_parameters(*args, **kwargs)
        body_parameters = self.extend_body_parameters(body_parameters, extended_params)

        headers = {"Content-Type": "application/json"}
        headers.update(header_parameters)
        request = {
            "url": url,
            "method": request_method_value.get(method),
            "headers": headers,
            "body": {
                "Entity": {
                    "E": "DataGrid_StandardAsync",
                    "W": {"requests": [body_parameters]},
                }
            },
        }

        return request

    def get_body_parameters(self, *_, **kwargs) -> dict:
        kwargs = validate_correct_format_parameters(*_, **kwargs)
        layout_rows = []
        body_parameters = {
            "layout": {
                "columns": [{"item": "dataitem"}],
                "rows": layout_rows,
            }
        }

        instruments = kwargs.get("universe")
        if instruments:
            body_parameters["instruments"] = instruments

        fields = kwargs.get("fields")
        if fields:
            body_parameters["fields"] = [
                {"name": i} for i in fields if re.match(ADC_PATTERN, i)
            ]

        parameters = kwargs.get("parameters")
        if parameters:
            body_parameters["parameters"] = parameters

        output = kwargs.get("output", "")
        if re.search(r"\bin\b", output, re.I):
            layout_rows.append({"item": "instrument"})
        if re.search(r"\bdate\b", output, re.I):
            layout_rows.append({"item": "date"})

        return body_parameters

    def get_request_method(self, *_, **kwargs) -> RequestMethod:
        return RequestMethod.POST


# --------------------------------------------------------------------------------------
#   Content data validator
# --------------------------------------------------------------------------------------


class DataGridRDPContentValidator(ContentValidator):
    def validate_content_data(self, data):
        is_valid = True

        status = data.get("status", {})
        status_content = status.get("content", "")

        if status_content.startswith("Failed"):
            is_valid = False
            data["error_code"] = -1
            data["error_message"] = status_content
            return is_valid

        content_data = data.get("content_data", {})
        content_data_ = content_data.get("data")
        error = content_data.get("error")

        if not content_data:
            is_valid = False
        elif error and not content_data_:
            is_valid = False
            data["error_code"] = error.get("code", -1)
            data["error_message"] = error.get("description")

            if not data["error_message"]:
                error_message = error.get("message")
                errors = error.get("errors")
                if isinstance(errors, list):
                    error_message += ":\n"
                    error_message += "\n".join(map(str, errors))
                data["error_message"] = error_message

        return is_valid


class DataGridUDFContentValidator(ContentValidator):
    def validate_content_data(self, data):
        is_valid = True

        status = data.get("status", {})
        status_content = status.get("content", "")

        if status_content.startswith("Failed"):
            is_valid = False
            data["error_code"] = -1
            data["error_message"] = status_content
            return is_valid

        content_data = data.get("content_data", {})
        if isinstance(content_data, str):
            is_valid = False
            data["error_code"] = -1
            data["error_message"] = content_data
            return is_valid

        response = content_data.get("responses", [])
        response = response[0] if response else {}
        response_data = response.get("data")
        error = response.get("error")

        if not content_data:
            is_valid = False
        elif "ErrorCode" in content_data:
            is_valid = False
            data["error_code"] = content_data.get("ErrorCode", -1)
            data["error_message"] = content_data.get("ErrorMessage")
        elif error and isinstance(error, dict) and not response_data:
            is_valid = False
            data["error_code"] = error.get("code", -1)
            data["error_message"] = error.get("message") or error
        elif error and not response_data:
            is_valid = False
            data["error_code"] = -1
            data["error_message"] = error

        return is_valid


# --------------------------------------------------------------------------------------
#   Providers
# --------------------------------------------------------------------------------------


data_grid_rdp_data_provider = DataProvider(
    request=DataGridRDPRequestFactory(),
    response=DataGridRDPResponseFactory(),
    validator=DataGridRDPContentValidator(),
)

data_grid_udf_data_provider = DataProvider(
    request=DataGridUDFRequestFactory(),
    response=DataGridUDFResponseFactory(),
    validator=DataGridUDFContentValidator(),
)

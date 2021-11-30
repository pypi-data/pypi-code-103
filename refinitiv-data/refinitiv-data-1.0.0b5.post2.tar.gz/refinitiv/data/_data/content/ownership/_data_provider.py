from dateutil.parser import ParserError
from refinitiv.data._data.tools import ArgsParser

from ._enums import StatTypes, Frequency, SortOrder
from .._content_provider import (
    DataProvider,
    RequestFactory,
    ResponseFactory,
    Response,
)
from ...tools import convert_content_data_to_df
from ...tools import universe_arg_parser, make_enum_arg_parser
from ...tools._datetime import ownership_datetime_adapter

MAX_LIMIT = 100


def join_data(input_data) -> dict:
    first, *input_data = input_data
    content_data = first.get("content_data", {})
    status = first.get("status")
    headers = content_data.get("headers")
    universe = content_data.get("universe")
    _data = content_data.get("data")

    result = {
        "content_data": {
            "headers": headers,
            "universe": universe,
            "data": _data,
        },
        "status": status,
    }
    result_data = _data
    for data in input_data:
        _data = data["content_data"]["data"]
        result_data.extend(_data)
    return result


def parse_str(param):
    if isinstance(param, str):
        return param
    raise ValueError(f"Invalid type, expected str: {type(param)} is given")


class OwnershipResponse(Response):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        error = self.status.get("error")
        if error:
            errors = error.get("errors")
            if errors:
                self.error_message = errors[0].get("reason", self.error_message)


class OwnershipResponseFactory(ResponseFactory):
    def create_success(self, *args, **kwargs):
        data = args[0]
        content_data = data.get("content_data")
        inst = self.response_class(is_success=True, **data)
        dataframe = (
            convert_content_data_to_df(content_data)
            if "headers" in content_data
            else None
        )
        inst.data = self.data_class(content_data, dataframe)
        inst.data._owner = inst
        return inst


class OwnershipRequestFactory(RequestFactory):
    def get_query_parameters(self, *_, **kwargs) -> list:
        query_parameters = []
        universe = kwargs.get("universe")
        universe = universe_arg_parser.get_str(universe, delim=",")
        query_parameters.append(("universe", universe))

        stat_type = kwargs.get("stat_type")
        if stat_type is not None:
            stat_type = stat_types_ownership_arg_parser.get_str(stat_type)
            query_parameters.append(("statType", stat_type))

        offset = kwargs.get("offset")
        if offset is not None:
            query_parameters.append(("offset", offset))

        limit = kwargs.get("limit")
        if limit is not None:
            query_parameters.append(("limit", limit))

        sort_order = kwargs.get("sort_order")
        if sort_order is not None:
            sort_order = sort_order_ownership_arg_parser.get_str(sort_order)
            query_parameters.append(("sortOrder", sort_order))

        frequency = kwargs.get("frequency")
        if frequency is not None:
            frequency = frequency_ownership_arg_parser.get_str(frequency)
            query_parameters.append(("frequency", frequency))

        start = kwargs.get("start")
        if start is not None:
            start = ownership_datetime_adapter.get_str(start)
            query_parameters.append(("start", start))

        end = kwargs.get("end")
        if end is not None:
            end = ownership_datetime_adapter.get_str(end)
            query_parameters.append(("end", end))

        count = kwargs.get("count")
        if count is not None:
            query_parameters.append(("count", count))

        return query_parameters

    def extend_query_parameters(self, query_parameters, extended_params):
        # query_parameters -> [("param1", "val1"), ]
        result = dict(query_parameters)
        # result -> {"param1": "val1"}
        result.update(extended_params)
        # result -> {"param1": "val1", "extended_param": "value"}
        # return [("param1", "val1"), ("extended_param", "value")]
        return list(result.items())


class OwnershipDataProvider(DataProvider):
    async def get_data_async(self, *args, **kwargs):
        limit = kwargs.get("limit")
        if limit is not None and limit > MAX_LIMIT:
            data_list = []
            for offset in range(0, limit, MAX_LIMIT):
                _kwargs = kwargs
                kwargs["limit"] = (
                    MAX_LIMIT if offset < limit - MAX_LIMIT else limit - offset
                )
                kwargs["offset"] = offset if offset else None

                request = self.request.create(*args, **kwargs)
                raw_response = await self.connection.send_async(
                    request, *args, **kwargs
                )
                is_success, data = self.parser.parse_raw_response(raw_response)

                if is_success and self.validator.validate_content_data(data):
                    if not data["content_data"]["data"]:
                        break
                    data_list.append(data)
            data = join_data(data_list)
            response = self.response.create_success(data, *args, **kwargs)
        else:
            response = await super().get_data_async(*args, **kwargs)
        return response


universe_ownership_arg_parser = ArgsParser(parse_str)
stat_types_ownership_arg_parser = make_enum_arg_parser(StatTypes)
sort_order_ownership_arg_parser = make_enum_arg_parser(SortOrder)
frequency_ownership_arg_parser = make_enum_arg_parser(Frequency)

ownership_data_provider = OwnershipDataProvider(
    request=OwnershipRequestFactory(),
    response=OwnershipResponseFactory(response_class=OwnershipResponse),
)

from .._content_provider import (
    DataProvider,
    ResponseFactory,
    RequestFactory,
    ContentValidator,
)
from ...tools import convert_content_data_to_df

# ---------------------------------------------------------------------------
#   Request
# ---------------------------------------------------------------------------
from ...tools import universe_arg_parser


class ESGRequestFactory(RequestFactory):
    def get_query_parameters(self, *args, **kwargs):
        query_parameters = []

        #
        # universe
        #
        universe = kwargs.get("universe")
        if universe:
            universe = universe_arg_parser.get_str(universe, delim=",")
            query_parameters.append(("universe", universe))

        #
        # start
        #
        start = kwargs.get("start")
        if start is not None:
            query_parameters.append(("start", start))

        #
        # end
        #
        end = kwargs.get("end")
        if end is not None:
            query_parameters.append(("end", end))

        return query_parameters


# ---------------------------------------------------------------------------
#   Response
# ---------------------------------------------------------------------------


class ESGResponseFactory(ResponseFactory):
    def create_success(self, *args, **kwargs):
        data = args[0]
        inst = self.response_class(is_success=True, **data)
        content_data = data.get("content_data")
        dataframe = convert_content_data_to_df(content_data)
        inst.data = self.data_class(content_data, dataframe)
        inst.data._owner = inst
        return inst


# ---------------------------------------------------------------------------
#   Content data validator
# ---------------------------------------------------------------------------


class ESGContentValidator(ContentValidator):
    def validate_content_data(self, data):
        is_valid = True
        content_data = data.get("content_data")
        error = content_data.get("error")

        if not content_data:
            is_valid = False

        elif error:
            is_valid = False
            data["error_code"] = error.get("code")

            error_message = error.get("description")

            if not error_message:
                error_message = error.get("message")
                errors = error.get("errors")
                if isinstance(errors, list):
                    error_message += ":\n"
                    error_message += "\n".join(map(str, errors))

            data["error_message"] = error_message

        return is_valid


# ---------------------------------------------------------------------------
#   Provider
# ---------------------------------------------------------------------------

esg_data_provider = DataProvider(
    request=ESGRequestFactory(),
    response=ESGResponseFactory(),
    validator=ESGContentValidator(),
)

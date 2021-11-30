from enum import Enum

from ...tools import make_enum_arg_parser, ArgsParser, validate_bool_value


class DataGridType(Enum):
    UDF = "udf"
    RDP = "rdp"


data_grid_types_arg_parser = make_enum_arg_parser(DataGridType)
use_field_names_in_headers_arg_parser = ArgsParser(validate_bool_value)


class data_grid_type_value_by_content_type:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            from .. import ContentType

            cls._instance = {
                DataGridType.UDF.value: ContentType.DATA_GRID_UDF,
                DataGridType.RDP.value: ContentType.DATA_GRID_RDP,
            }
        return cls._instance

    def get(self, key):
        return self._instance.get(key)

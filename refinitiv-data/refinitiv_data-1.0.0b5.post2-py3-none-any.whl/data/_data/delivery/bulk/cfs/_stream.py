from ._base_definition import BaseDefinition
from ...data._data_type import DataType


class CFSStream(BaseDefinition):
    def __init__(self, id):
        super().__init__(data_type=DataType.CFS_STREAM, id=id)

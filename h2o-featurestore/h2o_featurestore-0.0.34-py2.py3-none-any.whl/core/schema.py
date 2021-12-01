from copy import deepcopy

from . import CoreService_pb2 as pb
from .data_types import ARRAY, MAP
from .utils import extract_columns


class Column:
    def __init__(self, name, data_type):
        self.name = name
        if not isinstance(data_type, str):
            self.__data_type = self.to_string(data_type)
        else:
            self.__data_type = data_type

    @property
    def data_type(self):
        return self.__data_type

    @data_type.setter
    def data_type(self, value):
        self.__data_type = self.to_string(value)

    def to_string(self, data_type):
        if isinstance(data_type, (ARRAY, MAP)):
            return data_type.flatten()
        else:
            return pb.FeatureDataType.Name(data_type).lower()


class Schema:
    def __init__(self, columns):
        self.__order = [col.name for col in columns]
        self.__columns = {col.name: col for col in columns}

    @classmethod
    def load(cls, feature_set):
        fields = [
            Column(feature.name, feature.data_type)
            for feature in feature_set._feature_set.features
        ]
        return cls(fields)

    def dump(self):
        return [self._create_proto_spec(self.__columns[col]) for col in self.__order]

    def update_column(self, name, data_type):
        new_columns = deepcopy(self.__columns)
        new_columns[name].data_type = data_type
        return Schema([new_columns[name] for name in self.__order])

    def select(self, columns):
        new_cols = [self.__columns[name] for name in self.__order if name in columns]
        return Schema(new_cols)

    def exclude(self, columns):
        new_cols = [
            self.__columns[name] for name in self.__order if name not in columns
        ]
        return Schema(new_cols)

    def append(self, column, after=None):
        new_order = self.__order[:]
        if not after:
            new_order.append(column.name)
        else:
            index = new_order.index(after) + 1
            new_order.insert(index, column.name)
        new_cols = self.__columns.copy()
        new_cols[column.name] = column
        return Schema([new_cols[name] for name in new_order])

    def prepend(self, column, before=None):
        new_order = self.__order[:]
        if not before:
            new_order.insert(0, column.name)
        else:
            index = new_order.index(before)
            new_order.insert(index, column.name)
        new_cols = self.__columns.copy()
        new_cols[column.name] = column
        return Schema([new_cols[name] for name in new_order])

    @classmethod
    def from_string(cls, schema_str):
        return cls(extract_columns(schema_str))

    def to_string(self):
        schema = []
        for fld in self.__order:
            col = self.__columns[fld]
            schema.append(f"{col.name} {col.data_type}")
        return ", ".join(schema)

    def _create_proto_spec(self, column):
        feature_spec = pb.FeatureSchema()
        feature_spec.name = column.name
        feature_spec.data_type = column.data_type
        return feature_spec

    def __repr__(self):
        return str(
            [
                {
                    "name": self.__columns[col].name,
                    "data_type": self.__columns[col].data_type,
                }
                for col in self.__order
            ]
        )

from . import CoreService_pb2 as pb

TINYINT = pb.FeatureDataType.TinyInt
SMALLINT = pb.FeatureDataType.SmallInt
BIGINT = pb.FeatureDataType.BigInt
INT = pb.FeatureDataType.Int
DOUBLE = pb.FeatureDataType.Double
FLOAT = pb.FeatureDataType.Float
STRING = pb.FeatureDataType.String
BINARY = pb.FeatureDataType.Binary
BOOLEAN = pb.FeatureDataType.Boolean
DATE = pb.FeatureDataType.Date
TIMESTAMP = pb.FeatureDataType.Timestamp


class ARRAY:
    """ARRAY type accepts the type of the element as an argument"""

    def __init__(self, sub_type):
        try:
            self.sub_type = pb.FeatureDataType.Name(sub_type).lower()
        except:
            self.sub_type = sub_type.flatten()

    def flatten(self):
        return f"array<{self.sub_type}>"


class MAP:
    """STRUCT type accepts the type of the key and the value as arguments"""

    def __init__(self, key_type, value_type):
        try:
            self.key_type = pb.FeatureDataType.Name(key_type).lower()
        except:
            self.key_type = key_type.flatten()
        try:
            self.value_type = pb.FeatureDataType.Name(value_type).lower()
        except:
            self.value_type = value_type.flatten()

    def flatten(self):
        return f"map<{self.key_type},{self.value_type}>"

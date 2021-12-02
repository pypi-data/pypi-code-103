from .DataExporter import DataExporter

try:
    import pyarrow
    import numpy
except ImportError:
    pass


class ObjectExporter(DataExporter):
    """ An example Exporter that supports a lot of default formats using pyarrow"""

    supportedTypes = []
    def checkType(self, type):
        return type in (str, int, bool, float, list, dict, numpy.ndarray) or type in self.supportedTypes

    def importData(self, byteString, options={}):
        context = pyarrow.default_serialization_context()
        buffer = pyarrow.py_buffer(byteString)
        df = context.deserialize(buffer)

        return df

    def export(self, df, options={}):
        context = pyarrow.default_serialization_context()
        serialized_df = context.serialize(df)
        buffer = serialized_df.to_buffer()
        byteString = buffer.to_pybytes()

        return byteString

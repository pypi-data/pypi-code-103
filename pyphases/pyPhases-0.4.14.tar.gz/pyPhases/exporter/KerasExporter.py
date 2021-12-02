from .ObjectExporter import ObjectExporter

try:
    import keras
except ImportError:
    pass

from ..util.FileWrapper import wrapRead, wrapWrite

class KerasExporter(ObjectExporter):
    """ An Exporter for keras models"""
    def checkType(self, type):
        return issubclass(type, keras.Model)

    def importData(self, data, options = {}):
        def read(path):
            return keras.models.load_model(path)

        return wrapRead(read, data)


    def export(self, model : "keras.Model", options = {}):
        def write(path):
            model.save(path)

        return wrapWrite(write)



from kigo.etl.runtime.registry import MappingRegistry


class MappingInfo:
    def __init__(self, clazz, params: dict = {}):
        self._clazz = [clazz, params]
        self._readers = []

    @property
    def readers(self):
        return self._readers

    @property
    def clazz(self):
        return self._clazz

    @readers.setter
    def readers(self, readers):
        self._readers = readers

    def __repr__(self):
        return f"MappingInfo <{self._clazz}> readers: {self._readers}>"


def mapping(path=None, reader=None):

    def wrapper(clazz):
        mapping_info = MappingInfo(clazz)
        if reader is not None and path is not None:
            mapping_info.readers.append((MappingRegistry.readers[reader.__name__], {'path': path}))

        MappingRegistry.append_mapping(mapping_info)

        return clazz
    return wrapper


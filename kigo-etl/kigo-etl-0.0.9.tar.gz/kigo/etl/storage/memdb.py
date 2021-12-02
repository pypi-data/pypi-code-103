import zlib
import enum
from multiprocessing import Pool
from kigo.etl.mapper.archetype import Archetype


class CompressionLevel(enum.Enum):
    UNCOMPRESSED = "uncompressed"
    COMPRESSED   = "compressed"
    TEXT         = "text"


class MemoryDB:

    def __init__(self, compresson_level = CompressionLevel.UNCOMPRESSED):
        self.__typeof = {}
        self.__data = {}
        self.__text = False
        self.__compression_level = compresson_level

    @property
    def data(self):
        return self.__data

    def store(self, typeof, object):
        self.__init_typeof(typeof)
        typeof_keys = self.__typeof[typeof]["keys"]
        if typeof_keys:
            for key_name in typeof_keys:
                self.__append_data(typeof, key_name, object)
        else:
            self.__append_data(typeof, None, object)

    def __compress(self, object):
        if self.__compression_level == CompressionLevel.UNCOMPRESSED:
            return object
        elif self.__compression_level == CompressionLevel.COMPRESSED:
            return zlib.compress(str(object).encode("utf-8"))
        else:
            return str(object)

    def __append_data(self, typeof, key_name, object):
        if not key_name:
            self.__data[typeof].append(self.__compress(object))
            return
        current = self.__data[typeof][key_name].get(object[key_name], None)
        data = self.__compress(object)
        if not current:
            self.__data[typeof][key_name][object[key_name]] = data
        elif isinstance(current, list):
            self.__data[typeof][key_name][object[key_name]].append(data)
        else:
            self.__data[typeof][key_name][object[key_name]] = [current, data]

    def __init_typeof(self, typeof):
        if typeof not in self.__typeof:
            self.__typeof[typeof] = {"keys": []}
            self.__data[typeof] = {}
            annotations = typeof.__dict__.get("__annotations__", {})
            for key_name, archetype in annotations.items():
                if archetype.key is not None:
                    self.__data[typeof][key_name] = {}
                    self.__typeof[typeof]["keys"].append(key_name)
            if not self.__typeof[typeof]["keys"]:
                self.__data[typeof] = []


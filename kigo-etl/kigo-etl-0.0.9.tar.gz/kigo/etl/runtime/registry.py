from enum import Enum


def reader(clazz):
    MappingRegistry.append_reader(clazz)
    return clazz


def extractor(clazz):
    MappingRegistry.append_extractor(clazz)
    return clazz


def exposing(something = None):
    def wrapper(clazz):
        MappingRegistry.append_expose(something)
        return clazz
    return wrapper


class MappingType(Enum):
    objects   = "objects"
    documents = "documents"
    light     = "light"


class MappingRegistry:
    __EXPOSED      = {}
    __MAPPINGS     = {}
    __READERS      = {}
    __EXTRACTORS   = {}
    __MAPPING_TYPE = MappingType.documents

    @staticmethod
    def append_mapping(mapping_info):
        if mapping_info.clazz[0].__qualname__ not in MappingRegistry.__MAPPINGS:
            MappingRegistry.__MAPPINGS[mapping_info.clazz[0].__qualname__] = mapping_info
        else:
            raise Exception(f"Duplicate mapping name <{mapping_info.clazz.__qualname__}>!")

    @staticmethod
    def append_reader(clazz):
        if clazz.__qualname__ not in MappingRegistry.__READERS:
            MappingRegistry.__READERS[clazz.__qualname__] = clazz
        else:
            raise Exception(f"Duplicate reader name <{clazz.__qualname__}>!")

    @staticmethod
    def append_extractor(clazz):
        if clazz.__qualname__ not in MappingRegistry.__EXTRACTORS:
            MappingRegistry.__EXTRACTORS[clazz.__qualname__] = clazz
        else:
            raise Exception(f"Duplicate extractor name <{clazz.__qualname__}>!")

    @staticmethod
    def append_expose(clazz):
        if clazz.__qualname__ not in MappingRegistry.__EXPOSED:
            MappingRegistry.__EXPOSED[clazz.__qualname__] = clazz
        else:
            raise Exception(f"Duplicate expose name <{clazz.__qualname__}>!")

    @classmethod
    @property
    def extractors(cls):
        return MappingRegistry.__EXTRACTORS

    @classmethod
    @property
    def mappings(cls):
        return MappingRegistry.__MAPPINGS

    @classmethod
    @property
    def readers(cls):
        return MappingRegistry.__READERS

from kigo.etl.runtime.registry import MappingRegistry


class StaticExtractorAttribute(type):
    def __getattr__(cls, name):
        if name in MappingRegistry.extractors:
            return FabricExtractors(MappingRegistry.extractors[name])
        raise Exception(f"Extractor <{name}> not found. Available extractors: {tuple(MappingRegistry.extractors.keys())}")


class FabricExtractors(metaclass=StaticExtractorAttribute):
    def __init__(self, clazz):
        self.clazz = clazz

    def __getitem__(self, item):
        return self.clazz(item)

    def __call__(self, *args, **kwargs):
        return self.clazz(*args, **kwargs)


Extract = FabricExtractors

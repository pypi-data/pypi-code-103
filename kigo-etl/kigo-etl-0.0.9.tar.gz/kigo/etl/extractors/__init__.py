__all__ = []

from kigo.etl.runtime.registry import  MappingRegistry
from kigo.etl.extractors.operators import ExtractorOperator


class Extractor(ExtractorOperator):

    def call(self, num, raw, obj):
        raise Exception("Not implemented!")

from kigo.etl.mapper.mapping import mapping
from kigo.etl.extractors.fabric import Extract
from kigo.etl.file.readers import TextReader


@mapping("./data/input_1", TextReader)
class SomeClass3:
    data_1 = 'prefix ' + Extract.TextSlice[31:43]

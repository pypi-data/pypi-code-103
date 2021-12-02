from kigo.etl.mapper.mapping import mapping
from kigo.etl.extractors.fabric import Extract
from kigo.etl.file.readers import TextReader


@mapping(path="./data/input_1", reader=TextReader)
class SomeClass:
    data_1 = Extract.TextSlice[31:43]
    data_2 = Extract.TextSlice[49:61]


@mapping("./data/input_1", TextReader)
class SomeClass2:
    data_1 = Extract.TextSlice[31:43]
    data_2 = Extract.TextSlice[49:61]

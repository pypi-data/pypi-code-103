import unittest
import kigo.test.etl.unittest.resources.entities

from kigo.etl.configuration import Config
from kigo.etl.runtime.registry import MappingRegistry
from kigo.etl.unittest.decorators import set_reader
from kigo.etl.file.readers import TextReader


class MyTestCase(unittest.TestCase):

    def setUp(self):
        Config.load("resources/load.json")

    def test_proper_mapping(self):
        # GIVEN
        result = []

        # WHEN
        conf = Config.load("resources/load.json")
        for mapping_key in MappingRegistry.mappings:
            result.append(str(MappingRegistry.mappings[mapping_key]))

        # THEN
        self.assertListEqual(["MappingInfo <[<class 'kigo.test.etl.unittest.resources.entities.SomeClass'>, {}]> readers: [(<class 'kigo.etl.file.readers.TextReader'>, {'path': './data/input_1'})]>",
                              "MappingInfo <[<class 'kigo.test.etl.unittest.resources.entities.SomeClass2'>, {}]> readers: [(<class 'kigo.etl.file.readers.TextReader'>, {'path': './data/input_1'})]>"],
                             result)

    @set_reader(TextReader, init_values={'path': './data/input_2'})
    def test_proper_mapping_with_set_reader(self):
        # GIVEN
        result = []

        # WHEN
        conf = Config.load("resources/load.json")
        for mapping_key in MappingRegistry.mappings:
            result.append(str(MappingRegistry.mappings[mapping_key]))

        # THEN
        self.assertListEqual(["MappingInfo <[<class 'kigo.test.etl.unittest.resources.entities.SomeClass'>, {}]> readers: [(<class 'kigo.etl.file.readers.TextReader'>, {'path': './data/input_1'})]>",
                              "MappingInfo <[<class 'kigo.test.etl.unittest.resources.entities.SomeClass2'>, {}]> readers: [(<class 'kigo.etl.file.readers.TextReader'>, {'path': './data/input_2'})]>"],
                             result)

    @set_reader(TextReader, init_values={'path': './data/input_2'})
    def test_proper_mapping_with_set_reader_without_config_load(self):
        # GIVEN
        result = []

        # WHEN
        for mapping_key in MappingRegistry.mappings:
            result.append(str(MappingRegistry.mappings[mapping_key]))

        # THEN
        self.assertListEqual(["MappingInfo <[<class 'kigo.test.etl.unittest.resources.entities.SomeClass'>, {}]> readers: [(<class 'kigo.etl.file.readers.TextReader'>, {'path': './data/input_2'})]>",
                              "MappingInfo <[<class 'kigo.test.etl.unittest.resources.entities.SomeClass2'>, {}]> readers: [(<class 'kigo.etl.file.readers.TextReader'>, {'path': './data/input_2'})]>"],
                             result)

    @set_reader(TextReader, init_values={'path': './data/input_2'}, mappings=kigo.test.etl.unittest.resources.entities.SomeClass)
    def test_proper_mapping_with_set_reader_for_specific_entity_without_config_load(self):
        # GIVEN
        result = []

        # WHEN
        for mapping_key in MappingRegistry.mappings:
            result.append(str(MappingRegistry.mappings[mapping_key]))

        # THEN
        self.assertListEqual(["MappingInfo <[<class 'kigo.test.etl.unittest.resources.entities.SomeClass'>, {}]> readers: [(<class 'kigo.etl.file.readers.TextReader'>, {'path': './data/input_2'})]>",
                              "MappingInfo <[<class 'kigo.test.etl.unittest.resources.entities.SomeClass2'>, {}]> readers: [(<class 'kigo.etl.file.readers.TextReader'>, {'path': './data/input_1'})]>"],
                             result)

    @set_reader(TextReader, init_values={'path': './data/input_2'}, mappings=[kigo.test.etl.unittest.resources.entities.SomeClass])
    def test_proper_mapping_with_set_reader_for_specific_entity_as_a_list_without_config_load(self):
        # GIVEN
        result = []

        # WHEN
        for mapping_key in MappingRegistry.mappings:
            result.append(str(MappingRegistry.mappings[mapping_key]))

        # THEN
        self.assertListEqual(["MappingInfo <[<class 'kigo.test.etl.unittest.resources.entities.SomeClass'>, {}]> readers: [(<class 'kigo.etl.file.readers.TextReader'>, {'path': './data/input_2'})]>",
                              "MappingInfo <[<class 'kigo.test.etl.unittest.resources.entities.SomeClass2'>, {}]> readers: [(<class 'kigo.etl.file.readers.TextReader'>, {'path': './data/input_1'})]>"],
                             result)

    def test_proper_mapping_without_setter_once_again(self):
        # GIVEN
        result = []

        # WHEN
        conf = Config.load("resources/load.json")
        for mapping_key in MappingRegistry.mappings:
            result.append(str(MappingRegistry.mappings[mapping_key]))

        # THEN
        self.assertListEqual(["MappingInfo <[<class 'kigo.test.etl.unittest.resources.entities.SomeClass'>, {}]> readers: [(<class 'kigo.etl.file.readers.TextReader'>, {'path': './data/input_1'})]>",
                              "MappingInfo <[<class 'kigo.test.etl.unittest.resources.entities.SomeClass2'>, {}]> readers: [(<class 'kigo.etl.file.readers.TextReader'>, {'path': './data/input_1'})]>"],
                             result)


if __name__ == '__main__':
    unittest.main()

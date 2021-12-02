import unittest
from kigo.test.etl.unittest.resources.entity_1 import SomeClass3

from kigo.etl.configuration import Config
from kigo.etl.runtime import runtime
from kigo.etl.unittest.decorators import set_reader
from kigo.etl.file.readers import TextReader


class MyTestCase(unittest.TestCase):

    def setUp(self):
        Config.load("resources/load_1.json")

    @set_reader(TextReader, init_values={'path': r'resources/data/input_3'})
    def test_something(self):
        # GIVEN

        # WHEN
        db = runtime.process()

        # THEN
        self.assertEqual('prefix some data 11', db.data[SomeClass3][0]['data_1'])


if __name__ == '__main__':
    unittest.main()

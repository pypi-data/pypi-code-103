""" Tests metadata base class. """

import os
import glob
import unittest
import datetime

from src.medali.core import MetaData


class MetadataConfigReadTest(unittest.TestCase):
    """ Tests reading of all available config files. """

    def test_configs_read(self):
        """ Test reading all available config files and filling null values. """
        root_dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "medali"))
        lib_path = os.path.join(root_dirpath, "lib")

        product_names = os.listdir(lib_path)
        cfg_filepaths = []
        for product_name in product_names:
            product_dirpath = os.path.join(lib_path, product_name)
            cfg_filepaths.extend(glob.glob(os.path.join(product_dirpath, "*.ini")))

        for cfg_filepath in cfg_filepaths:
            metadata = MetaData.from_cfg_file({}, cfg_filepath)
            self.assertEqual(metadata._meta.keys(), metadata._ref_meta['Metadata'].keys())


class MetadataTest(unittest.TestCase):
    """
    Test reading, checking and converting metadata with respect to the reference metadata
    and other metadata classes.

    """

    def setUp(self):
        """ Reads template config metadata file and creates a `MetaData` instance. """
        test_data_dirpath = os.path.join(os.path.dirname(__file__), "test_data")
        cfg_filepath = os.path.join(test_data_dirpath, "cfg_template.ini")
        self.cfg_filepath = cfg_filepath
        self.metadata = MetaData.from_cfg_file({}, cfg_filepath)
        self.metadata['datetime_type'] = datetime.datetime(2020, 12, 12, 12, 20, 10)
        self.metadata['boolean_type'] = False
        self.metadata['number_type'] = 1.2
        self.metadata['integer_type'] = 1
        self.metadata['string_general'] = 'abc'
        self.metadata['string_list'] = 'V3'
        self.metadata['string_pattern'] = 'Pattern01'

    def test_set_metadata_attributes(self):
        """ Tests metadata item setting. """
        metadata_should = {'datetime_type': '2020-12-12 12:20:10',
                           'string_pattern': 'Pattern01',
                           'string_general': 'abc',
                           'integer_type': '1',
                           'number_type': '1.2',
                           'string_list': 'V3',
                           'boolean_type': 'False'}

        self.assertDictEqual(metadata_should, self.metadata._meta)

    def test_get_metadata_attributes(self):
        """ Tests value decoding when accessing metadata attributes. """

        assert self.metadata['datetime_type'] == datetime.datetime(2020, 12, 12, 12, 20, 10)
        assert not self.metadata['boolean_type']
        assert self.metadata['number_type'] == 1.2
        assert self.metadata['integer_type'] == 1
        assert self.metadata['string_general'] == 'abc'
        assert self.metadata['string_list'] == 'V3'
        assert self.metadata['string_pattern'] == 'Pattern01'

    def test_expected_values(self):
        """ Tests checking of external metadata. """

        metadata = MetaData.from_cfg_file({}, self.cfg_filepath)
        metadata['datetime_type'] = '2020-12-12 12:20:10'
        metadata['string_pattern'] = 'null'
        metadata['integer_type'] = '1'
        try:
            metadata['number_type'] = 'haha'
            assert False
        except ValueError:
            assert True
        try:
            metadata['string_list'] = 'V5'
            assert False
        except ValueError:
            assert True
        metadata['boolean_type'] = 'False'

    def test_and(self):
        """ Tests AND operation between two `MetaData` instances. """

        ref_dtypes = {'datetime_type': 'datetime',
                      'boolean_type': 'boolean',
                      'number_type': 'number',
                      'integer_type': 'integer'}
        ref_metadata = dict()
        ref_metadata['Metadata'] = ref_dtypes
        sec_metadata = MetaData({}, ref_metadata)

        metadata_should = {'datetime_type': '2020-12-12 12:20:10',
                           'integer_type': '1',
                           'number_type': '1.2',
                           'boolean_type': 'False'}

        common_metadata = self.metadata & sec_metadata

        self.assertDictEqual(metadata_should, common_metadata._meta)


if __name__ == '__main__':
    unittest.main()

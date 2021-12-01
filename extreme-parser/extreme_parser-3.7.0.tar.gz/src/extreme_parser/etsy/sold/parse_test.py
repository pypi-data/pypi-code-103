from unittest import TestCase

from extreme_parser.etsy.sold.parse import parse_product_ids
from extreme_parser.util import read_file


class ParseTest(TestCase):
    def test_parse_product_ids(self):
        self.assertEqual([
            '862998032', '1044895494', '862998032', '862998032',
            '1079076535', '1044895494', '1044895494', '1044895494',
            '862998032', '862998032', '862998032', '862998032',
            '862998032', '862998032', '862998032', '1079076535',
            '1044895494', '862998032', '1106258351', '1106258351',
            '862998032', '862998032', '862998032', '862998032'
        ], parse_product_ids(read_file("./testdata/1.html")))

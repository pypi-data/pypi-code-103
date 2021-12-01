from unittest import TestCase

from extreme_parser.amazon.option.model import Option
from extreme_parser.amazon.option.parse import parse
from extreme_parser.util import read_file


class ParseTest(TestCase):
    def test_parse(self):
        self.assertEqual([
            Option(
                sold="ganweiganxiangshangmao",
                sold_url_rel="/gp/aag/main?ie=UTF8&seller=AXVBSX7024YAN&isAmazonFulfilled=0&asin=B096F45ST8&ref_=olp_merch_name_1"
            )
        ], parse(read_file("./testdata/1.html")))

# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import unittest
from ibm_wos_utils.joblib.utils.param_utils import *


class TestParamUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def test_get_boolean_value(self):
        assert get_boolean_value("true") is True
        assert get_boolean_value("True") is True
        assert get_boolean_value(True) is True
        assert get_boolean_value("False") is False
        assert get_boolean_value("false") is False
        assert get_boolean_value(False) is False
        assert get_boolean_value("") is False
        assert get_boolean_value(None) is False


if __name__ == '__main__':
    unittest.main()

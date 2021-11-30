# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import unittest
from ibm_wos_utils.joblib.exceptions.client_errors import *
from ibm_wos_utils.joblib.utils.validator import *


class TestValidator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def test_validate_type(self):
        try:
            validate_type("instance_id", None, str, is_mandatory=True)
        except Exception as e:
            assert isinstance(e, MissingValueError)
        try:
            validate_type("instance_id", 100, str, is_mandatory=True)
        except Exception as e:
            assert isinstance(e, UnexpectedTypeError)
        try:
            validate_type("job_payload", "payload", dict, is_mandatory=True)
        except Exception as e:
            assert isinstance(e, UnexpectedTypeError)
        is_valid_type = validate_type(
            "instance_name", "test_instance", str, is_mandatory=True)
        assert is_valid_type is True

    def test_validate_resource_id(self):
        try:
            validate_resource_id("instance_id", None)
        except Exception as e:
            assert isinstance(e, MissingValueError)
        try:
            validate_resource_id("instance_id", "test_id")
        except Exception as e:
            assert isinstance(e, InvalidInputError)
        is_valid_id = validate_resource_id(
            "job_id", "9588a87f-4876-4a95-a967-d3566f7e8db8")
        assert is_valid_id is True


if __name__ == '__main__':
    unittest.main()

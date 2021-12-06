import os
from unittest import TestCase, mock
from nasdaqdatalink.api_config import *

TEST_KEY_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".nasdaq-config", "testkeyfile")

class ApiConfigTest(TestCase):
    @mock.patch.dict(os.environ, {"NASDAQ_DATA_LINK_API_KEY": "setinenv"})
    def test_read_key_when_environment_variable_set(self):
        read_key()
        self.assertEqual(ApiConfig.api_key, "setinenv")
        print(ApiConfig.api_key)

    def test_read_key_when_environment_variable_not_set(self):
        save_key("keyforfile", TEST_KEY_FILE)
        #read_key()
        #print("HOW: ", ApiConfig.api_key)
        #self.assertEqual(ApiConfig.api_key, None)
        print(TEST_KEY_FILE)

import json
import logging
import logging.config
import pathlib
import unittest
import copy

from ibm_wos_utils.joblib.utils.log_formatter import SensitiveDataFormatter


class TestLog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def get_logger(self):
        clients_dir = pathlib.Path(__file__).parent.absolute()
        with open(str(clients_dir) + "/../jobs/logging.json", "r") as f:
            log_config = json.load(f)
        logging.config.dictConfig(log_config)
        for h in logging.root.handlers:
            h.setFormatter(SensitiveDataFormatter(
                h.formatter))

        return logging.getLogger(__name__)

    def test_logger(self):
        logger = self.get_logger()
        # Test logging hive related sensitive info
        params = {"storage": {"type": "hive",
                              "connection": {"metastore_url": "thrift://sample.host.com:9083", "location_type": "metastore"}}}
        original_params = copy.deepcopy(params)
        logger.info('AIOS base job parameters: {}'.format(params))
        # Verifying that original params dict is not modified after logging
        for field in params:
            assert params[field] == original_params[field]

        # Test logging jdbc related sensitive info
        params = {"storage": {"type": "jdbc",
                              "connection": {"jdbc_url": "jdbc:db2//host:50001/DB", "use_ssl": True, "certificate": "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURFakNDQWZxZ0F3SUJBZ0lKQVA1S0R3ZTNCTkxiTUEwR0NTcUdTSWIzRFFFQkN3VUFNQjR4SERBYUJnTlYKQkFNTUUwbENUU0JEYkc5MVpDQkVZWFJoWW1GelpYTXdIaGNOTWpBd01qSTVNRFF5TVRBeVdoY05NekF3TWpJMgpNRFF5TVRBeVdqQWVNUnd3R2dZRFZRUUREQk5KUWswZ1EyeHZkV1FnUkdGMFlXSmhjMlZ6TUlJQklqQU5CZ2txCmhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBdXUvbitpWW9xdkdGNU8xSGpEalpsK25iYjE4UkR4ZGwKTzRUL3FoUGMxMTREY1FUK0plRXdhdG13aGljTGxaQnF2QWFMb1hrbmhqSVFOMG01L0x5YzdBY291VXNmSGR0QwpDVGcrSUsxbjBrdDMrTHM3d1dTakxqVE96N3M3MlZUSU5yYmx3cnRIRUlvM1JWTkV6SkNHYW5LSXdZMWZVSUtrCldNMlR0SDl5cnFsSGN0Z2pIUlFmRkVTRmlYaHJiODhSQmd0amIva0xtVGpCaTFBeEVadWNobWZ2QVRmNENOY3EKY21QcHNqdDBPTnI0YnhJMVRyUWxEemNiN1hMSFBrWW91SUprdnVzMUZvaTEySmRNM1MrK3labFZPMUZmZkU3bwpKMjhUdGJoZ3JGOGtIU0NMSkJvTTFSZ3FPZG9OVm5QOC9EOWZhamNNN0lWd2V4a0lSOTNKR1FJREFRQUJvMU13ClVUQWRCZ05WSFE0RUZnUVVlQ3JZanFJQzc1VUpxVmZEMDh1ZWdqeDZiUmN3SHdZRFZSMGpCQmd3Rm9BVWVDclkKanFJQzc1VUpxVmZEMDh1ZWdqeDZiUmN3RHdZRFZSMFRBUUgvQkFVd0F3RUIvekFOQmdrcWhraUc5dzBCQVFzRgpBQU9DQVFFQUkyRTBUOUt3MlN3RjJ2MXBqaHV4M0lkWWV2SGFVSkRMb0tPd0hSRnFSOHgxZ2dRcGVEcFBnMk5SCkx3R08yek85SWZUMmhLaWd1d2orWnJ5SGxxcHlxQ0pLOHJEU28xZUVPekIyWmE2S1YrQTVscEttMWdjV3VHYzMKK1UrVTFzTDdlUjd3ZFFuVjU0TVU4aERvNi9sVHRMRVB2Mnc3VlNPSlFDK013ejgrTFJMdjVHSW5BNlJySWNhKwozM0wxNnB4ZEttd1pLYThWcnBnMXJ3QzRnY3dlYUhYMUNEWE42K0JIbzhvWG5YWkh6UG91cldYS1BoaGdXZ2J5CkNDcUdIK0NWNnQ1eFg3b05NS3VNSUNqRVZndnNLWnRqeTQ5VW5iNVZZbHQ0b1J3dTFlbGdzRDNjekltbjlLREQKNHB1REFvYTZyMktZZE4xVkxuN3F3VG1TbDlTU05RPT0KLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo=",
                                             "location_type": "jdbc"}, "credentials": {"username": "username", "password": "password"}}}
        original_params = copy.deepcopy(params)
        logger.warning(params)
        for field in params:
            assert params[field] == original_params[field]

    def test_mask_sensitive_fields(self):
        fields_to_mask = ["metastore_url", "username",
                          "password", "certificate", "apikey"]
        log_formatter = SensitiveDataFormatter(None)
        params = {"storage": {"type": "hive",
                              "connection": {"metastore_url": "thrift://sample.host.com:9083", "location_type": "metastore"}}}
        message = "AIOS base job parameters: {}".format(params)
        formatted_message = log_formatter.mask_sensitive_fields(
            message, fields_to_mask)
        for field in fields_to_mask:
            if field in message:
                assert "'{}': '***'".format(field) in formatted_message
        assert formatted_message == "AIOS base job parameters: {'storage': {'type': 'hive', 'connection': {'metastore_url': '***', 'location_type': 'metastore'}}}"

        params = {"storage": {"type": "jdbc",
                              "connection": {"jdbc_url": "jdbc:db2//host:50001/DB", "use_ssl": True, "certificate": "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURFakNDQWZxZ0F3SUJBZ0lKQVA1S0R3ZTNCTkxiTUEwR0NTcUdTSWIzRFFFQkN3VUFNQjR4SERBYUJnTlYKQkFNTUUwbENUU0JEYkc5MVpDQkVZWFJoWW1GelpYTXdIaGNOTWpBd01qSTVNRFF5TVRBeVdoY05NekF3TWpJMgpNRFF5TVRBeVdqQWVNUnd3R2dZRFZRUUREQk5KUWswZ1EyeHZkV1FnUkdGMFlXSmhjMlZ6TUlJQklqQU5CZ2txCmhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBdXUvbitpWW9xdkdGNU8xSGpEalpsK25iYjE4UkR4ZGwKTzRUL3FoUGMxMTREY1FUK0plRXdhdG13aGljTGxaQnF2QWFMb1hrbmhqSVFOMG01L0x5YzdBY291VXNmSGR0QwpDVGcrSUsxbjBrdDMrTHM3d1dTakxqVE96N3M3MlZUSU5yYmx3cnRIRUlvM1JWTkV6SkNHYW5LSXdZMWZVSUtrCldNMlR0SDl5cnFsSGN0Z2pIUlFmRkVTRmlYaHJiODhSQmd0amIva0xtVGpCaTFBeEVadWNobWZ2QVRmNENOY3EKY21QcHNqdDBPTnI0YnhJMVRyUWxEemNiN1hMSFBrWW91SUprdnVzMUZvaTEySmRNM1MrK3labFZPMUZmZkU3bwpKMjhUdGJoZ3JGOGtIU0NMSkJvTTFSZ3FPZG9OVm5QOC9EOWZhamNNN0lWd2V4a0lSOTNKR1FJREFRQUJvMU13ClVUQWRCZ05WSFE0RUZnUVVlQ3JZanFJQzc1VUpxVmZEMDh1ZWdqeDZiUmN3SHdZRFZSMGpCQmd3Rm9BVWVDclkKanFJQzc1VUpxVmZEMDh1ZWdqeDZiUmN3RHdZRFZSMFRBUUgvQkFVd0F3RUIvekFOQmdrcWhraUc5dzBCQVFzRgpBQU9DQVFFQUkyRTBUOUt3MlN3RjJ2MXBqaHV4M0lkWWV2SGFVSkRMb0tPd0hSRnFSOHgxZ2dRcGVEcFBnMk5SCkx3R08yek85SWZUMmhLaWd1d2orWnJ5SGxxcHlxQ0pLOHJEU28xZUVPekIyWmE2S1YrQTVscEttMWdjV3VHYzMKK1UrVTFzTDdlUjd3ZFFuVjU0TVU4aERvNi9sVHRMRVB2Mnc3VlNPSlFDK013ejgrTFJMdjVHSW5BNlJySWNhKwozM0wxNnB4ZEttd1pLYThWcnBnMXJ3QzRnY3dlYUhYMUNEWE42K0JIbzhvWG5YWkh6UG91cldYS1BoaGdXZ2J5CkNDcUdIK0NWNnQ1eFg3b05NS3VNSUNqRVZndnNLWnRqeTQ5VW5iNVZZbHQ0b1J3dTFlbGdzRDNjekltbjlLREQKNHB1REFvYTZyMktZZE4xVkxuN3F3VG1TbDlTU05RPT0KLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo=",
                                             "location_type": "jdbc"}, "credentials": {"username": "user", "password": "passw0rd"}}}
        message = "AIOS base job parameters: {}".format(params)
        formatted_message = log_formatter.mask_sensitive_fields(
            message, fields_to_mask)

        for field in fields_to_mask:
            if field in message:
                assert "'{}': '***'".format(field) in formatted_message

        assert formatted_message == "AIOS base job parameters: {'storage': {'type': 'jdbc', 'connection': {'jdbc_url': 'jdbc:db2//host:50001/DB', 'use_ssl': True, 'certificate': '***', 'location_type': 'jdbc'}, 'credentials': {'username': '***', 'password': '***'}}}"

        # Logging with json.dumps()
        formatted_message = log_formatter.mask_sensitive_fields(
            json.dumps(params), fields_to_mask)
        assert formatted_message == '{"storage": {"type": "jdbc", "connection": {"jdbc_url": "jdbc:db2//host:50001/DB", "use_ssl": true, "certificate": "***", "location_type": "jdbc"}, "credentials": {"username": "***", "password": "***"}}}'

        # Test with empty/none value in sensitive fields
        params = {"storage": {"type": "jdbc",
                              "connection": {"jdbc_url": "jdbc:db2//host:50001/DB", "use_ssl": True, "certificate": "",
                                             "location_type": "jdbc"}, "credentials": {"username": "username", "password": None}}}
        message = "AIOS base job parameters: {}".format(params)
        formatted_message = log_formatter.mask_sensitive_fields(
            message, fields_to_mask)
        assert formatted_message == "AIOS base job parameters: {'storage': {'type': 'jdbc', 'connection': {'jdbc_url': 'jdbc:db2//host:50001/DB', 'use_ssl': True, 'certificate': '', 'location_type': 'jdbc'}, 'credentials': {'username': '***', 'password': None}}}"

        # check plain message
        message = "Sample log message"
        formatted_message = log_formatter.mask_sensitive_fields(
            message, fields_to_mask)
        assert formatted_message == message

if __name__ == '__main__':
    unittest.main()

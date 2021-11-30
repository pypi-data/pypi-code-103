# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import unittest
from ibm_wos_utils.joblib.utils.joblib_utils import JoblibUtils
from ibm_wos_utils.joblib.utils.jobstatus_utils import get_common_job_status


class TestJoblibUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def test_get_iae_spark_instance_details(self):
        credentials = {
            "connection": {
                "endpoint": "https://namespace1-cpd-namespace1.apps.islapr25.os.fyre.ibm.com/ae/spark/v2/033f1c3a124f4897b3a60f25bc6603b6/v2/jobs",
                "location_type": "cpd_iae",
                "instance_id": "BatchTestingInstance",
                "volume": "aios"
            },
            "credentials": {
                "username": "admin",
                "password": None,
                "apikey": "apikey"
            }
        }
        spark_instance_details = JoblibUtils.get_spark_instance_details(
            credentials)
        assert 'endpoint' in spark_instance_details, "Endpoint is missing"
        assert 'username' in spark_instance_details, "Username is missing"
        assert 'apikey' in spark_instance_details, "Apikey is missing"
        assert 'location_type' in spark_instance_details, "location_type is missing"
        assert 'instance_id' in spark_instance_details, "instance_id is missing"
        assert 'volume' in spark_instance_details, "volume is missing"

    def test_get_remote_spark_instance_details(self):
        credentials = {
            'spark_credentials': {
                'url': 'http://localhost:5000',
                'username': 'openscale',
                'password': 'test_password'
            }
        }
        spark_instance_details = JoblibUtils.get_spark_instance_details(
            credentials)
        assert 'endpoint' in spark_instance_details, "Endpoint is missing"
        assert 'username' in spark_instance_details, "Username is missing"
        assert 'password' in spark_instance_details, "Password is missing"
        
    def test_job_status(self):
        
        #Running status
        assert "running" == get_common_job_status("running").value
        assert "running" == get_common_job_status("starting").value
        assert "running" == get_common_job_status("waiting").value
        
        #Finished status
        assert "finished" == get_common_job_status("finished").value
        assert "finished" == get_common_job_status("success").value
        
        #Faile status
        assert "failed" == get_common_job_status("error").value
        assert "failed" == get_common_job_status("dead").value
        assert "failed" == get_common_job_status("killed").value
        assert "failed" == get_common_job_status("failed").value
        assert "failed" == get_common_job_status("stopped").value
        
        #Unknown status
        assert "unknown" == get_common_job_status("unknown").value        


if __name__ == '__main__':
    unittest.main()

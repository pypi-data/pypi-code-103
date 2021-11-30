# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import unittest
from ibm_wos_utils.joblib.clients.engine_client import EngineClient
from ibm_wos_utils.joblib.utils import constants
from ibm_wos_utils.joblib.exceptions.client_errors import *
from ibm_wos_utils.sample.batch.jobs.sample_spark_job import SampleJob
from pathlib import Path
import json


class TestRemoteJobRun(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_remote_job(self):
        '''
        credentials = {
            'spark_credentials': {
                'url': 'http://9.199.147.19:5000',
                'username': 'openscale',
                'password': 'passw0rd'
            }
        }
        '''

        credentials = {
            'spark_credentials': {
                'url': 'http://localhost:5000',
                'username': 'openscale',
                'password': 'passw0rd'
            }
        }

        '''
        credentials = {
            'spark_credentials': {
                'url': 'http://wos-spark-wrapper-route.apps.islapr35.os.fyre.ibm.com',
                'username': 'openscale',
                'password': 'passw0rd'
            }
        }
        '''
        rc = EngineClient(credentials)

        # my_files = ['/Users/kishorepatel/_Work/2020/BatchScoring/hdfs_job_testing/first_spark_job.py']
        my_files = ['/Users/kishorepatel/Downloads/debiased.json']
        # my_files = []

        subscription = {
            "entity": {
                "analytics_engine": {
                    "type": "spark",
                    "integration_reference": {
                        "integrated_system_id": "4585f9a2-2712-4c77-9199-f33e0bf3e766",
                        "external_id": "id of scottda-new-spark"
                    },
                    "credentials": {
                        "livy_url": "http://localhost:8998"
                    }
                },
                "data_sources": [
                    {
                        "type": "drift",
                        "connection": {
                            "type": "hive",
                            "integration_reference": {
                                "integrated_system_id": "5fe50f25-ea5a-42bf-98fa-db1ee3d929fe",
                                "external_id": "id of scottda-new-hive"
                            },
                            "credentials": {
                                "host": "localhost",
                                "port": "9083",
                                "credentials": {
                                    "host": "localhost",
                                    "port": "9083",
                                    "credentials": {
                                        "host": "localhost",
                                        "port": "9083"
                                    }
                                }
                            }
                        },
                        "database_name": "subscription_d1642521",
                        "table_name": "drifted_transactions"
                    }
                ]
            },
            "metadata": {
                "created_at": "2020-08-10T08:56:38.885Z",
                "created_by": "IBMid-2700031PFG",
                "crn": "crn:v1:bluemix:public:aiopenscale:us-south:a/1c35533e221430a71c1352b1b4ade87e:30c76795-b9b9-4591-b9b8-6addd8db0217:subscription:d1642521-94a9-4382-8c6a-19677c3379d0",
                "id": "d1642521-94a9-4382-8c6a-19677c3379d0",
                "modified_at": "2020-08-10T08:57:02.931Z",
                "modified_by": "IBMid-2700031PFG",
                "url": "/v2/subscriptions/d1642521-94a9-4382-8c6a-19677c3379d0"
            }
        }

        deployment = {
            "name": "My_regression_model_deployment",
            "id": 999999
        }
        job_params = {
            "arguments": {
                "model_type": "regression",
                "label_col": 'Amount',
                "monitoring_run_id": "run_uuid_dkaECO02DckdTD4g123asebdded",
                "subscription_id": "sub_uuid_dkaECO02DckdTD4g123asebdded",
                "model_info": {
                    "name": "My_regression_model",
                    "id": 888888,
                    "depl": deployment
                },
                "subscription": subscription
            },
            "spark_settings": {
                "max_num_executors": "2",
                "min_num_executors": "1",
                "executor_cores": "2",
                "executor_memory": "1",
                "driver_cores": "2",
                "driver_memory": "1"
            },
            "dependency_zip": []
        }

        job_response = rc.engine.run_job(job_name="sample_job",
                                         job_class=SampleJob,
                                         job_args=job_params,
                                         data_file_list=my_files,
                                         background=False)

        job_id = job_response["id"]
        job_state = job_response["state"]
        output_file_path = job_response["output_file_path"]

        print(" Job id: ", job_id)
        print(" Job status: ", job_state)
        print(" output path: ", output_file_path)

        print("JOB STATUS : ", rc.engine.get_job_status(job_id))

        print("========== Get File output ===============")
        data = rc.engine.get_file(output_file_path + "/output.json")
        json_data = json.loads(data.decode("utf-8"))
        print(json_data)

        print('============Exception =====================')
        data = rc.engine.get_exception(output_file_path=output_file_path)
        print(data)

        print('============Logging =====================')
        data = rc.engine.get_file(output_file_path + "/job.log")
        log_data = str(data, 'utf-8')
        print(log_data)
        f = open("my_job_output.log", "w")
        f.write(log_data)
        f.close()
        rc.engine.kill_job(job_id)

    def test_upload_artifacts_with_retry(self):
        credentials = {
            "connection": {
                "endpoint": "http://aizawl.fyre.ibm.com:5010",
                "location_type": "custom"
            },
            "credentials": {
                # Enter the details before running the test
                "username": "openscale_user1",
                "password": "passw0rd"
            }
        }
        client = EngineClient(credentials)

        # Upload the main job
        import pathlib
        clients_dir = str(pathlib.Path(__file__).parent.absolute())
        file_list = [str(clients_dir) + "/../main_job.py"]
        # Trying to upload to invalid location, so the method should retry and fail.
        try:
            client.engine.upload_job_artifacts(file_list, "/ppm")
        except ClientError as ex:
            assert "Max retries exceeded" in str(ex)

    def test_download_directory(self):
        credentials = {
            "spark_credentials": {
                "url": "http://localhost:5000",
                "username": "",
                "password": ""
            }
        }
        client = EngineClient(credentials)
        try:
            client.engine.download_directory("test")
        except Exception as e:
            raise e


if __name__ == '__main__':
    unittest.main()
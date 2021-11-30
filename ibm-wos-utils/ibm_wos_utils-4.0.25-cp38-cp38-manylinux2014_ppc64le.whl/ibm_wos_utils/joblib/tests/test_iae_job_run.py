# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import json
import unittest
from ibm_wos_utils.joblib.clients.engine_client import EngineClient
from ibm_wos_utils.joblib.clients.iae_instance_client import IAEInstanceClient
from ibm_wos_utils.joblib.clients.iae_engine_client import IAEEngineClient
from ibm_wos_utils.joblib.clients.token_client import TokenClient
from ibm_wos_utils.joblib.exceptions.client_errors import *
from ibm_wos_utils.sample.batch.jobs.sample_spark_job import SampleJob
import os
from time import sleep
from pathlib import Path


class TestIAEJobRun(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_iae_job(self):
        credentials = {
            "connection": {
                "endpoint": "https://namespace1-cpd-namespace1.apps.islnov15.os.fyre.ibm.com/ae/spark/v2/6349e41f19c04d64af1aaab1c4a08a53/v2/jobs",
                "location_type": "cpd_iae",
                "display_name": "BatchIAE",
                "instance_id": "6349e41f19c04d64af1aaab1c4a08a53",
                "volume": "wos-batch-support-volume"
            },
            "credentials": {
                # Enter the details before running the test
                "username": "",
                "apikey": ""
            }
        }
        rc = EngineClient(credentials)
        job_params = {
            "spark_settings": {
                "max_num_executors": 4,
                "executor_cores": 1,
                "executor_memory": "1",
                "driver_cores": 1,
                "driver_memory": "1"
            },
            # "mount_path" :"/test_path",
            "arguments": {
                "monitoring_run_id": "fairness_run",
                "subscription": {
                    "subscription_id": "test_sub_id",
                    "asset_properties": {
                        "output_data_schema": {
                            "type": "struct",
                            "fields": []
                        }
                    }

                },
                "deployment": {
                    "deployment_id": "test_dep_id",
                    "scoring_url": "https://us-south.ml.cloud.ibm.com/test_dep_id/online"
                }
            }
        }
        job_response = rc.engine.run_job(job_name="sample_job",
                                         job_class=SampleJob,
                                         job_args=job_params,
                                         background=False)
        print('Job ID: ', job_response['id'])
        status = job_response['state']
        print('Status: ', status)
        assert status == 'finished'
        print('Output file path: ', job_response['output_file_path'])
        # Get the output file
        sleep(5)
        job_output = rc.engine.get_file(
            job_response['output_file_path'] + "/output.json").decode('utf-8')
        print(json.loads(job_output))

    # Copy drift evaluation job in drift->batch->jobs folder before running this test
    def test_drift_job(self):
        my_files = ["/Users/prashant/Downloads/drift.tar.gz"]
        credentials = {
            "connection": {
                "endpoint": "https://namespace1-cpd-namespace1.apps.islnov03.os.fyre.ibm.com/ae/spark/v2/5cdaa2b2af3a49ae874e1e98b825cecd/v2/jobs",
                "location_type": "cpd_iae",
                "display_name": "BatchTestSpark",
                "instance_id": "1604315480426432",
                "volume": "openscale-volume"
            },
            "credentials": {
                # Enter the details before running the test
                "username": "",
                "apikey": ""
            }
        }
        rc = EngineClient(credentials)

        job_params = {
            "arguments": {
                "monitoring_run_id": "test_monitor_run_id",
                "feature_columns": [
                    "CheckingStatus",
                    "LoanDuration",
                    "CreditHistory",
                    "LoanPurpose",
                    "LoanAmount",
                    "ExistingSavings",
                    "EmploymentDuration",
                    "InstallmentPercent",
                    "Sex",
                    "OthersOnLoan",
                    "CurrentResidenceDuration",
                    "OwnsProperty",
                    "Age",
                    "InstallmentPlans",
                    "Housing",
                    "ExistingCreditsCount",
                    "Job",
                    "Dependents",
                    "Telephone",
                    "ForeignWorker"
                ],
                "record_id_column": "scoring_id",
                "record_timestamp_column": "scoring_timestamp",
                "model_drift": {
                    "enabled": True
                },
                "data_drift": {
                    "enabled": True
                },
                "storage": {
                    "type": "hive",
                    "connection": {
                        "location_type": "metastore",
                        "metastore_url": "thrift://shillong1.fyre.ibm.com:9083"
                    }
                },
                "tables": [
                    {
                        "type": "payload",
                        "database": "gcr_data",
                        "schema": None,
                        "table": "german_credit_payload_10k",
                        "columns": {
                            "fields": [],
                            "type": "struct"
                        }
                    },
                    {
                        "type": "drift",
                        "database": "ppm_data",
                        "schema": None,
                        "table": "drifted_transactions_table_ppm",
                        "columns": {
                            "fields": [],
                            "type": "struct"
                        }
                    }
                ]
            },
            "dependency_zip": [],
            "conf": {
                "spark.yarn.maxAppAttempts": 1
            },
            "spark_settings": {
                "max_num_executors": 4,
                "executor_cores": 1,
                "executor_memory": "1",
                "driver_cores": 1,
                "driver_memory": "1"
            }
        }

        from ibm_wos_utils.drift.batch.jobs.evaluation import DriftEvaluation
        job_response = rc.engine.run_job(
            job_name="Drift_Evaluation_Job", job_class=DriftEvaluation,
            job_args=job_params, data_file_list=my_files, background=False)

        job_id = job_response["id"]
        job_state = job_response["state"]
        output_file_path = job_response["output_file_path"]

        print("Job id: ", job_id)
        print("Job status: ", job_state)
        print("Job output path: ", output_file_path)

        job_status = rc.engine.get_job_status(job_id)
        print("Job status: ", job_status)

        if job_status.get("state") == "success":
            print("Drift evaluation successful.")
            data = rc.engine.get_file(output_file_path + "/metrics.json")
            print(data)
        elif job_status.get("state") == "dead":
            print("Drift evaluation failed.")
            data = rc.engine.get_exception(output_file_path=output_file_path)
            print(data)
        else:
            print("Unknown job status - {}!!!".format(job_status))

    def test_negative_scenarios(self):
        server_url = None
        token = "token"
        service_instance_name = "BatchTestingInstance"
        volume = "aios"
        try:
            client = IAEInstanceClient(
                server_url, service_instance_name, volume, token)
        except Exception as e:
            assert isinstance(e, MissingValueError)
        server_url = "https://namespace1-cpd-namespace1.apps.islapr25.os.fyre.ibm.com"
        # Enter the details before running the test
        username = ""
        apikey = ""
        token = TokenClient().get_iam_token_with_apikey(server_url, username, apikey)
        client = IAEInstanceClient(
            server_url, service_instance_name, volume, token)
        try:
            client.get_instance(name="invalid_instance")
        except Exception as e:
            assert isinstance(e, ObjectNotFoundError)
        try:
            client.get_volume("invalid_volume")
        except Exception as e:
            assert isinstance(e, ObjectNotFoundError)
        try:
            client.run_job("invalid_payload")
        except Exception as e:
            assert isinstance(e, UnexpectedTypeError)
        try:
            client.get_job_state("test_id")
        except Exception as e:
            assert isinstance(e, DependentServiceError)
        try:
            client.delete_job("test_id")
        except Exception as e:
            assert isinstance(e, DependentServiceError)
        try:
            client.get_job_logs("test_id")
        except Exception as e:
            assert isinstance(e, NotImplementedError)

    def test_get_non_existing_file(self):
        credentials = {
            "connection": {
                "endpoint": "https://namespace1-cpd-namespace1.apps.islnov04.cp.fyre.ibm.com/ae/spark/v2/06769dde70b44e42ab937df53e553bab/v2/jobs",
                "location_type": "cpd_iae",
                "display_name": "OpenScaleBatchSupport",
                "instance_id": "1605606238778296",
                "volume": "openscale-batch-test"
            },
            "credentials": {
                # Enter the details before running the test
                "username": "",
                "apikey": ""
            }
        }
        client = EngineClient(credentials)
        try:
            resp = client.engine.get_file('job').decode('utf-8')
            print(json.loads(resp))
        except (DependentServiceError, ClientError) as ex:
            assert "404" in str(ex)

    def test_get_directory(self):
        credentials = {
            "connection": {
                "endpoint": "https://namespace1-cpd-namespace1.apps.islnov15.os.fyre.ibm.com",
                "location_type": "cpd_iae",
                "display_name": "BatchTestingInstance",
                "instance_id": "1605118801425795",
                "volume": "openscale-volume1"
            },
            "credentials": {
                # Enter the details before running the test
                "username": "",
                "apikey": ""
            }
        }
        client = EngineClient(credentials)
        try:
            resp = client.engine.download_directory("test_neelima")
        except Exception as ex:
            raise ex

    def test_upload_artifacts_with_retry(self):
        credentials = {
            "connection": {
                "endpoint": "https://namespace1-cpd-namespace1.apps.islnov04.cp.fyre.ibm.com/ae/spark/v2/08bed6b4bd924d7aa0e1f040250dff42/v2/jobs",
                "location_type": "cpd_iae",
                "display_name": "OpenscaleBatchTest",
                "instance_id": "1606128504412970",
                "volume": "invalid"
            },
            "credentials": {
                # Enter the details before running the test
                "username": "",
                "apikey": ""
            }
        }
        client = EngineClient(credentials)
        # Upload the main job
        import pathlib
        clients_dir = str(pathlib.Path(__file__).parent.absolute())
        file_list = [str(clients_dir) + "/../main_job.py"]
        # Trying to upload to non-existing volume, so the method should retry and fail.
        try:
            client.engine.upload_job_artifacts(file_list, "/jobs")
        except MaxRetryError as ex:
            assert "Max retries exceeded" in str(ex)

    def test_iae_job_with_insufficient_resources(self):
        credentials = {
            "connection": {
                "endpoint": "https://namespace1-cpd-namespace1.apps.islnov15.os.fyre.ibm.com/ae/spark/v2/6349e41f19c04d64af1aaab1c4a08a53/v2/jobs",
                "location_type": "cpd_iae",
                "display_name": "BatchIAE",
                "instance_id": "6349e41f19c04d64af1aaab1c4a08a53",
                "volume": "wos-batch-support-volume"
            },
            "credentials": {
                # Enter the details before running the test
                "username": "",
                "apikey": ""
            }
        }
        rc = EngineClient(credentials)
        job_params = {
            "spark_settings": {
                "max_num_executors": 10,
                "executor_cores": 5,
                "executor_memory": "6",
                "driver_cores": 3,
                "driver_memory": "6"
            },
            "arguments": {
                "monitoring_run_id": "fairness_run",
                "subscription": {
                    "subscription_id": "test_sub_id",
                    "asset_properties": {
                        "output_data_schema": {
                            "type": "struct",
                            "fields": []
                        }
                    }

                },
                "deployment": {
                    "deployment_id": "test_dep_id",
                    "scoring_url": "https://us-south.ml.cloud.ibm.com/test_dep_id/online"
                }
            }
        }
        try:
            job_response = rc.engine.run_job(
                job_name="sample_job",
                job_class=SampleJob,
                job_args=job_params,
                background=False)
            assert False, "Job submission should return ServiceUnavailableError."
        except ServiceUnavailableError as e:
            assert e.message == "The available resource quota(CPU 20 cores, Memory 80g) is less than the resource quota requested by the job(CPU 53 cores, Memory 66g). Please increase the resource quota and retry."

if __name__ == '__main__':
    unittest.main()

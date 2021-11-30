# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2020
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from http import HTTPStatus
import json
import os
import pathlib
import time
import uuid
from pathlib import Path
from string import Template

from ibm_wos_utils.joblib.clients.engine import Client
from ibm_wos_utils.joblib.exceptions.client_errors import *
from ibm_wos_utils.joblib.utils import constants
from ibm_wos_utils.joblib.utils.constants import UPLOAD_FILE_RETRY_COUNT, UPLOAD_FILE_RETRY_STATUS_CODES
from ibm_wos_utils.joblib.utils.joblib_utils import JoblibUtils
from ibm_wos_utils.joblib.utils.param_utils import get
from ibm_wos_utils.joblib.utils.rest_util import RestUtil
from ibm_wos_utils.joblib.utils.validator import validate_type
from requests.auth import HTTPBasicAuth


class RemoteEngineClient(Client):

    def __init__(self, server_url, username, password):
        # Validate required parameters
        validate_type("server_url", server_url, str, True)
        validate_type("username", username, str, True)
        validate_type("password", password, str, True)

        self.server_url = server_url
        self.username = username
        self.password = password
        self.jobs_url = "/openscale/spark_wrapper/v1/jobs"
        self.files_url = "/openscale/spark_wrapper/v1/files"

        self.HDFS_BASE = "$hdfs/"

    def upload_job_artifacts(self, file_list, target_folder, overwrite=True):
        # Validate incoming parameters
        validate_type("file_list", file_list, list, True)
        validate_type("target_folder", target_folder, str, True)

        basic_auth = HTTPBasicAuth(self.username, self.password)
        for my_file in file_list:
            file_name = Path(my_file).name
            url = "{}{}?overwrite={}&file={}".format(
                self.server_url, self.files_url, overwrite, target_folder + "/" + file_name)

            # Retrying with backoff
            delay = 5 # Initial delay for retry
            backoff_factor = 2
            for i in range(UPLOAD_FILE_RETRY_COUNT):
                with open(my_file, "rb") as file_stream:
                    file_data = file_stream.read()
                    response = RestUtil.request().put(url=url, auth=basic_auth, headers={
                        "Content-Type": "application/octet-stream"}, data=bytes(file_data))
                if not response.ok:
                    # If status code is one of [not_found, gateway_timeout] then retry the operation
                    status_code = response.status_code
                    if status_code in UPLOAD_FILE_RETRY_STATUS_CODES:
                        if i == UPLOAD_FILE_RETRY_COUNT-1:
                            # Uploading failed even after retrying
                            raise MaxRetryError("upload_file", error=response.text)
                        # Retry with backoff
                        print("\nThe operation upload_file failed with status {}, retrying in {} seconds.".format(status_code, delay))
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        raise DependentServiceError("Uploading of file {} failed. Error: ".format(
                            my_file, response.text), response)
                else:
                    # If response is successful, then breaking the loop
                    break
        return response.json()

    def run_job(self, job_name, job_class, job_args, data_file_list=None, background=True):
        job_class_path = job_class.__module__ + "." + job_class.__name__
        # Validate incoming parameters
        validate_type("job_name", job_name, str, True)
        validate_type("job_class", job_class_path, str, True)
        validate_type("job_args", job_args, dict, True)
        validate_type("data_file_list", data_file_list, list, False)

        basic_auth = HTTPBasicAuth(self.username, self.password)

        # Push entry job if it is not already pushed
        entry_job_path = self.HDFS_BASE + constants.ENTRY_JOB_BASE_FOLDER
        # Upload the main job
        clients_dir = str(pathlib.Path(__file__).parent.absolute())
        file_list = [str(clients_dir) + "/../" + constants.ENTRY_JOB_FILE]
        self.upload_job_artifacts(file_list, entry_job_path)

        # Compose Job payload
        json_payload, data_path, output_file_path = self.__get_job_payload(
            job_name, job_class_path, job_args)

        if data_file_list is not None and len(data_file_list) > 0:
            self.upload_job_artifacts(data_file_list, data_path)

        # Run the job
        url = "{}/{}?background_mode={}".format(
            self.server_url, self.jobs_url, background)
        response = RestUtil.request().post(
            url=url, auth=basic_auth, json=json_payload, headers={"Content-Type": "application/json"})
        if not response.ok:
            raise DependentServiceError(
                "Failed to run job. Error: {}".format(response.text), response)
        job_response = response.json()
        job_response["output_file_path"] = output_file_path
        return job_response

    def get_job_status(self, job_id):
        # Validate incoming parameters
        validate_type("job_id", job_id, int, True)

        basic_auth = HTTPBasicAuth(self.username, self.password)
        url = "{}{}/{}/status?".format(self.server_url, self.jobs_url, job_id)
        response = RestUtil.request().get(url=url, auth=basic_auth, headers={})
        if not response.ok:
            raise DependentServiceError("Unable to get the status of job_id . Error {}".format(
                job_id, response.text), response)
        return response.json()

    def get_file(self, file_path):
        # Validate incoming parameters
        validate_type("file_path", file_path, str, True)

        basic_auth = HTTPBasicAuth(self.username, self.password)
        url = "{}{}?file={}".format(self.server_url, self.files_url, file_path)
        response = RestUtil.request().get(url=url, auth=basic_auth, headers={})
        if not response.ok:
            raise DependentServiceError("Unable to get the file {}. Error {}".format(
                file_path, response.text), response)
        return response.content

    def get_exception(self, output_file_path):
        data = self.get_file(output_file_path + "/exception.json")
        return json.loads(data.decode("utf-8"))

    def get_job_logs(self, job_id):
        # Validate incoming parameters
        validate_type("job_id", job_id, int, True)
        raise NotImplementedError("kill_job")

    def delete_job_artifacts(job_id):
        # Validate incoming parameters
        validate_type("job_id", job_id, int, True)
        raise NotImplementedError("kill_job")
    
    def kill_job(self, job_id):
        #validate_type("job_id", job_id, int, True)
        raise NotImplementedError("kill_job")

    def __get_job_payload(self, job_name, job_class, param_dict):
        if "arguments" not in param_dict:
            param_dict["arguments"] = {}
        subscription_id = get(param_dict, "arguments.subscription_id") or str(uuid.uuid4())
        run_id = get(param_dict, "arguments.monitoring_run_id") or str(uuid.uuid4())

        data_path = job_name + "/" + subscription_id + "/data"

        data_path = self.HDFS_BASE + data_path
        param_dict["arguments"]["data_file_path"] = data_path
        
        output_file_path = data_path[0:-5] + "/output/" + run_id
        param_dict["arguments"]["output_file_path"] = output_file_path

        arg_str = json.dumps(param_dict["arguments"])
        arg_str = arg_str.replace('"', '\"').replace(
            '{', '\{').replace('}', '\}')

        arguments = [job_name, job_class, arg_str]
        replacement_dict = {}
        replacement_dict["arguments"] = arguments
        replacement_dict["hdfs"] = self.HDFS_BASE
        replacement_dict["dependency_zip"] = param_dict["dependency_zip"]
        replacement_dict["conf"] = param_dict.get("conf", {})
        if replacement_dict["conf"] is None:
            replacement_dict["conf"] = {}

        spark_settings = param_dict.get("spark_settings", {})
        if (spark_settings is not None) and (len(spark_settings) != 0):
            # Update spark_settings to use modified parameter names
            JoblibUtils.update_spark_parameters(spark_settings)
            replacement_dict.update(spark_settings)
        else:
            # TODO Need to remove this once every monitor passes it as parameter
            replacement_dict["max_num_executors"] = "2"
            replacement_dict["min_num_executors"] = "1"
            replacement_dict["executor_cores"] = "2"
            replacement_dict["executor_memory"] = "2"
            replacement_dict["driver_cores"] = "2"
            replacement_dict["driver_memory"] = "1"

        clients_dir = pathlib.Path(__file__).parent.absolute()
        with open(str(clients_dir) + "/../jobs/livy_job.json.template", "r") as content_file:
            template_content = content_file.read()
        json_str = Template(template_content)
        json_str = json_str.substitute(replacement_dict)
        json_str = json_str.replace('"', '\\\"')
        json_str = json_str.replace("'", "\"")

        return json.loads(json_str), data_path, output_file_path

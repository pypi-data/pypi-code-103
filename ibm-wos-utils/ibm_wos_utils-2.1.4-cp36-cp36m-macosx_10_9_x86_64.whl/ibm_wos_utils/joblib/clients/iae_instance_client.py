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
import datetime
import time
import urllib
import requests
import os
import pathlib
import tarfile
from time import sleep
import logging
from ibm_wos_utils.joblib.exceptions.client_errors import *
from ibm_wos_utils.joblib.utils import constants
from ibm_wos_utils.joblib.utils.constants import UPLOAD_FILE_RETRY_COUNT, UPLOAD_FILE_RETRY_STATUS_CODES
from ibm_wos_utils.joblib.utils.validator import validate_type
from ibm_wos_utils.joblib.utils.rest_util import RestUtil

logger = logging.getLogger(__name__)

class IAEInstanceClient():
    
    """Client class to manage spark instance and data volumes"""

    def __init__(self, server_url, service_instance_name, volume, token):
        self.server_url = server_url
        self.service_instance_name = service_instance_name
        self.volume = volume
        self.token = token
        
    def get_instance(self, name=None):
        instance = self._get_instance(name=name)
        return IAESparkInstance(self.server_url, instance)

    def _get_instance(self, name=None):
        if name is None:
            name = constants.SPARK_INSTANCE
        validate_type("instance_name", name, str, is_mandatory=True)
        url = "{}/zen-data/v2/serviceInstance?type=spark".format(
            self.server_url)
        response = RestUtil.request().get(
            url=url, headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError("Getting spark instance failed.", response)
        instances = response.json().get("requestObj")
        instance = next((i for i in instances if i.get(
            "ServiceInstanceDisplayName") == name), None)
        if instance is None:
            raise ObjectNotFoundError("Spark instance with name '{}' could not be found.".format(name))
        return instance

    def get_volume(self, name):
        validate_type("volume_name", name, str, is_mandatory=True)
        url = "{}/zen-data/v2/serviceInstance?type=volumes".format(
            self.server_url)
        response = RestUtil.request().get(
            url=url, headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError("Getting data volumes failed.", response)
        instances = response.json().get("requestObj")
        instance = next((i for i in instances if i.get(
            "ServiceInstanceDisplayName") == name), None)
        if instance is None:
            raise ObjectNotFoundError("Volume with name '{}' could not be found.".format(name))
        return instance.get("ID")
    
    def get_instance_volume(self, service_name):      
        instance = self._get_instance(name=service_name)
        return instance["CreateArguments"]["metadata"]["volumeName"]
    
    def create_instance(self, name=None):
        if name is None:
            name = constants.SPARK_INSTANCE
        vol_name = name + "Data"     
        self.create_volume(
            name=vol_name,
            description="OpenScale spark volume",
            size="5Gi")
        payload = {
            "serviceInstanceType": "spark",
            "serviceInstanceDisplayName": name,
            "serviceInstanceVersion": "3.0.0",
            "preExistingOwner": False,
            "createArguments": {
                "metadata": {
                    "volumeName": vol_name,
                    "storageClass": "",
                    "storageSize": ""
                }
            },
            "parameters": {},
            "serviceInstanceDescription": "OpenScale spark instance",
            "metadata": {},
            "ownerServiceInstanceUsername": "",
            "transientFields": {}
        }
        url = "{}/zen-data/v2/serviceInstance".format(self.server_url)
        response = RestUtil.request().post(
            url=url, data=json.dumps(payload), headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError("Creating spark instance {} failed.".format(name), response)
        return response.json().get("id")

    def create_volume(self, name, description, size="2Gi"):
        validate_type("volume_name", name, str, is_mandatory=True)
        payload = {
            "createArguments": {
                "metadata": {
                    "storageClass": "nfs-client",
                    "storageSize": size
                },
                "resources": {},
                "serviceInstanceDescription": description
            },
            "preExistingOwner": False,
            "serviceInstanceDisplayName": name,
            "serviceInstanceType": "volumes",
            "serviceInstanceVersion": "-",
            "transientFields": {}
        }

        url = "{}/zen-data/v2/serviceInstance".format(
            self.server_url)
        response = RestUtil.request().post(
            url=url, data=json.dumps(payload), headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError("Creating volume {} failed.".format(name), response)
        return response.json().get("id")

    def delete_instance(self, name=None):
        if name is None:
            name = constants.SPARK_INSTANCE
        validate_type("instance_name", name, str, is_mandatory=True)
        vol_name = constants.SPARK_VOLUME
        payload = {"serviceInstanceType": "spark", "serviceInstanceVersion": "3.0.0",
                   "serviceInstanceDisplayName": name}
        url = "{}/zen-data/v2/serviceInstance".format(
            self.server_url)
        response = RestUtil.request().delete(
            url=url, data=json.dumps(payload), headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError("Deleting spark instance {} failed.".format(name), response)
        self.delete_volume(name="aiosSparkData")

    def delete_volume(self, name=None):
        if name is None:
            name = constants.SPARK_VOLUME
        validate_type("volume_name", name, str, is_mandatory=True)
        """Deleting a volume doesn't delete from actual storage"""
        payload = {"serviceInstanceType": "volumes", "serviceInstanceVersion": "-",
                   "serviceInstanceDisplayName": name}
        url = "{}/zen-data/v2/serviceInstance".format(
            self.server_url)
        response = RestUtil.request().delete(
            url=url, data=json.dumps(payload), headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError("Deleting volume {} failed.".format(name), response)

    def start_volume_file_server(self, name=None):
        if name is None:
            name = constants.SPARK_VOLUME
        validate_type("volume_name", name, str, is_mandatory=True)
        url = "{}/zen-data/v1/volumes/volume_services/{}".format(
            self.server_url, name)
        response = RestUtil.request().post(
            url=url, data=json.dumps({}), headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError("Starting volume {} file server failed.".format(name), response)

    def stop_volume_file_server(self, name=None):
        if name is None:
            name = constants.SPARK_VOLUME
        validate_type("volume_name", name, str, is_mandatory=True)
        url = "{}/zen-data/v1/volumes/volume_services/{}".format(
            self.server_url, name)
        response = RestUtil.request().delete(
            url=url, headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError("Stopping volume {} file server failed.".format(name), response)

    def get_directories(self, vol_name, path):
        validate_type("volume_name", vol_name, str, is_mandatory=True)
        validate_type("directory_path", path, str, is_mandatory=True)
        path = path.replace("/", "%2F")
        url = "{}/zen-volumes/{}/v1/volumes/directories/{}".format(
            self.server_url, vol_name, path)
        response = RestUtil.request().get(
            url=url, headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError("Getting volume {} directories failed.".format(vol_name), response)
        return response.json()    
            
    
    def upload_file(self, vol_name, src_file_path, tgt_file_path):
        validate_type("volume_name", vol_name, str, is_mandatory=True)
        validate_type("source_file_path", src_file_path, str, is_mandatory=True)
        validate_type("target_file_path", tgt_file_path, str, is_mandatory=True)
        tgt_file_path = tgt_file_path.replace("/", "%2F")
        url = "{}/zen-volumes/{}/v1/volumes/files/{}".format(
            self.server_url, vol_name, tgt_file_path)
        # Retrying with backoff
        delay = 5 # Initial delay for retry
        backoff_factor = 2
        for i in range(UPLOAD_FILE_RETRY_COUNT):
            with open(src_file_path, "rb") as f:
                response = RestUtil.request().put(
                    url=url, headers={
                        "Authorization": "Bearer {}".format(self.token)
                    }, files={"upFile": f}, verify=False)
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
                    raise DependentServiceError("Uploading file to volume {} failed.".format(vol_name), response)
            else:
                # If response is successful, then breaking the loop
                break
        logger.info("\nSuccessfully uploaded file {} to volume {}".format(src_file_path, vol_name))
        print("Successfully uploaded file {} to volume {} at location {}".format(src_file_path, vol_name, tgt_file_path))
        return response.json()
    
    def create_archive(self, src_dir):
        validate_type("source_directory", src_dir, str, is_mandatory=True)
        dir_name = os.path.basename(src_dir)
        tar_file = dir_name+".tar.gz"
        with tarfile.open(tar_file, "w:gz") as tar:
            tar.add(src_dir, arcname=dir_name)

        return tar_file

    def upload_archive(self, vol_name, archive_file, tgt_file_path):
        validate_type("volume_name", vol_name, str, is_mandatory=True)
        validate_type("archive_file", archive_file, str, is_mandatory=True)
        validate_type("target_file_path", tgt_file_path, str, is_mandatory=True)
        tgt_file_path = tgt_file_path.replace("/", "%2F")
        url = "{}/zen-volumes/{}/v1/volumes/files/{}?extract=true".format(
            self.server_url, vol_name, tgt_file_path)
        with open(archive_file, "rb") as f:
            response = RestUtil.request().put(
                url=url, headers={
                    "Authorization": "Bearer {}".format(self.token)
                }, files={"upFile": f}, verify=False)
        
        if not response.ok:
            raise DependentServiceError("Uploading archive {} to volume {} failed.".format(archive_file, vol_name), response)
        print("Successfully uploaded archive {} to volume {} at location {}".format(archive_file, vol_name, tgt_file_path))
        return response.json()

    def pretty_print_POST(self, req):
        """
        At this point it is completely built and ready
        to be fired; it is "prepared".

        However pay attention at the formatting used in 
        this function because it is programmed to be pretty 
        printed and may differ from the actual request.
        """
        print('{}\n{}\r\n{}\r\n\r\n{}'.format(
            '-----------START-----------',
            req.method + ' ' + req.url,
            '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
            req.body,
        ))

    def get_files_from_dir(self, vol_name, file_path):
        validate_type("volume_name", vol_name, str, is_mandatory=True)
        validate_type("file_path", file_path, str, is_mandatory=True)
        file_path = file_path.replace("/", "%2F")
        url = "{}/zen-volumes/{}/v1/volumes/directories/{}".format(
            self.server_url, vol_name, file_path)
        response = RestUtil.request().get(
            url=url, headers={
                "Authorization": "Bearer {}".format(self.token)
            }, verify=False)

        if not response.ok:
            raise DependentServiceError("Getting list of files in directory {} from volume {} failed.".format(file_path, vol_name), response)
        response = response.json()
        file_list = []
        if "responseObject" in response and "directoryContents" in response["responseObject"]:
            file_list = response["responseObject"]["directoryContents"]
        return file_list  
            

    def get_file(self, vol_name, file_path):
        validate_type("volume_name", vol_name, str, is_mandatory=True)
        validate_type("file_path", file_path, str, is_mandatory=True)
        file_name = os.path.basename(file_path)
        file_path = file_path.replace("/", "%2F")
        url = "{}/zen-volumes/{}/v1/volumes/files/{}".format(
            self.server_url, vol_name, file_path)
        response = RestUtil.request().get(
            url=url, headers={
                "Authorization": "Bearer {}".format(self.token)
            }, verify=False)

        if not response.ok:
            raise DependentServiceError("Getting file {} from volume {} failed.".format(file_path, vol_name), response)
        logger.info("Successfully read file {} from volume {}.".format(file_path, vol_name))
        return response.content

    def delete_file(self, vol_name, file_path):
        validate_type("volume_name", vol_name, str, is_mandatory=True)
        validate_type("file_path", file_path, str, is_mandatory=True)
        file_path = file_path.replace("/", "%2F")
        url = "{}/zen-volumes/{}/v1/volumes/files/{}".format(
            self.server_url, vol_name, file_path)
        response = RestUtil.request().delete(
            url=url, headers={
                "Authorization": "Bearer {}".format(self.token)
            }, verify=False)

        if not response.ok:
            raise DependentServiceError("Deleting file {} from volume {} failed.".format(file_path, vol_name), response)
            print("Volume {} delete file failed. Response {}".format(
                vol_name, response.text))
        logger.info("Successfully deleted file {} from volume {}".format(file_path, vol_name))

    def get_instance_token(self, instance_id):
        url = "{}/zen-data/v2/serviceInstance/token".format(self.server_url)
        response = RestUtil.request().post(
            url=url, data=json.dumps({"serviceInstanceID": str(instance_id)}), headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError("Getting token for service instance id {} failed.".format(instance_id), response)
        return response.json().get("AccessToken")

    def run_job(self, job_json, background=True):
        validate_type("job_payload", job_json, dict, is_mandatory=True)
        spark_instance = self.get_instance(name=self.service_instance_name)
        job_url = spark_instance.jobs_url
        #instance_token = self.get_instance_token(spark_instance.instance_id)
        logger.info("Submitting spark job to IAE instance {}. Job URL: {}".format(spark_instance.instance_id, job_url))
        response = requests.post(
            url=job_url, json=job_json, headers=self.__get_headers(), verify=False)
        if not response.ok:
            #Response code will be 503 when there are insufficient resources.
            raise DependentServiceError("Failed to run job.", response)
        job_response = response.json()
        job_id = job_response.get("id")
        state = job_response.get("job_state")
        # Add state field to response which is used by calling service
        job_response["state"] = str(state).lower()
        print("\nSuccessfully submitted spark job to IAE instance {}. Job ID: {}, Status {}".format(spark_instance.instance_id, job_id, state))
        logger.info("Successfully submitted spark job to IAE instance {}. Job ID: {}, Status {}".format(spark_instance.instance_id, job_id, state))
        if background is False:
            start_time = time.time()
            elapsed_time = 0
            sleep_time = 15
            timeout = constants.SYNC_JOB_MAX_WAIT_TIME
            while state not in (constants.IAE_JOB_FINISHED_STATE, constants.IAE_JOB_FAILED_STATE):
                if elapsed_time > timeout:
                    raise Exception("Job didn't come to FINISHED/FAILED state in {} seconds. Current state is ".format(timeout, state)) 
                print("{}: Sleeping for {} seconds. Current state {}".format(datetime.datetime.now(), sleep_time,state))
                sleep(sleep_time)
                elapsed_time = time.time() - start_time
                state = self.get_job_state(job_id, job_url=job_url)
              
        return job_response
    
    def delete_job(self, job_id):
        validate_type("job_id", job_id, str, is_mandatory=True)
        spark_instance = self.get_instance(name=self.service_instance_name)
        jobs_url = spark_instance.jobs_url + "/" + job_id
        
        response = requests.delete(url=jobs_url, headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError("Failed to delete job with URL {}.".format(jobs_url), response)
        return

    def get_job_state(self, job_id, instance_token=None, job_url=None):
        validate_type("job_id", job_id, str, is_mandatory=True)
        if instance_token is None or job_url is None:
            spark_instance = self.get_instance(name=self.service_instance_name)
            #instance_token = self.get_instance_token(spark_instance.instance_id)
            job_url = spark_instance.jobs_url + "/" + job_id
        response = RestUtil.request().get(
            url=job_url, headers=self.__get_headers(), verify=False)
        if not response.ok:
            raise DependentServiceError("Failed to get status for job with id {}.".format(job_id), response)
        job_response = response.json()
        # Not sure why we get response as list when we try to retrieve status from run_job call
        if type(job_response) is list:
            return job_response[0].get("job_state")
        else:
            return job_response.get("job_state")

    def get_job_logs(self, job_id):
        raise NotImplementedError("get_job_logs")

    def delete_job_artifacts(self, job_id):
        raise NotImplementedError("delete_job_artifacts")

    def __get_headers(self):
        return {"Authorization": "Bearer {}".format(self.token),
                "Content-Type": "application/json"}
    
    def kill_job(self, job_id):
        raise NotImplementedError("kill_job")    


class IAESparkInstance():
    def __init__(self, server_url, instance):
        validate_type("server_url", server_url, str, is_mandatory=True)
        validate_type("spark_instance", instance, dict, is_mandatory=True)
        self.instance_id = instance.get("ID")
        self.jobs_url = instance["CreateArguments"]["connection-info"]["Spark jobs endpoint"].replace(
            "$HOST", server_url)

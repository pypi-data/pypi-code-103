# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import json
import os
import pathlib
import uuid
import tempfile
import tarfile
import logging
import tempfile
from string import Template

from ibm_wos_utils.joblib.clients.engine import Client
from ibm_wos_utils.joblib.clients.iae_instance_client import IAEInstanceClient
from ibm_wos_utils.joblib.exceptions.client_errors import *
from ibm_wos_utils.joblib.utils import constants
from ibm_wos_utils.joblib.utils.db_utils import DbUtils
from ibm_wos_utils.joblib.utils.joblib_utils import JoblibUtils
from ibm_wos_utils.joblib.utils.param_utils import get
from ibm_wos_utils.joblib.utils.validator import validate_type

from ibm_wos_utils.joblib.utils.jobstatus_utils import get_common_job_status

logger = logging.getLogger(__name__)


class IAEEngineClient(Client):

    def __init__(self, server_url, service_instance_name, volume, token):
        super().__init__()
        validate_type('server_url', server_url, str, is_mandatory=True)
        validate_type('token', token, str, is_mandatory=True)
        self.server_url = server_url
        self.service_instance_name = service_instance_name
        self.volume = volume
        self.token = token
        self.files_url = '/spark_wrapper/v1/files'
        self.iae_instance_client = IAEInstanceClient(
            self.server_url, self.service_instance_name, self.volume, self.token)

    def upload_job_artifacts(self, file_list, target_folder, overwrite=True):
        """
        Method to upload job artifacts.
        :param file_list: List of files to upload
        :type file_list: list
        :param target_folder: Path of destination directory where files will be uploaded
        :type target_folder: str
        :param overwrite: Flag to indicate whether to overwrite file
        :type overwrite: bool
        """
        try:
            #volume = self.iae_instance_client.get_instance_volume(self.service_instance_name)
            for file in file_list:
                folder_path, file_name = os.path.split(file)
                self.iae_instance_client.upload_file(self.volume, file,
                                                     target_folder + "/{}".format(file_name))
        except ClientError as clerr:
            raise clerr
        except Exception as e:
            raise ClientError(
                "Error while uploading job artifacts. Error: {}".format(str(e)))

    def run_job(self, job_name, job_class, job_args, data_file_list=None, background=True, timeout=constants.SYNC_JOB_MAX_WAIT_TIME):
        """
        Method to submit spark job.
        :param job_name: Name of the job
        :type job_name: str
        :param job_class: Job class to be executed
        :type job_class: str
        :param job_args: Input parameters to the job
        :type job_args: dict
        :param data_file_list: List of files to be uploaded, if any
        :type data_file_list: list
        :param background: Flag to indicate whether to run job in async mode 
        :type job_type: bool
        """
        certificate_file = None
        try:
            job_class_path = job_class.__module__ + "." + job_class.__name__
            validate_type("job_name", job_name, str, True)
            validate_type("job_class", job_class_path, str, True)
            validate_type("job_args", job_args, dict, True)
            # Push entry job
            entry_job_path = constants.ENTRY_JOB_BASE_FOLDER
            # Upload the main job
            clients_dir = str(pathlib.Path(__file__).parent.absolute())
            file_list = [str(clients_dir) + "/../" + constants.ENTRY_JOB_FILE]
            self.upload_job_artifacts(file_list, entry_job_path)

            # Create temp file containing the arguments json
            fp = tempfile.NamedTemporaryFile(delete=True)
            head, filename = os.path.split(fp.name)

            # If SSL certificate is specified in job parameters, then create certificate file and upload to volume
            certificate_file = DbUtils.check_and_create_ssl_cert_file(
                job_args.get("arguments"))
            if certificate_file:
                # Add certificate_file name to job parameters
                directory, file_name = os.path.split(certificate_file)
                job_args["arguments"]["storage"]["connection"]["ssl_cert_file_name"] = file_name

            # Compose job payload
            json_payload, data_path, output_file_path, arguments = self.get_job_payload(
                job_name, job_class_path, job_args, filename)
            # Check if default volume associated with the spark instance is used. If yes, remove it from job payload.
            instance_volume = self.iae_instance_client.get_instance_volume(
                self.service_instance_name)
            default_volume_used = JoblibUtils.is_default_volume_used(
                json_payload, instance_volume)
            if default_volume_used:
                del json_payload["engine"]["volumes"]

            # write arguments to file
            fp.write(bytes(str(arguments), 'utf-8'))
            fp.seek(0)
            if data_file_list is None:
                data_file_list = [fp.name]
            else:
                data_file_list.append(fp.name)

            if certificate_file:
                # Upload certificate file to volume
                data_file_list.append(certificate_file)

            # Upload dependent files, if any
            if data_file_list is not None and len(data_file_list) > 0:
                self.upload_job_artifacts(data_file_list, data_path)

            # Submit the job
            job_response = None
            try:
                job_response = self.iae_instance_client.run_job(
                    json_payload, background, timeout)
            except Exception as ex:
                raise ex
            finally:
                # delete the temp file
                fp.close()

            job_response['output_file_path'] = output_file_path
            state = job_response.get("state")
            job_response['state'] = get_common_job_status(
                str(state).lower()).value

            return job_response

        except ClientError as clerr:
            raise clerr
        except Exception as e:
            raise ClientError(
                "Error while executing spark job. Error: {}".format(str(e)))
        finally:
            # If temporary file is created for ssl certificate_file, delete it
            if certificate_file:
                JoblibUtils.delete_local_file(certificate_file)

    def get_job_status(self, job_id):
        """
        Method to get status of spark job.
        :param job_id: ID of the job
        :type job_id: str
        :param job_state: Status of the job
        :type job_state: str
        """
        try:
            status = self.iae_instance_client.get_job_state(job_id)
            # Sometimes the API to get status returns finished status even when job is failed. So checking the status again in when API returns status as finished. WI 21371
            if str(status).lower() in constants.JOB_FINISHED_STATES:
                status = self.iae_instance_client.get_job_state(job_id)
            state = get_common_job_status(str(status).lower()).value
            response = {
                "job_id": job_id,
                "state": state
            }
            return response
        except ClientError as clerr:
            raise clerr
        except Exception as e:
            raise ClientError(
                "Error while fetching job status. Error: {}".format(str(e)))

    def get_file(self, file_path):
        """
        Method to get output written by the spark job.
        :param file_path: Source file location
        :type file_path: str
        """
        try:
            # The spark job writes output in a directory at location file_path
            # Fetch the list of files in the directory
            file_list = self.iae_instance_client.get_files_from_dir(
                self.volume, file_path)
            if len(file_list) == 0:
                raise ClientError("The specified directory {} in volume {} is empty.".format(
                    file_path, self.volume))
            # The directory contains files like _SUCCESS, _SUCCESS.crc, part-00000-.json, .part-00000-.json.crc. Select appropriate file
            output_file = None
            for f in file_list:
                file_name = str(f)
                if file_name.startswith("part-") and not file_name.endswith(".crc"):
                    output_file = file_name
            if output_file is None:
                raise ClientError("Status Code: 404. Error: Could not find job output file in directory {} in volume {}.".format(
                    file_path, self.volume))
            return self.iae_instance_client.get_file(self.volume, file_path+"/"+output_file)
        except ClientError as clerr:
            raise clerr
        except Exception as e:
            raise ClientError(
                "Error while fetching job output. Error: {}".format(str(e)))

    def _get_file(self, file_path):
        """
        Method to get file contents located at given path.
        :param file_path: Source file location
        :type file_path: str
        """
        try:
            return self.iae_instance_client.get_file(self.volume, file_path)
        except ClientError as clerr:
            raise clerr
        except Exception as e:
            raise ClientError(
                "Error while fetching job output. Error: {}".format(str(e)))

    def get_job_logs(self, job_id):
        """
        Method to get logs of spark job.
        :param job_id: ID of the job
        :type job_id: str
        """
        try:
            self.iae_instance_client.get_job_logs(job_id)
        except ClientError as clerr:
            raise clerr
        except Exception as e:
            raise ClientError(
                "Error while fetching job logs. Error: {}".format(str(e)))

    def delete_job_artifacts(self, job_id):
        """
        Method to delete artifacts created for a spark job.
        :param job_id: ID of the job
        :type job_id: str
        """
        try:
            self.iae_instance_client.delete_job_artifacts(job_id)
        except ClientError as clerr:
            raise clerr
        except Exception as e:
            raise ClientError(
                "Error while deleting job artifacts. Error: {}".format(str(e)))

    def get_exception(self, output_file_path):
        data = self.get_file(output_file_path + "/exception.json")
        return json.loads(data.decode("utf-8"))

    def kill_job(self, job_id):
        pass

    def get_job_payload(self, job_name, job_class, param_dict, argumentfile_name):
        payload_dict = dict()
        if "arguments" not in param_dict:
            param_dict["arguments"] = {}
        # copy original parameters
        original_argument = param_dict["arguments"].copy()
        subscription_id = get(
            param_dict, "arguments.subscription_id") or str(uuid.uuid4())
        run_id = get(param_dict, "arguments.monitoring_run_id") or str(
            uuid.uuid4())

        if job_name is None:
            job_name = constants.IAE_SPARK_JOB_NAME
        payload_dict["name"] = job_name
        volume = param_dict.get("volume")
        if volume is None:
            volume = self.volume
        payload_dict["volume_name"] = volume
        volume_mount_path = param_dict.get("mount_path")
        if volume_mount_path is None:
            volume_mount_path = constants.IAE_VOLUME_MOUNT_PATH
        if volume_mount_path is not None and not volume_mount_path.startswith("/"):
            volume_mount_path = "/" + volume_mount_path
        payload_dict["mount_path"] = volume_mount_path
        base_path = job_name + "/" + subscription_id
        data_path = base_path + "/data"
        # removing original prameters and adding path related params so that volume gets replaced by wrapper app
        param_dict["arguments"] = {}

        param_dict["arguments"]["data_file_path"] = "{}/{}".format(
            volume_mount_path, data_path)

        output_file_path = None
        if run_id is not None:
            output_file_path = base_path + "/output/" + run_id
            param_dict["arguments"]["output_file_path"] = "{}/{}".format(
                volume_mount_path, output_file_path)
        param_dict["arguments"]["param_file_name"] = argumentfile_name
        param_dict["arguments"]["storage_type"] = get(
            original_argument, "storage.type")

        # Get the spark configuration parameters
        spark_settings = param_dict.get("spark_settings") or {}
        if (spark_settings is not None) and (len(spark_settings) != 0):
            # Update spark_settings to use modified parameter names
            JoblibUtils.update_spark_parameters(spark_settings)
        else:
            spark_settings["max_num_executors"] = "2"
            spark_settings["executor_cores"] = "2"
            spark_settings["executor_memory"] = "2"
            spark_settings["driver_cores"] = "2"
            spark_settings["driver_memory"] = "1"

        original_argument["spark_settings"] = spark_settings
        arg_str = json.dumps(param_dict["arguments"])
        arg_str = arg_str.replace('"', '\"')
        arguments = [job_name, job_class, arg_str]
        payload_dict["parameter_list"] = arguments
        payload_dict["full_job_file"] = "{}/{}/{}".format(
            volume_mount_path, constants.ENTRY_JOB_BASE_FOLDER, constants.ENTRY_JOB_FILE)

        payload_dict.update(spark_settings)
        # Read the template file
        clients_dir = pathlib.Path(__file__).parent.absolute()
        with open(str(clients_dir) + "/../jobs/iae_job.json.template", 'r') as content_file:
            template_content = content_file.read()

        json_str = Template(template_content)
        json_str = json_str.substitute(payload_dict)
        json_str = json_str.replace('"', '\\\"')
        json_str = json_str.replace("'", "\"")
        return json.loads(json_str), data_path, output_file_path, original_argument

    def __get_job_payload(self, param_dict):
        '''
        Following values needs to be replaced in job payload template
            name - name of the job
            num_of_nodes - eg: 2
            worker_cpu - eg: 2
            worker_memory -eg: 1g
            driver_cpu
            driver_memory
            volume_name
            mount_path
            parameter_list
            full_job_file
        '''

        import pathlib
        clients_dir = pathlib.Path(__file__).parent.absolute()
        with open(str(clients_dir) + "/../jobs/iae_job.json.template", 'r') as content_file:
            template_content = content_file.read()

        json_str = Template(template_content)
        json_str = json_str.substitute(param_dict)
        json_str = json_str.replace("'", "\"")
        return json.loads(json_str)

    def download_directory(self, directory_path):
        return self._get_file(directory_path)

    def delete_directory(self, directory_path):
        try:
            if directory_path.startswith(constants.IAE_VOLUME_MOUNT_PATH):
                directory_path = directory_path[len(
                    constants.IAE_VOLUME_MOUNT_PATH):]
            self.iae_instance_client.delete_file(self.volume, directory_path)
        except Exception as e:
            logger.error(
                "Error while deleting the directory. Error: {}".format(str(e)))
            raise ClientError(
                "Error while deleting the directory. Error: {}".format(str(e)))

    def upload_directory(self, directory_path, archive_directory_content):
        try:
            with tempfile.NamedTemporaryFile(suffix=".tar.gz") as temp:
                temp.write(archive_directory_content)
                temp.flush()
                self.iae_instance_client.upload_archive(
                    self.volume, temp.name, directory_path)
                upload_path = constants.IAE_VOLUME_MOUNT_PATH + directory_path
                return upload_path
        except Exception as e:
            logger.error(
                "An error occurred while uploading the directory. Error: {}".format(str(e)))
            raise ClientError(
                "An error occurred while uploading the directory. Error: {}".format(str(e)))

# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import os
import logging

from ibm_wos_utils.joblib.utils import constants
from ibm_wos_utils.joblib.utils.python_utils import get

logger = logging.getLogger(__name__)

class JoblibUtils:

    @classmethod
    def get_spark_instance_details(cls, credentials):
        spark_instance_details = dict()
        connection = credentials.get("connection")
        spark_credentials = credentials.get("credentials")
        if spark_credentials is None:  # This is for backward compatibility
            spark_credentials = credentials.get("spark_credentials")
        if connection is not None:
            endpoint = connection.get("endpoint")
            location_type = connection.get("location_type")
            spark_instance_details["location_type"] = location_type
            if location_type is not None and location_type == constants.SparkType.IAE_SPARK.value:
                # Get spark instance name and volume for IAE
                spark_instance_details["instance_id"] = connection.get(
                    "instance_id")
                spark_instance_details["display_name"] = connection.get(
                    "display_name")
                spark_instance_details["volume"] = connection.get("volume")
                # In case of IAE, endpoint will be jobs endpoint. So just fetching host part from the endpoint
                if endpoint is not None and "/ae/" in endpoint:
                    endpoint = endpoint.split("/ae/")[0]
        else:
            endpoint = spark_credentials.get("url")
        spark_instance_details["endpoint"] = endpoint
        spark_instance_details["username"] = spark_credentials.get("username")
        if "password" in spark_credentials:
            spark_instance_details["password"] = spark_credentials.get(
                "password")
        if "apikey" in spark_credentials:
            spark_instance_details["apikey"] = spark_credentials.get("apikey")
        return spark_instance_details

    @classmethod
    def is_default_volume_used(cls, job_payload, instance_volume):
        default_volume_used = False
        volumes = get(job_payload, "engine.volumes")
        if volumes is not None and len(volumes) > 0:
            volume_name = volumes[0].get("volume_name")
            if instance_volume == volume_name:
                default_volume_used = True
        return default_volume_used

    @classmethod
    def update_spark_parameters(cls, spark_parameters):
        if "max_num_executors" not in spark_parameters and "max_executors" in spark_parameters:
            spark_parameters["max_num_executors"] = spark_parameters.get(
                "max_executors")
        if "min_num_executors" not in spark_parameters and "min_executors" in spark_parameters:
            spark_parameters["min_num_executors"] = spark_parameters.get(
                "min_executors")
        if "executor_cores" not in spark_parameters and "max_executor_cores" in spark_parameters:
            spark_parameters["executor_cores"] = spark_parameters.get(
                "max_executor_cores")
        if "driver_cores" not in spark_parameters and "max_driver_cores" in spark_parameters:
            spark_parameters["driver_cores"] = spark_parameters.get(
                "max_driver_cores")

    @classmethod
    def get_column_by_modeling_role(cls, schema, modeling_role):
        for column in schema.get("fields"):
            col_modeling_role = get(column, "metadata.modeling_role")
            if col_modeling_role is not None and col_modeling_role == modeling_role:
                return column.get("name")
        return None

    @classmethod
    def delete_local_file(cls, file_path: str):
        try:
            if file_path is not None and os.path.exists(file_path) and os.path.isfile(file_path):
                os.remove(file_path)
                logger.info('Deleted file {}'.format(file_path))
        except Exception as e:
            logger.warning(
                "Failed to delete file {}. Error: {}".format(file_path, str(e)))

    @classmethod
    def delete_file_from_hdfs(cls, spark, file_path: str):
        try:
            sc = spark.sparkContext
            fs = sc._jvm.org.apache.hadoop.fs.FileSystem.get(
                sc._jsc.hadoopConfiguration())
            if file_path:
                fs_file_path = sc._jvm.org.apache.hadoop.fs.Path(file_path)
                if fs.exists(fs_file_path) and fs.isFile(fs_file_path):
                    fs.delete(fs_file_path, True)
                    logger.info('Deleted file {}'.format(file_path))
        except Exception as e:
            logger.warning(
                "Failed to delete file {}. Error: {}".format(file_path, str(e)))

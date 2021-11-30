# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2020
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import json
import logging
import logging.config
import pathlib
import traceback
from abc import ABC

from ibm_wos_utils.joblib.utils.param_utils import get


class AIOSBaseJob(ABC):

    def __init__(self, arguments, job_name: str = "Base Job"):

        print("*********** Dumping a list of packages and versions ********************")
        import pkg_resources
        packages_of_interest = ["pyspark", "numpy", "pandas", "ibm-wos-utils"]
        installed_packages_list = sorted(["{}=={}".format(
            i.key, i.version) for i in pkg_resources.working_set if i.key in packages_of_interest])
        print("Packages of Interest: {}".format(packages_of_interest))
        print("Installed packaged of interest with version: {}".format(
            installed_packages_list))
        print("************************************************************************")

        spark_module = None
        try:
            spark_module = __import__("pyspark.sql", fromlist=["SparkSession"])
        except Exception as e:
            msg = "Unable to find pyspark library ro run AI OpenScale Job " + job_name
            raise Exception(msg)

        sparkSession = getattr(spark_module, "SparkSession")

        print(" AIOSBaseJob instantiated with parameter ", arguments)
        self.storage_type = get(arguments, "storage.type")

        sparkApp = sparkSession.builder.appName(job_name)
        if self.storage_type == "hive":
            sparkApp = sparkApp.enableHiveSupport()

        self.spark = sparkApp.getOrCreate()
        self.sc = self.spark.sparkContext
        self.arguments = arguments
        self.logger = self.__get_logger()

        print("===== Start - Spark Properties ")
        print(self.sc.getConf().getAll())
        print("===== End - Spark Properties ")

        """
            conf.set("spark.dynamicAllocation.enabled",True)
            conf.set("spark.shuffle.service.enabled",True)
            conf.set("spark.dynamicAllocation.shuffleTracking.enabled",True)
            conf.set("spark.dynamicAllocation.minExecutors", "5");
            conf.set("spark.dynamicAllocation.maxExecutors", "30");
            conf.set("spark.dynamicAllocation.initialExecutors", "10");
            spark.sql.execution.arrow.enabled
            spark.sql.execution.arrow.fallback.enabled
        """

        if self.storage_type == "hive":
            metastore_url = get(
                self.arguments, "storage.connection.metastore_url")
            if metastore_url:
                self.sc.setSystemProperty("hive.metastore.uris", metastore_url)

        self.jdbc_connection_driver = None
        self.jdbc_connection_driver = None
        if self.storage_type == "jdbc":
            self.jdbc_connection_url = get(
                self.arguments, "storage.connection.jdbc_url")
            self.jdbc_connection_driver = get(
                self.arguments, "storage.connection.jdbc_driver")

        # Set the following configuration to skip generating _SUCCESS file
        # while saving dataframe as files in HDFS
        self.sc._jsc.hadoopConfiguration().set(
            "mapreduce.fileoutputcommitter.marksuccessfuljobs", "false")

    def save_data(
            self,
            path: str,
            data_json: dict,
            mode: str = "overwrite",
            compression: str = None):
        df = self.spark.createDataFrame([data_json])
        if compression is None:
            df.coalesce(1).write.json(path, mode=mode)
        else:
            df.coalesce(1).write.json(path, mode=mode, compression=compression)

    def save_exception_trace(self, error_msg: str):
        tr = traceback.format_exc()
        output_path = self.arguments.get("output_file_path")
        path = output_path + "/exception.json"
        exception = {
            "error_msg": error_msg,
            "stacktrace": tr
        }
        self.save_data(path=path, data_json=exception)

    def save_log_file(self, mode: str = "overwrite"):

        f = open("openscale_job.log", "r")
        d = [(str(f.read()))]
        strType = __import__("pyspark.sql.types", fromlist=["StringType"])
        df = self.spark.createDataFrame(d, getattr(strType, "StringType")())
        df.coalesce(1).write.mode(mode).text(
            self.arguments.get("output_file_path") + "/job.log")

    def __get_logger(self):
        clients_dir = pathlib.Path(__file__).parent.absolute()
        with open(str(clients_dir) + "/../jobs/logging.json", "r") as f:
            log_config = json.load(f)
        logging.config.dictConfig(log_config)
        return logging.getLogger(__name__)

    def finish_job(self):
        self.save_log_file()
        if self.spark is not None:
            self.spark.stop()

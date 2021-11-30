# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2019, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S. Copyright Office.
# ----------------------------------------------------------------------------------------------------

import io
import json
import os
import unittest


class BaseTestUtils(unittest.TestCase):

    def read_json_resource(self, file_name):
        data = None
        with io.open(os.getcwd() + "/tests/unit/resources/" + file_name + ".json", "r", encoding="utf-8") as my_file:
            data_str = my_file.read()
            data = json.loads(data_str)
        return data

    def read_csv_resource_as_spark_df(self, file_name: str, spark):
        # Reads a CSV file and returns a spark dataframe
        file_path = "{}/ibm_wos_utils/joblib/tests/resources/data/{}".format(
            os.getcwd(), file_name)
        if not file_path.endswith(".csv"):
            file_path += ".csv"
        spark_df = spark.read \
            .option("header", "true") \
            .csv(file_path)
        return spark_df


if __name__ == '__main__':
    unittest.main()

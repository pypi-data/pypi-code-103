# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2020
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import base64
import json
import time
from json.decoder import JSONDecodeError

from ibm_wos_utils.joblib.exceptions.client_errors import DependentServiceError, ClientError
from IPython.display import HTML, clear_output


def validate_config_info(config_info):
    model_type = config_info["problem_type"]
    missing_details = []
    if config_info.get("label_column") is None:
        missing_details.append("label_column")

    if config_info.get("feature_columns") is None:
        missing_details.append("feature_columns")

    if config_info.get("prediction") is None:
        missing_details.append("prediction")

    if model_type != "regression" and config_info.get("probability") is None:
        missing_details.append("probability")

    if len(missing_details) > 0:
        raise Exception(
            "Missing information in config_info. Details:{}".format(missing_details))

    categorical_columns = config_info.get("categorical_columns")
    if categorical_columns is not None and len(categorical_columns) > 0:
        check_cat_col_existence = list(
            set(categorical_columns) - set(config_info.get("feature_columns")))
        if len(check_cat_col_existence) > 0:
            raise Exception("'categorical_columns' should be subset of feature columns. Missing Details:{}".format(
                check_cat_col_existence))


def is_prediction_type_valid(model_type, label_field, prediction_field):
    numeric_fields = ["short", "integer", "long", "float", "double", "decimal"]
    if (model_type == "regression") and (prediction_field["type"] in numeric_fields) and (
            label_field["type"] in numeric_fields):
        return True

    if prediction_field["type"] == label_field["type"]:
        return True

    return False


def generate_schemas(df, config_info):
    # Convert boolean columns to string
    spark_df_dtypes = dict(df.dtypes)
    for col in df.columns:
        if spark_df_dtypes[col] == "boolean":
            df = df.withColumn(
                col, df[col].cast("string"))

    # Read inputs from config:
    feature_columns = config_info.get("feature_columns")
    categorical_columns = config_info.get("categorical_columns")
    if categorical_columns is None:
        categorical_columns = []

    label_column = config_info.get("label_column")
    prediction = config_info.get("prediction")
    model_type = config_info.get("problem_type")
    probability = config_info.get(
        "probability") if model_type != "regression" else None
    record_id = "scoring_id"
    record_timestamp = "scoring_timestamp"
    # record_id = config_info.get("record_id") or "record_id"
    # record_timestamp = config_info.get("record_timestamp")

    prediction_field = {}
    probability_field = {}
    label_field = {}
    fields = []
    training_fields = []
    output_fields = []
    column_names = []
    for f in df.schema:
        field = f.jsonValue()
        column = field["name"]
        column_names.append(column)

        if column == prediction:
            prediction_field = field.copy()
            prediction_field["metadata"]["modeling_role"] = "prediction"
            output_fields.append(prediction_field)

        elif model_type != "regression" and column == probability:
            probability_field = field.copy()
            probability_field["metadata"]["modeling_role"] = "probability"
            output_fields.append(probability_field)

        elif column == label_column:
            label_field = field.copy()
            label_field["metadata"]["modeling_role"] = "target"
            training_fields.append(label_field)

        elif column in feature_columns:
            field["metadata"]["modeling_role"] = "feature"

            if column in categorical_columns:
                field["metadata"]["measure"] = "discrete"

            fields.append(field)
            training_fields.append(field)
            output_fields.append(field)
        else:
            continue

    # Check missing details and proceed
    missing_features = list(set(feature_columns) - set(column_names))
    if len(missing_features) > 0:
        raise Exception(
            "Missing features in sample score data provided.Details:{}".format(missing_features))

    # Set input data schema
    input_data_schema = {}
    input_data_schema["type"] = "struct"
    input_data_schema["fields"] = fields

    # Set training data schema
    training_data_schema = {}
    if len(label_field) > 0:
        training_data_schema["type"] = "struct"
        training_data_schema["fields"] = training_fields
    else:
        raise Exception("Missing class label details in sample score data")

    # Set output data schema
    output_data_schema = {}

    # Set prediction
    if len(prediction_field) > 0:
        if not is_prediction_type_valid(
                model_type, label_field, prediction_field):
            raise Exception(
                "The data types of prediction ({}) and label column ({}) do not match.".format(
                    prediction_field["type"], label_field["type"]))
    else:
        raise Exception(
            "Missing prediction column details in sample score data")

    # Set probability
    if model_type != "regression":
        if len(probability_field) > 0:
            # Setting probability type as array of doubles
            probability_field["type"] = {
                "type": "array",
                "elementType": "double",
                "containsNull": True
            }
        else:
            raise Exception(
                "Missing probability column details in sample score data")

    record_id_field = {
        "name": record_id,
        "type": "string",
        "nullable": False,
        "metadata": {
            "modeling_role": "record-id"
        }
    }
    output_fields.append(record_id_field)

    if record_timestamp is not None and record_timestamp != "":
        record_timestamp_field = {
            "name": record_timestamp,
            "type": "timestamp",
            "nullable": False,
            "metadata": {
                "modeling_role": "record-timestamp"
            }
        }
        output_fields.append(record_timestamp_field)

    output_data_schema["type"] = "struct"
    output_data_schema["fields"] = output_fields

    common_config = config_info.copy()
    if ("probability" in common_config) and (model_type == "regression"):
        del common_config["probability"]
    common_config["record_id"] = record_id
    common_config["record_timestamp"] = record_timestamp
    common_config["training_data_schema"] = training_data_schema
    common_config["input_data_schema"] = input_data_schema
    common_config["output_data_schema"] = output_data_schema
    return common_config


def create_download_link(data, type):
    format_args = {}
    if type == "config":
        output_json = json.dumps(data, indent=4)
        format_args = {
            "payload": base64.b64encode(output_json.encode()).decode(),
            "title": "Download Common Configuration JSON",
            "filename": "common_configuration.json"
        }
    elif type == "drift":
        format_args = {
            "payload": base64.b64encode(data).decode(),
            "title": "Download Drift Configuration Archive",
            "filename": "drift.tar.gz"
        }
    else:
        print("The type parameter should be one of ('config', 'drift')")
        return
    html = '<a download="{filename}" href="data:text/json;base64,{payload}" target="_blank">{title}</a>'
    return HTML(html.format(**format_args))


class JobStatus(object):
    INITIAL_INTERVAL = 5
    MAX_INTERVAL = 60

    def __init__(self, client, job_response, clear_output=True):
        self.client = client
        self.app_id = job_response.get("appId")
        self.job_id = job_response.get("id")
        self.job_state = job_response.get("state", "starting")
        self.output_file_path = job_response.get("output_file_path")
        self.interval = JobStatus.INITIAL_INTERVAL
        self.previous_status = None
        self.status = None
        self.response = None
        self.start_time = time.time()
        self.clear_output = clear_output

    def __time_string(self):
        seconds = int(time.time() - self.start_time)
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        if days > 0:
            return "{} days {} hours {} minutes {} seconds".format(
                days, hours, minutes, seconds)
        elif hours > 0:
            return "{} hours {} minutes {} seconds".format(
                hours, minutes, seconds)
        elif minutes > 0:
            return "{} minutes {} seconds".format(minutes, seconds)
        else:
            return "{} seconds".format(seconds)

    def __print_status_helper(self, status=None):
        prefix = "Application ID: {}; Job ID: {};".format(
            self.app_id, self.job_id)
        if status == "FINISHED":
            print("{} Status: FINISHED.".format(prefix))
            print("Total Run Time: {} ".format(self.__time_string()))
        elif status == "FAILED":
            print(
                "{} Status: FAILED. Exception: {}".format(
                    prefix,
                    self.response.get(
                        "exception",
                        "No exception saved.")))
            print("Total Run Time: {} ".format(self.__time_string()))
        else:
            print("{} Status: {}. Sleeping for {} seconds.".format(
                prefix, status or "File not present", self.interval))
            print("Current Run Time: {} ".format(self.__time_string()))
            time.sleep(self.interval)
            self.interval = min(JobStatus.MAX_INTERVAL, self.interval * 2)
            self.previous_status = status

    def print_status(self):
        while True:
            try:
                if self.clear_output:
                    clear_output(wait=True)
                self.response = self.client.engine.get_file(
                    self.output_file_path + "/drift_config_status.json").decode()
                self.response = json.loads(self.response)

                if self.response is None:
                    self.__print_status_helper()
                    continue

                self.status = self.response.get("status")
                if self.status != self.previous_status:
                    self.interval = JobStatus.INITIAL_INTERVAL
                self.__print_status_helper(self.status)
                if self.status in ("FINISHED", "FAILED"):
                    break

            except JSONDecodeError as ex:
                print(self.response)
                self.__print_status_helper()
                continue
            except (DependentServiceError, ClientError) as ex:
                if "404" in str(ex):
                    self.__print_status_helper()
                    continue
            finally:
                # Providing a fallback here to check Spark Job status.
                # So that the status polling doesn't keep happening forever.
                response = self.client.engine.get_job_status(self.job_id)
                self.app_id = response.get("appId")
                self.job_state = response.get("state")
                if self.job_state in ("error", "dead", "killed", "failed"):
                    print(response)
                    break

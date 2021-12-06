import json
import os
import re
import shutil

import pandas as pd
import numpy as np
import milliman_sensi.syntax as syn

from pathlib import Path

pd.options.mode.chained_assignment = None  # Used to supress panda warning
SENSI_CONFIG_HEADER = ['Scenario', 'Stress name', 'Apply stress']

# IR -> Nominal_rates
# RIR -> Real_rates
# EQ -> Equity
# RE -> Real_estate
# CRED -> Credit
# FX -> FX_rate

# Custom Exception class for sensi validation and modification
class SensiIOError(Exception):
    def __init__(self, msg):
        self.msg = str(msg)

    def __str__(self):
        return self.msg

def log(msg, logger=None):
    # If logger is a string of output file
    if isinstance(logger, str):
        with open(logger, mode='a') as output:
            print(msg, file=output, flush=True)
    else:
        if logger is not None:
            logger.info(msg)

def read_json_file(file_path):
    data = None
    try:
        with open(file_path) as json_file:
            data = json.load(json_file)
    except ValueError:
        raise ValueError("Failed to load the json file {}".format(file_path))
    except FileNotFoundError:
        raise FileNotFoundError("Unable to find json file {}".format(file_path))

    return data


def find_file_in_directory(filename, dir):
    for root, dirs, files in os.walk(dir):
        if filename in files:
            return os.path.join(root, filename).replace("\\", "/")
    return None


def validate_sensi_config(filepath):
    if os.path.exists(filepath) is False:
        return "{} does not exist".format(filepath)

    sensi_config = pd.read_csv(filepath, sep=r'~', squeeze=True, header=None)
    sensi_config = sensi_config.map(lambda x: re.sub(r'"([^"]*)"', lambda m: re.sub(r';', '_SEMI_COL', m.group()), x))

    sensi_config = pd.concat([
        sensi_config.str.split(';', expand=True),
        sensi_config.str.count(';').rename('_count_sep')
        ], axis=1)

    if sensi_config['_count_sep'].nunique(dropna=True) != 1:
        sensi_config_rows_with_more_columns = sensi_config[
            sensi_config['_count_sep'] > sensi_config.iloc[0]['_count_sep']]['_count_sep']
        sensi_config_rows_with_less_columns = sensi_config[
            sensi_config['_count_sep'] < sensi_config.iloc[0]['_count_sep']]['_count_sep']

        message1 = "" if sensi_config_rows_with_more_columns.empty else "Rows with additional columns are {}".format(list(sensi_config_rows_with_more_columns.index.values))
        message2 = "" if sensi_config_rows_with_less_columns.empty else "Rows with fewer columns are {}".format(list(sensi_config_rows_with_less_columns.index.values))

        return '\n'.join([message1, message2])

    else:
        sensi_config = sensi_config.drop(columns=['_count_sep'])
        sensi_config.columns = sensi_config.iloc[0]
        sensi_config = sensi_config[1:]
        sensi_config.reset_index(drop=True)

    sensi_config_copy = sensi_config

    sensi_config_columns = list(sensi_config_copy.columns)
    message = []

    if len(sensi_config_columns) > len(SENSI_CONFIG_HEADER):
        difference = list(set(sensi_config_columns) - set(SENSI_CONFIG_HEADER))
        for ele in sorted(difference):
            message.append("'Sensi_config.csv': '{}' is extra".format(ele))

    elif len(sensi_config_columns) < len(SENSI_CONFIG_HEADER):
        difference = list(set(SENSI_CONFIG_HEADER) - set(sensi_config_columns))
        for ele in sorted(difference):
            message.append("'Sensi_config.csv': '{}' is missing".format(ele))

    else:
        for index in range(len(sensi_config_columns)):
            if sensi_config_columns[index] != SENSI_CONFIG_HEADER[index]:
                message.append("'Sensi_config.csv': '{}' is incorrect, should be '{}'"
                               .format(sensi_config_columns[index], SENSI_CONFIG_HEADER[index]))

    if message:
        return '\n'.join(message)
    else:
        if sensi_config_copy['Apply stress'].dtype != bool:
            d = {'true': True, 'false': False}
            sensi_config_copy['Apply stress'] = sensi_config_copy['Apply stress'].apply(
                lambda x: x if isinstance(x, bool) or x.lower() not in ['true', 'false'] else d[x.lower()])
            incorrect_values = sensi_config_copy[(sensi_config_copy[['Apply stress']].applymap(type) != bool).any(axis=1)]
            if not incorrect_values.empty:
                return "'Sensi_config.csv': 'Apply stress' has incorrect entry at row(s) {}".format(
                    list(incorrect_values.index.values))

    return sensi_config


def validate_sensi_param(filepath):
    if os.path.exists(filepath) is False:
        return "{} does not exist".format(filepath)

    sensi_param = pd.read_csv(filepath, sep=r'~', squeeze=True, header=None)
    sensi_param = sensi_param.map(lambda x: re.sub(r'"([^"]*)"', lambda m: re.sub(r';', '_SEMI_COL', m.group()), x))

    sensi_param = pd.concat([
        sensi_param.str.split(';', expand=True),
        sensi_param.str.count(';').rename('_count_sep')
        ], axis=1)

    if sensi_param['_count_sep'].nunique(dropna=True) != 1:
        sensi_param_rows_with_more_columns = sensi_param[
            sensi_param['_count_sep'] > sensi_param.iloc[0]['_count_sep']]['_count_sep']
        sensi_param_rows_with_less_columns = sensi_param[
            sensi_param['_count_sep'] < sensi_param.iloc[0]['_count_sep']]['_count_sep']

        message1 = "" if sensi_param_rows_with_more_columns.empty else "Rows with additional columns are {}".format(list(sensi_param_rows_with_more_columns.index.values))
        message2 = "" if sensi_param_rows_with_less_columns.empty else "Rows with fewer columns are {}".format(list(sensi_param_rows_with_less_columns.index.values))

        return '\n'.join([message1, message2])
    else:
        sensi_param = sensi_param.drop(columns=['_count_sep'])
        sensi_param.columns = sensi_param.iloc[0]
        sensi_param = sensi_param[1:]
        sensi_param.reset_index(drop=True)

    sensi_param_copy = sensi_param

    sensi_param_columns = list(sensi_param_copy.columns)
    message = ""

    if sensi_param_columns[0] != 'Name':
        message = "Missing column 'Name' in Sensi_param.csv"

    if message:
        return message

    return sensi_param


def read_sensitivities(env_dir):
    """
    1. Read Sensi_config.csv & Sensi_param.csv in the /sensitivities directory (throw error if column does not match)
    2. Sanitary check for columns in both csv files
    3. Return two dict: sensi_list, param_map
       sensi_list: Name_in_Sensi_config -> [List_of_Stress_name_in_Sensi_config_in_order]
         eg: "Sensi_1" -> ["Stress_vol_1", "Stress_eq_vol_1"]
       param_map: Stress_name_in_Sensi_param -> [List_of_Parameters_syntax_in_Sensi_param]
         eg: "Stress_vol_1" -> ["param.H=(+100)","file::eco[GBP].driver[IR].data.swaptions.mkt[*,1]=(+100)"]
    """
    sensi_list = {}
    param_map = {}
    result = validate_sensi_config(find_file_in_directory('Sensi_config.csv', env_dir))
    if isinstance(result, str):
        raise SensiIOError(result)

    sensi_config = result

    result = validate_sensi_param(find_file_in_directory('Sensi_param.csv', env_dir))
    if isinstance(result, str):
        raise SensiIOError(result)

    sensi_param = result
    sensi_names = sensi_config['Scenario'].unique()
    for sensi in sensi_names:
        sensi_list[sensi] = list(sensi_config["Stress name"][ (sensi_config["Scenario"] == sensi) & (sensi_config["Apply stress"] == True) ])

    # TODO: To cross check the Stress names in the Sensi_param -> To add a unit test
    # Check if colmuns of sensi_config['Stress name'] values all are columns in sensi_param
    if not set(sensi_config['Stress name']).issubset(set(sensi_param.columns)):
        raise SensiIOError("Columns {} in sensi_param do not match the values in sensi_config".format(sensi_config['Stress name'] - set(sensi_param.columns)))

    param_map_unsorted = {}

    for stress_name in list(sensi_param.columns)[1:]:
        # Drop all rows with empty values for that stress_name
        sensi_param_cleaned = sensi_param[['Name', stress_name]]
        sensi_param_cleaned.replace('', np.nan, inplace=True)
        sensi_param_cleaned.dropna(inplace=True)
        # Concatenate values
        sensi_param_cleaned[stress_name] = sensi_param_cleaned['Name'] + '=' + sensi_param_cleaned[stress_name].astype(str)
        param_map_unsorted[stress_name] = sensi_param_cleaned.to_dict('list')[stress_name]

    # Ordering Stress names in param_map following the values in sensi_config.csv
    param_map = {key: param_map_unsorted[key] for key in sensi_config[sensi_config['Apply stress'] == True]['Stress name']}

    return sensi_list, param_map


def create_one_sensi_from_base(sensi_name, base_dir, sensi_path=None, logger=None):
    if sensi_path is not None:
        sensi_path = sensi_path.replace("\\", '/')
        try:
            # Re-copy all files
            log(f"Copying files to {sensi_path}", logger)
            sensi_rsrc_dir = os.path.join(sensi_path, "resources").replace("\\", "/")
            sensi_rsrc_admin_dir = os.path.join(sensi_path, "resources_admin").replace("\\", "/")
            base_rsrc_dir = os.path.join(base_dir, "resources").replace("\\", "/")
            base_rsrc_admin_dir = os.path.join(base_dir, "resources_admin").replace("\\", "/")
            if os.path.exists(sensi_rsrc_dir):
                shutil.rmtree(sensi_rsrc_dir)

            if os.path.exists(base_rsrc_dir):
                shutil.copytree(base_rsrc_dir, sensi_rsrc_dir)

            if os.path.exists(sensi_rsrc_admin_dir):
                shutil.rmtree(sensi_rsrc_admin_dir)

            if os.path.exists(base_rsrc_admin_dir):
                shutil.copytree(base_rsrc_admin_dir, sensi_rsrc_admin_dir)

        except Exception as exc:
            log(f"Exception {exc}", logger)
            return SensiIOError(f"Unable to copy files to {sensi_name}: {exc}")

        try:
            settings_json_patj = f"{sensi_path}/resources/settings.json"
            settings_json_sensi = read_json_file(settings_json_patj)
            settings_json_sensi['gen_param']['name'] = sensi_name
            settings_json_sensi['gen_param']['path'] = sensi_path
            log(f"Writing settings.json to {sensi_path}", logger)
            with open(settings_json_patj, 'w') as f:
                f.write(json.dumps(settings_json_sensi, indent=4))
        except Exception as err:
            log(f"Exception {err}", logger)
            return SensiIOError("Unable to read/write settings.json to {}".format(sensi_name))

    return sensi_path


class SensiConfig:
    def __init__(self, env_dir, logger=None):
        if not os.path.exists(env_dir):
            raise SensiIOError("Base table {} does not exist".format(env_dir))
        self.base_dir = env_dir
        self.settings_json = read_json_file(f'{env_dir}/resources/settings.json')
        self.sensi_list, self.param_map = read_sensitivities(self.base_dir)
        self.logger = logger

    def get_stress_desc(self, sensi_name):
        param_list = self.sensi_list.get(sensi_name, [])
        return "".join([">>".join(self.param_map.get(p, [""])) for p in param_list])

    def create_tables(self, sensi_dirs={}):
        # For Seni_config.csv
        # To new create directory from the name of the Scenario
        # Copy env_dir to each directory of the name of the Scenario
        # Replace gen_param.name = name of the Scenario in the settings.json of the newly copied directory
        # Replace gen_param.path = newly created path
        # Input sensi_dirs can be provided by the API as dict { "<SENSI_NAME>":"<TABLE_ENV_PATH>" }
        # If sensi_dirs is provided, only the tables for the Sensi there are created
        # Else all the tables are created for every sensi in sensi_list
        # Dict that contains the list of sensi and their dirs
        processed_sensi_dirs = {}
        if len(self.sensi_list)>0:
            if len(sensi_dirs)>0:
                for sensi in self.sensi_list.keys():
                    if sensi in sensi_dirs.keys():
                        log(f"Creating sensi {sensi} from base table {self.base_dir} to {sensi_dirs[sensi]}", self.logger)
                        res = create_one_sensi_from_base(sensi, self.base_dir, sensi_dirs[sensi], self.logger)
                        if res is not None:
                            processed_sensi_dirs[sensi] = res
            else:
                path = Path(self.base_dir)
                parent_dir = path.parent
                for sensi in self.sensi_list.keys():
                    res = create_one_sensi_from_base(sensi, self.base_dir, os.path.join(parent_dir, sensi))
                    if res is not None:
                        processed_sensi_dirs[sensi] = res

        return processed_sensi_dirs

    def apply(self, sensi_dirs={}):
        # For Sensi_param.csv
        # Iterate over sensi_list and apply the stress in the param_map
        # When interate param_map:
        # Build the good correct path from the json query
        # Call syntax.apply_sentax_to_file(path, syntax) in the syntax.py
        # Input sensi_dirs can be provided by the API as dict { "<SENSI_NAME>":"<TABLE_ENV_PATH>" }
        # If sensi_dirs is provided, only Sensi in sensi_dirs are stress applied
        # Else all the sensis are stress applied
        # Dict that contains the list of sensi and their dirs
        sensi_dirs_to_process = {}
        processed_sensi_messages = {}
        if len(self.sensi_list)>0:
            if len(sensi_dirs)>0:
                # print(self.sensi_list)
                for sensi in self.sensi_list.keys():
                    if sensi in sensi_dirs.keys():
                        sensi_dirs_to_process[sensi] = sensi_dirs[sensi].replace('\\', '/')
            else:
                path = Path(self.base_dir)
                parent_dir = path.parent
                for sensi in self.sensi_list.keys():
                    sensi_dirs_to_process[sensi] = os.path.join(parent_dir, sensi).replace('\\', '/')
        else:
            return sensi_dirs_to_process

        if len(self.param_map)>0:
            # Read settings.json from each sensi dir and apply changes
            for sensi_name, sensi_dirpath in sensi_dirs_to_process.items():
                log(f"Applying stresses of sensi {sensi_name} in {sensi_dirpath}", self.logger)
                if os.path.exists(sensi_dirpath):
                    try:
                        settings_json_sensi = read_json_file(os.path.join(sensi_dirpath, 'resources/settings.json').replace("\\", "/"))
                    except Exception as err:
                        processed_sensi_messages[sensi_name] = SensiIOError("Unable to read settings.json in {}: {}".format(sensi_name, err))
                        continue

                    if settings_json_sensi is not None:
                        settings_modif_express = list()
                        settings_modif_values = list()
                        for stress_name in self.sensi_list[sensi_name]:
                            log(f"Applying stress {stress_name} to {sensi_name}", self.logger)
                            counter = 0
                            for command in self.param_map[stress_name]:
                                try:
                                    syntax = syn.parse_param(command)
                                    if syntax.expression.startswith("$"):
                                        path_to_file = syn.get_input_file_path(settings_json_sensi, syntax.expression, sensi_dirpath)
                                        # Apply the changes to the input file using the syntax
                                        applied = syn.apply_syntax_to_file(path_to_file, syntax, settings_json_sensi)
                                        if applied:
                                            counter += 1
                                            processed_sensi_messages[sensi_name] = "Applied {} modification(s) on input files of {}".format(counter, sensi_name)
                                            log(processed_sensi_messages[sensi_name], self.logger)
                                        else:
                                            # print("Failed to apply a syntax to {}".format(path_to_file))
                                            processed_sensi_messages[sensi_name] = SensiIOError("Failed to apply a modification to {}".format(path_to_file))
                                            log(processed_sensi_messages[sensi_name].msg, self.logger)
                                            break
                                    else:
                                        try:
                                            table_name = syn.query(settings_json_sensi, "$.framework.sensi_1.name")
                                            expression = syntax.expression
                                            if not syntax.expression.startswith("framework"):
                                                expression = "framework.sensi[{}].{}".format(table_name, syntax.expression)
                                            settings_modif_express.append(expression)
                                            settings_modif_values.append(syntax.value)
                                            log("Added {} to settings_modif".format(expression), self.logger)
                                        except syn.SensiSyntaxError:
                                            processed_sensi_messages[sensi_name] = SensiIOError("Unable to add {} to settings_modif because no table name is found in settings_json".format(syntax.expression))

                                        continue
                                except syn.SensiSyntaxError as err:
                                    processed_sensi_messages[sensi_name] = SensiIOError(err.msg)
                                    log(processed_sensi_messages[sensi_name].msg, self.logger)
                                    break

                        # Saving settings_modif commands to settings_modif.csv
                        if len(settings_modif_express)>0 and len(settings_modif_values)>0:
                            settings_modif_pd = pd.DataFrame({"id": settings_modif_express, "value": settings_modif_values})
                            settings_modif_pd.to_csv(os.path.join(sensi_dirpath, 'resources/settings_modif.csv'), sep=";", index=False)
                            log(f"settings_modif.csv of {sensi_name} saved", self.logger)
                else:
                    processed_sensi_messages[sensi_name] = SensiIOError("Sensitivity path does not exist")

        return processed_sensi_messages

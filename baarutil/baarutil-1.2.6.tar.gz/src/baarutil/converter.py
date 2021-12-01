import traceback
import pandas as pd
import numpy as np
from Crypto.Cipher import AES
import base64
from robot.libraries.BuiltIn import BuiltIn
from robot.libraries.BuiltIn import _Misc
import robot.api.logger as logger
from robot.api.deco import keyword
import os
import sys
import json


def get_python_path():
    path = os.path.split(sys.executable)
    return path


def read_convert(input_str: str) -> list:
    """This function reads the string format and then converts it to a dictionary of lists"""
    dict_list = []
    try:
        inputs = input_str.split("__::__")
        for lines in inputs:
            line_dict = {}
            line = lines.split("__$$__")
            for l in line:
                dict_value = l.split("__=__")
                key = dict_value[0]
                if len(dict_value) == 1:
                    value = ""
                else:
                    value = dict_value[1]
                if key != "":
                    line_dict[key] = value
            dict_list.append(line_dict)
    except Exception as e:
        print(traceback.format_exc(), flush=True)
    return dict_list


def write_convert(input_list: list) -> str:
    """This function reads convert the list of dictionaries(Tabular format) to a string format"""
    output_str = ""
    try:
        for dicts in input_list:
            for key, value in dicts.items():
                output_str = output_str + key + "__=__" + value
                output_str = output_str + "__$$__"
            output_str = output_str[:len(output_str) - 6]
            output_str = output_str + "__::__"
        output_str = output_str[:len(output_str) - 6]
    except Exception as e:
        print(traceback.format_exc(), flush=True)
    return output_str


def string_to_df(input_str: str, rename_cols: dict = {}, drop_dupes=False) -> pd.DataFrame():
    """This function converts the string format to a DataFrame"""
    final_dataframe = pd.DataFrame()
    try:
        for index, data_list in enumerate(input_str.split('__::__')):
            if str(data_list) == '':
                continue
            for each_data in data_list.split('__$$__'):
                if each_data == '':
                    continue
                if '__=__' in each_data:
                    final_dataframe.at[index, str(each_data.split('__=__')[0])] = str(each_data.split('__=__')[1])
        if len(rename_cols) != 0:
            try:
                final_dataframe = final_dataframe.rename(rename_cols, axis=1)
            except Exception as e:
                print(traceback.format_exc(), flush=True)
        if drop_dupes:
            final_dataframe = final_dataframe.drop_duplicates()
        final_dataframe = final_dataframe.replace(np.nan, '', regex=True)
    except Exception as e:
        print(traceback.format_exc(), flush=True)
    return final_dataframe


def df_to_string(input_df: pd.DataFrame(), rename_cols: dict = {}, drop_dupes=False) -> str:
    """This function converts a DataFrame to the string format"""
    final_string = ''
    try:
        input_df = input_df.replace(np.nan, '', regex=True)
        if len(rename_cols) != 0:
            try:
                input_df = input_df.rename(rename_cols, axis=1)
            except Exception as e:
                print(traceback.format_exc(), flush=True)
        if drop_dupes:
            input_df = input_df.drop_duplicates()
        for data_dict in input_df.to_dict('r'):
            for key in data_dict.keys():
                final_string += str(key) + '__=__' + str(data_dict[key]) + '__$$__'
            final_string += '__::__'
    except Exception as e:
        print(traceback.format_exc(), flush=True)
    return final_string


def df_to_listdict(input_df: pd.DataFrame(), rename_cols: dict = {}, drop_dupes=False) -> list:
    """This function converts a DataFrame to the string format"""
    final_list = []
    try:
        input_df = input_df.replace(np.nan, '', regex=True)
        if len(rename_cols) != 0:
            try:
                input_df = input_df.rename(rename_cols, axis=1)
            except Exception as e:
                print(traceback.format_exc(), flush=True)
        if drop_dupes:
            input_df = input_df.drop_duplicates()
        final_list = input_df.to_dict('r')
    except Exception as e:
        print(traceback.format_exc(), flush=True)
    return final_list


def perform_base_decryption(encrypted_message: str, config_file: str = 'baarutil_config.json') -> str:
    """This function decrypts the Old Baar Vault Encrypted info"""
    decrypted_text = ''
    key = ''
    iv = ''
    key_name = ''
    iv_name = ''
    py_path = get_python_path()
    if len(py_path) != 0:
        config_path = os.path.join(py_path[0], 'Scripts', config_file)
        if os.path.isfile(config_path):
            try:
                config_json = open(config_path)
                config_data = json.load(config_json)
                if 'key_mapping' in config_data.keys() and 'key_value' in config_data.keys():
                    if 'key' in config_data['key_mapping'].keys() and 'iv' in config_data['key_mapping'].keys():
                        key_name = config_data['key_mapping']['key']
                        iv_name = config_data['key_mapping']['iv']
                        if key_name in config_data['key_value'].keys() and iv_name in config_data['key_value'].keys():
                            key = config_data['key_value'][key_name]
                            iv = config_data['key_value'][iv_name]
                            # ~~~~~~~~ Starting Decryption ~~~~~~~~
                            decrypted_text = base64.urlsafe_b64decode(encrypted_message)
                            decipher = AES.new(bytes(key, encoding='utf-8'), AES.MODE_CBC, bytes(iv, encoding='utf-8'))
                            decrypted_bytes = decipher.decrypt(decrypted_text)
                            decrypted_text = decrypted_bytes.decode('utf-8')
                            unpad = lambda s: s[0:-ord(s[-1])]
                            decrypted_text = unpad(decrypted_text)
                        else:
                            print('Decryption failed! Incorrect config (unknown vey value Pair):', config_path, flush=True)
                    else:
                        print('Decryption failed! Incorrect config (missing key and iv):', config_path, flush=True)
                else:
                    print('Decryption failed! Incorrect config:', config_path, flush=True)
            except Exception as e:
                print(traceback.format_exc(), flush=True)
                pass
        else:
            print('Decryption failed! Missing config file:', config_path, flush=True)
    return decrypted_text


@keyword("Decrypt Vault")
def decrypt_vault(encrypted_message: str, config_file: str = 'baarutil_config.json') -> str:
    """This function decrypts the Baar Vault Encrypted info 2.0"""
    try:
        # This will set the Log Level to NONE if it is called from a Robot Framework script
        BuiltIn.log_to_console(BuiltIn(), 'Setting Log Level from INFO to NONE!')
        old = _Misc.set_log_level(_Misc(), level='NONE')
    except:
        pass
    decrypted_string = ''
    try:
        if len(encrypted_message) != 0:
            decrypted_text = base64.b64decode(encrypted_message)
            decrypt_str = decrypted_text.decode(encoding='utf-8')
            split_num = int(decrypt_str[-1])
            decrypt_str = decrypt_str[:-1]
            split_strings = [decrypt_str[index: index + split_num] for index in range(0, len(decrypt_str), split_num)]
            extracted_string = "".join([split_strings[index] for index in range(len(split_strings)) if index == 0 or index % 2 == 0])
            extracted_string = extracted_string.rstrip('@')
            layer_num = int(extracted_string[-1])
            decrypted_string = extracted_string[:-1]
            for iiter in range(0, layer_num + 1):
                decrypted_string = perform_base_decryption(decrypted_string)
        else:
            print('Decryption failed! Encrypted data is empty', flush=True)
    except Exception as e:
        print('Decryption failed! Incorrect Encrypted data.', flush=True)
        print(traceback.format_exc(), flush=True)
    return decrypted_string
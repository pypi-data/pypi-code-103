"""
  Copyright (c) 2016- 2021, Wiliot Ltd. All rights reserved.

  Redistribution and use of the Software in source and binary forms, with or without modification,
   are permitted provided that the following conditions are met:

     1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

     2. Redistributions in binary form, except as used in conjunction with
     Wiliot's Pixel in a product or a Software update for such product, must reproduce
     the above copyright notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the distribution.

     3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
     may be used to endorse or promote products or services derived from this Software,
     without specific prior written permission.

     4. This Software, with or without modification, must only be used in conjunction
     with Wiliot's Pixel or with Wiliot's cloud service.

     5. If any Software is provided in binary form under this license, you must not
     do any of the following:
     (a) modify, adapt, translate, or create a derivative work of the Software; or
     (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
     discover the source code or non-literal aspects (such as the underlying structure,
     sequence, organization, ideas, or algorithms) of the Software.

     6. If you create a derivative work and/or improvement of any Software, you hereby
     irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
     royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
     right and license to reproduce, use, make, have made, import, distribute, sell,
     offer for sale, create derivative works of, modify, translate, publicly perform
     and display, and otherwise commercially exploit such derivative works and improvements
     (as applicable) in conjunction with Wiliot's products and services.

     7. You represent and warrant that you are not a resident of (and will not use the
     Software in) a country that the U.S. government has embargoed for use of the Software,
     nor are you named on the U.S. Treasury Department’s list of Specially Designated
     Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
     You must not transfer, export, re-export, import, re-import or divert the Software
     in violation of any export or re-export control laws and regulations (such as the
     United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
     and use restrictions, all as then in effect

   THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
   OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
   WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
   QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
   IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
   ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
   OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
   FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
   (SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
   (A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
   (B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
   (C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""
from enum import Enum

from yoctopuce.yocto_temperature import *
import http.client
import mimetypes
from codecs import encode
import threading
import logging
import traceback
import json
import serial.tools.list_ports
import time
import pandas as pd
import os
from csv import writer
import ast
from threading import Event
import numpy as np
import statistics
from queue import Queue


###########################################
#            Tester Management            #
###########################################


class TesterName(Enum):
    """
    determines tester type (affects output file format set in class CsvLog)
    """
    OFFLINE = 'offline'
    TAL15K = 'tal15k'
    CONVERSION = 'conversion'
    NONE = ''


class HeaderType(Enum):
    """
    determines which output file is generated in class CsvLog (run data or tags data)
    """
    TAG = 'tag'
    RUN = 'run'
    NONE = ''


def get_ports(device_name):
    """
    search the com ports for the desired device (arduino/ gw)
    :type device_name: string
    :param device_name: arduino or gw (gateway)
    :return: ports list of the desired devices
    """
    if device_name == 'gw' or device_name == 'gateway':
        str_device = 'Wiliot GW'
        baud = 921600
    elif device_name == 'arduino':
        str_device = 'Wiliot Tester GPIO unit'
        baud = 1000000
    else:
        print("please selecet a valid device names: {'gw','arduino'}")
        return []
    ports = list(serial.tools.list_ports.comports())
    device_ports = []
    for p in ports:
        try:
            s = serial.Serial(port=p.device, baudrate=baud, timeout=1)
            if s.isOpen():
                s.write(b'*IDN?')
                current_device = s.readline()
                if str_device in current_device.decode():
                    device_ports.append(p.device)
                    print(current_device.decode())
                s.close()
        except (OSError, serial.SerialException):
            pass
        except Exception as e:
            raise(e)
    return device_ports


def set_temperature():
    """
    initialize yocto temperature sensor
    :return: current temperature
    """
    # object tenp sens
    errmsg = YRefParam()
    if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
        sys.exit("init error :" + errmsg.value)
    cur_temp = YTemperature.FirstTemperature()
    print("Temp :  " + "%2.3f" % cur_temp.get_currentValue() + "°C (Ctrl-C to stop)")
    return cur_temp


def print_exception(exception_details, printing_lock=None):
    """
    prints an exception to screen and to log
    :type exception_details: type(sys.exc_info())
    :param exception_details: desired printed exception
    :type printing_lock: threading.Lock()
    :param printing_lock: lock for printing
    """
    # print except - print_lock if None nothing else with
    exc_type, exc_obj, exc_trace = exception_details
    # deal with the exception
    if printing_lock is not None:
        with printing_lock:
            print('Exception details: ')
            print(exc_type)
            print(exc_obj)
            traceback.print_tb(exc_trace, limit=None, file=None)
    else:
        print('Exception details: ')
        print(exc_type)
        print(exc_obj)
        traceback.print_tb(exc_trace, limit=None, file=None)
    try:
        logging.warning('Exception details: exc_type = {}, exc_obj = {}'.format(exc_type, exc_obj))
    except Exception:
        pass


def config_gw(gw_obj, rssi_threshold=None, energizing_pattern=None, tx_power=None, time_profile=None, pl_delay=None,
              set_interrupt=None):
    """
    :type gw_obj: WiliotGateway
    :type rssi_threshold: int or str
    :type energizing_pattern: int or str
    :type tx_power:  int or str
    :type time_profile:  list or str
    :type pl_delay: int or str
    :type set_interrupt: bool

    :param gw_obj:
    :param rssi_threshold:
    :param energizing_pattern:
    :param tx_power:
    :param time_profile:
    :param pl_delay:
    :param set_interrupt:
    :return:
    """
    # print version
    print('{}={}'.format(gw_obj.hw_version, gw_obj.sw_version))
    # config:
    if energizing_pattern is not None:
        int_energizing_pattern = int(energizing_pattern)
    else:
        int_energizing_pattern = None
    if time_profile is not None:
        if isinstance(time_profile, str):
            time_profile = [int(time_profile.split(',')[0]), int(time_profile.split(',')[1])]
        else:
            print("time_profile can be a string 'x,x' or list of int [5,15]")
    gw_obj.config_gw(filter_val=False, pacer_val=0, energy_pattern_val=int_energizing_pattern,
                     time_profile_val=time_profile, received_channel=37, modulation_val=True)
    if set_interrupt is not None:
        gw_obj.write('!pl_gw_config {}'.format(int(set_interrupt)))
        time.sleep(0.002)
    if rssi_threshold is not None:
        gw_obj.write('!set_rssi_th {}'.format(hex(int(rssi_threshold))))
        time.sleep(0.002)
        gw_obj.write('!send_rssi_config 1')
        time.sleep(0.002)
    if tx_power is not None:
        gw_obj.write('!output_power pos{}dBm'.format(tx_power))
        time.sleep(0.002)
    if pl_delay is not None:
        gw_obj.write('!set_pl_delay {}'.format(pl_delay))


def encrypted_packet_decoder(processed_data):
    """
    extracts only the data relevant to the tester
    :type processed_data: dictionary (output of WiliotGateway.get_data())
    :return dictionary of relevant fields
    """
    packet_dict = {'advAddress': processed_data['adv_address'],
                   'packet_time': processed_data['time_from_start'],
                   'raw_data': processed_data['packet'],
                   'rssi': processed_data['rssi']}

    return packet_dict


def open_json(folder_path, file_path, default_values=None):
    """
    opens config json
    :type folder_path: string
    :param folder_path: the folder path which contains the desired file
    :type file_path: string
    :param file_path: the file path which contains the json
            (including the folder [file_path = folder_path+"json_file.json"])
    :type default_values: dictionary
    :param default_values: default values for the case of empty json
    :return: the desired json object
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_exists = os.path.isfile(file_path)
    if not file_exists or os.stat(file_path).st_size == 0:
        # save the default values to json
        with open(file_path, "w") as out_file:
            json.dump(default_values, out_file)

        return json.load(open(file_path, "rb"))
    else:
        with open(file_path) as f:
            json_content = f.read()
        if len(json_content) == 0:
            with open(file_path, "w") as out_file:
                json.dump(default_values, out_file)
            json_content = json.load(open(file_path, "rb"))
        else:
            json_content = json.loads(json_content)
        return json_content


###########################################
#              Tester Classes             #
###########################################

class CounterThread(threading.Thread):
    """
    a class that manages and interacts with arduino_counter code

    Parameters:
        @type stop: Event
        @param stop: when set, close the port and exit
        @type printing_lock: threading.Lock
        @param printing_lock: a lock to access screen printing
        @type arduino_ports: list
        @param arduino_ports: list of arduino ports connected to PC

        global param tested: will use a global variable called tested

    Exceptions: None

    Events:
        listen/ waits on:
            stop => when set, close the port and exit

    Logging:
        debug: 'Warning: Could not decode counter data'
    """

    def __init__(self, stop: Event, printing_lock, arduino_ports):
        super(CounterThread, self).__init__()
        self.stop = stop
        self.printing_lock = printing_lock
        self.port = arduino_ports
        if len(self.port) > 1:
            print("too many USB Serial Device connected, can't figure out which is the counter")
        elif len(self.port) < 1:
            print("No USB Serial Device connected, please connect the counter")
        else:  # there is only one port of usb that is not GW
            self.port = self.port[0]
        self.baud = '9600'
        self.comPortObj = serial.Serial(self.port, self.baud, timeout=0.1)

    def run(self):
        global tested
        while not self.stop.isSet():
            data = self.comPortObj.readline()
            buf = b''
            if data.__len__() > 0:
                buf += data
                if b'\n' in buf:
                    try:
                        tmp = buf.decode().strip(' \t\n\r')
                        if "pulses detected" in tmp:
                            tested += 1

                    except Exception:
                        with self.printing_lock:
                            print('Warning: Could not decode counter data')
                        logging.debug('Warning: Could not decode counter data')
                        continue

        self.comPortObj.close()


###########################################
#              Cloud Functions            #
###########################################


def get_new_token_api():
    """
    uses user name and password to get a token for uploading files
    saves the Bearer token to Json
    return: True if got token and saved it successfully False otherwise
    """
    folder_path = 'configs'
    cfg_file_name = 'user_configs.json'
    save_the_auth_res = True
    # if file or folder doesn't exist will create json file with Authorization = 'None' and raise exception
    if os.path.isdir(folder_path):
        file_path = os.path.join(folder_path, cfg_file_name)
        if os.path.exists(file_path):
            cfg_data = open_json(folder_path=folder_path, file_path=os.path.join(folder_path, cfg_file_name))
            try:
                user_name = cfg_data['UserName']
                password = cfg_data['Password']
                OwnerId = cfg_data['OwnerId']
            except Exception:
                save_the_auth_res = False
                print("Config file was missing some variables and was updated")
                with open(file_path, 'w') as cfg:
                    json.dump({"Authorization": "None", "UserName": "None", "Password": "None", "OwnerId": "None"}, cfg)
                raise Exception('user_config.json was missing variables and was updated\n'
                                'to Upload files please insert your FusionAuth User name and Password in file:\n'
                                'wiliot_testers/offline/configs/user_configs.json\n')
        else:
            save_the_auth_res = False
            print("Config file doesn't exist\n Creating user_config.json")
            with open(file_path, 'w') as cfg:
                json.dump({"Authorization": "None", "UserName": "None", "Password": "None", "OwnerId": "None"}, cfg)
            raise Exception('user_config.json was created\n'
                            'to Upload files please insert your FusionAuth User name and Password in file:\n'
                            'wiliot_testers/offline/configs/user_configs.json')
    else:
        save_the_auth_res = False
        print("'wiliot_testers/offline/configs' directory doesn't exist\n Creating directory and user_config.json")
        os.mkdir(folder_path)
        file_path = os.path.join(folder_path, cfg_file_name)
        with open(file_path, 'w') as cfg:
            json.dump({"Authorization": "None", "UserName": "None", "Password": "None", "OwnerId": "None"}, cfg)
        raise Exception('user_config.json was created \n'
                        'to Upload files please insert your User name and Password in file:\n'
                        'wiliot_testers/offline/configs/user_configs.json\n')
    if user_name == 'None' or password == 'None':
        print('Unable to get token from cloud because the user_name or password were not documented\n'
              'to Upload files please insert your FusionAuth User name and Password in file:\n'
              'configs/user_configs.json\n')

    conn = http.client.HTTPSConnection("api.wiliot.com")
    payload = ''
    headers = {}
    url = "/v1/auth/token?username=" + user_name + '&password=' + password
    conn.request("POST", url, payload, headers)
    res = conn.getresponse()
    data = res.read()

    if str(res.status) == '500':
        print('There was a problem at the Server side (status 500), '
              'please try get_new_token_api() again or reach Wiliot')
        return False
    elif str(res.status) == '401':
        print('There was a problem with the authorization (status 401),\n '
              'Please make sure your user name and password in wiliot_testers/offline/configs/user_configs.json'
              ' is correct or reach Wiliot')
        return False
    elif str(res.status)[0:2] == '40':
        print('There was a problem at the request side (status 40*), '
              'please try get_new_token_api() again or reach Wiliot')
        print('Status code is: ' + str(res.status))
        return False
    elif str(res.status) == '200':
        print('The token drawn successfully from Wiliot cloud')

    res_dict = ast.literal_eval(data.decode("utf-8"))
    if save_the_auth_res:
        with open(file_path, 'w') as cfg:
            try:
                json.dump({"Authorization": res_dict['access_token'], "UserName": cfg_data['UserName'],
                           "Password": cfg_data['Password'], "OwnerId": cfg_data['OwnerId']}, cfg)
                return True
            except Exception:
                json.dump({"Authorization": 'None', "UserName": cfg_data['UserName'],
                           "Password": cfg_data['Password'], "OwnerId": cfg_data['OwnerId']}, cfg)
                raise Exception('failed to get token from cloud')


def upload_to_cloud_api(batch_name, tester_type, run_data_csv_name=None, tags_data_csv_name=None, to_logging=False,
                        env='prod', is_batch_name_inside_logs_folder=True):
    """
    uploads a tester log to Wiliot cloud
    :type batch_name: string
    :param batch_name: folder name of the relevant log
    :type run_data_csv_name: string
    :param run_data_csv_name: name of desired run_data log to upload,
                              should contain 'run_data' and end with .csv
    :type tags_data_csv_name: string
    :param tags_data_csv_name: name of desired tags_data log to upload,
                               should contain 'tags_data' and end with .csv
    :type tester_type: string
    :param tester_type: name of the tester the run was made on (offline, tal15k, conversion)
    :type to_logging: bool
    :param to_logging: if true, write to logging.debug the result of the upload
    :type env: string (prod, dev, test)
    :param env: to what cloud environment should we upload the files
    :type is_batch_name_inside_logs_folder: bool
    :param is_batch_name_inside_logs_folder: flag to indicate if the batch_name is the regular run folder (logs) or
                                             this function is being used in a way we will need the full path
    :return: True for successful upload, False otherwise
    """
    if tester_type not in ['offline', 'tal15k', 'conversion']:
        print('Unsupported tester_type inserted to upload_to_cloud_api()\nPlease change it and retry')
        return
    if run_data_csv_name is not None and 'run_data' not in run_data_csv_name:
        print('Unsupported run_data_csv_name inserted to upload_to_cloud_api()\nPlease change it and retry')
        return
    if tags_data_csv_name is not None and 'tags_data' not in tags_data_csv_name:
        print('Unsupported tags_data_csv_name inserted to upload_to_cloud_api()\nPlease change it and retry')
        return
    folder_path = 'configs'
    cfg_file_name = 'user_configs.json'
    # if file or folder doesn't exist will create json file with Authorization = 'None' and raise exception
    if not get_new_token_api():
        raise Exception('get_new_token_api() failed')

    if os.path.isdir(folder_path):
        file_path = os.path.join(folder_path, cfg_file_name)
        if os.path.exists(file_path):
            cfg_data = open_json(folder_path=folder_path, file_path=os.path.join(folder_path, cfg_file_name))
            bearer_token = cfg_data['Authorization']
        else:
            print("Config file doesn't exist\n Creating user_config.json")
            with open(file_path, 'w') as cfg:
                json.dump({"Authorization": "None", "OwnerId": "None"}, cfg)
            raise Exception('user_config.json was created\n')
    else:
        print("'wiliot_testers/offline/configs' directory doesn't exist\n Creating directory and user_config.json")
        os.mkdir(folder_path)
        file_path = os.path.join(folder_path, cfg_file_name)
        with open(file_path, 'w') as cfg:
            json.dump({"Authorization": "None", "OwnerId": "None"}, cfg)
        raise Exception('user_config.json was created to Upload files '
                        'please insert your OwnerId Bearer token in file:\n'
                        'wiliot_testers/offline/configs/user_configs.json under \n'
                        '"Authorization": "<enter your Bearer token here>"\n')
    print('Upload to cloud has began\nWaiting for the server response, please wait...')
    conn = http.client.HTTPSConnection("api.wiliot.com")
    boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
    headers = {
        'Authorization': 'Bearer ' + bearer_token,
        'Content-type': 'multipart/form-data; boundary={}'.format(boundary)
    }

    if env == 'prod':
        url = "/v1/" + str(cfg_data['OwnerId']) + "/upload/testerslogs/"
    elif env == 'test':
        url = "/test/v1/" + str(cfg_data['OwnerId']) + "/upload/testerslogs/"
    elif env == 'dev':
        url = "/dev/v1/" + str(cfg_data['OwnerId']) + "/upload/testerslogs/"
    else:
        print('unsupported env value was inserted (env = ' + str(env) + ')')
        return False

    if run_data_csv_name is not None:
        print("Run data csv upload started")
        if to_logging:
            logging.debug("Run data csv upload started")
        data_list = []
        data_list.append(encode('--' + boundary))
        if is_batch_name_inside_logs_folder:
            run_data_path = 'logs/' + batch_name
        else:
            run_data_path = batch_name
        run_data_path = os.path.join(run_data_path, run_data_csv_name)

        if not os.path.exists(run_data_path):
            exception_string = str(run_data_path) + ' run_data_path could not be found \n' + \
                               'please find it and try to upload again'
            raise Exception(exception_string)

        data_list.append(encode('Content-Disposition: form-data; name=file; filename={0}'.format(run_data_path)))
        file_type = mimetypes.guess_type(run_data_path)[0] or 'application/octet-stream'
        data_list.append(encode('Content-Type: {}'.format(file_type)))
        data_list.append(encode(''))
        with open(run_data_path, 'rb') as f:
            data_list.append(f.read())
        data_list.append(encode('--' + boundary + '--'))
        data_list.append(encode(''))
        body = b'\r\n'.join(data_list)
        payload = body
        if 'offline' in tester_type:
            url += 'offline-tester-runs-indicators'
        elif 'tal15k' in tester_type:
            url += 'tal15k-tester-runs-indicators'
        elif 'conversion' in tester_type:
            url += 'conversion-tester-runs-indicators'

        conn.request("POST", url, payload, headers)
        run_data_res = conn.getresponse()
        run_data_data = run_data_res.read()
        print("answer from cloud is:")
        print(run_data_data.decode("utf-8"))
        if to_logging:
            logging.debug("answer from cloud is:")
            logging.debug(run_data_data.decode("utf-8"))
        if str(run_data_res.status) == '500':
            print('There was a problem at the Server side (status 500), please try to upload again or reach Wiliot')
            return False
        elif str(run_data_res.status) == '401':
            print('There was a problem with the authorization (status 401),\n '
                  'Please make sure your user name and password in wiliot_testers/offline/configs/user_configs.json'
                  ' is correct or reach Wiliot')
            return False
        elif str(run_data_res.status)[0:2] == '40':
            print('There was a problem with the request (status 40*), please try to upload again or reach Wiliot')
            print('Status code is: ' + str(run_data_res.status))
            return False
        elif str(run_data_res.status) == '200':
            print('The file "' + run_data_csv_name + '" was uploaded successfully to Wiliot cloud')

    if tags_data_csv_name is not None:
        print("Tags data csv upload started")
        if to_logging:
            logging.debug("Tags data csv upload started")
        data_list = []
        data_list.append(encode('--' + boundary))
        if is_batch_name_inside_logs_folder:
            tags_data_path = 'logs/' + batch_name
        else:
            tags_data_path = batch_name
        tags_data_path = os.path.join(tags_data_path, tags_data_csv_name)
        if not os.path.exists(tags_data_path):
            exception_string = str(tags_data_path) + ' tags_data_path could not be found \n' + \
                               'please find it and try to upload again'
            raise Exception(exception_string)
        data_list.append(encode('Content-Disposition: form-data; name=file; filename={0}'.format(tags_data_path)))
        file_type = mimetypes.guess_type(tags_data_path)[0] or 'application/octet-stream'
        data_list.append(encode('Content-Type: {}'.format(file_type)))
        data_list.append(encode(''))
        with open(tags_data_path, 'rb') as f:
            data_list.append(f.read())
        data_list.append(encode('--' + boundary + '--'))
        data_list.append(encode(''))
        body = b'\r\n'.join(data_list)
        payload = body
        if 'offline' in tester_type:
            url += 'offline-tester-tags-indicators'
        elif 'tal15k' in tester_type:
            url += 'tal15k-tester-tags-indicators'
        elif 'conversion' in tester_type:
            url += 'conversion-tester-tags-indicators'

        conn.request("POST", url, payload, headers)
        tags_data_res = conn.getresponse()
        tags_data_data = tags_data_res.read()
        print("answer from cloud is:")
        print(tags_data_data.decode("utf-8"))
        if to_logging:
            logging.debug("answer from cloud is:")
            logging.debug(tags_data_data.decode("utf-8"))
        if str(tags_data_res.status) == '500':
            print('There was a problem at the Server side (status 500), please try to upload again or reach Wiliot')
            return False
        elif str(tags_data_res.status) == '401':
            print('There was a problem with the authorization (status 401),\n '
                  'Please make sure your user name and password in wiliot_testers/offline/configs/user_configs.json'
                  ' is correct or reach Wiliot')
            return False
        elif str(tags_data_res.status)[0:2] == '40':
            print('There was a problem at the request side (status 40*), please try to upload again or reach Wiliot')
            print('Status code is: ' + str(tags_data_res.status))
            return False
        elif str(tags_data_res.status) == '200':
            print('The file "' + tags_data_csv_name + '" was uploaded successfully to Wiliot cloud')
    print('-----------------------------------------------------------------------\n'
          'upload to cloud is finished successfully, the program will end now\n'
          '-----------------------------------------------------------------------')
    return True


def get_encryption_key_from_cloud_api(username, password, group_id):
    """
    gets the encryption key for the tags at this run
    :type username: string
    :param username: Wiliot user name for accessing the data
    :type password: string
    :param password: Wiliot password name for accessing the data
    :type group_id: string
    :param group_id: tags group_id
    :return: the desired encryption keys
    """
    try:
        conn = http.client.HTTPSConnection("api.wiliot.com")
        headers = {'accept': "application/json"}
        payload = ''
        conn.request("POST", "/dev/v1/auth/token?password=" + password + "&username=" + username, payload,
                     headers=headers)
        res = conn.getresponse()
        data = res.read()
        tokens = json.loads(data.decode("utf-8"))
        token = tokens['access_token']
        payload = json.dumps({
            "groupId": group_id
        })
        headers = {
            'Authorization': "Bearer " + token + "",
            'Content-Type': 'application/json'
        }
        conn.request("POST", "/dev/v1/admin/keys", payload, headers)
        res = conn.getresponse()
        data = res.read()
        return ast.literal_eval(data.decode("utf-8"))
    except Exception:
        print("An exception occurred at get_encryption_key_from_cloud_API()")


class SerializationAPI(threading.Thread):
    def __init__(self, batch_dictionary, to_logging=False, get_new_token=True):
        """
        uploads 1 batch using serialization API and puts the result in batch_dictionary['response']
        :type batch_dictionary:
            {'response': string,
             'upload_data': [{"payload": packet (string, of full packets w/o 'post_process("' or '")' ),
                              "tagId": externalId (string)},....],
             'writing_lock': threading.Lock()}
        :param batch_dictionary: dictionary of a specific batch to upload
        :type to_logging: bool
        :param to_logging: if true, write to logging.debug the result of the upload
        """
        super(SerializationAPI, self).__init__()
        self.batch_dictionary = batch_dictionary
        self.kill_thread = threading.Event()  # will be set by the part that called this class
        self.to_logging = to_logging
        self.get_new_token = get_new_token
        self.exception_queue = Queue()
        with self.batch_dictionary['writing_lock']:
            self.batch_dictionary['response'] = 'waiting for cloud response'
        self.tags_in_batch = []
        for i in range(len(batch_dictionary['upload_data'])):
            self.tags_in_batch.append(batch_dictionary['upload_data'][i]['tagId'])

    def run(self):
        """
        will do the upload, will save the result to batch_dictionary['response'] when done
        """
        try:
            # take only the relevant part from the packets
            for i in range(len(self.batch_dictionary['upload_data'])):
                self.batch_dictionary['upload_data'][i]['payload'] = \
                    self.batch_dictionary['upload_data'][i]['payload'][16:-4]

            if self.to_logging:
                logging.debug('Serialization: sends the following upload_data: ' +
                              str(self.batch_dictionary['upload_data']))
            folder_path = 'configs'
            cfg_file_name = 'user_configs.json'
            # if file or folder doesn't exist will create json file with Authorization = 'None' and raise exception
            if self.get_new_token:
                if not get_new_token_api():
                    raise Exception('get_new_token_api() failed')

            if os.path.isdir(folder_path):
                file_path = os.path.join(folder_path, cfg_file_name)
                if os.path.exists(file_path):
                    cfg_data = open_json(folder_path=folder_path, file_path=os.path.join(folder_path, cfg_file_name))
                    bearer_token = cfg_data['Authorization']
                else:
                    print("Config file doesn't exist\n Creating user_config.json")
                    with open(file_path, 'w') as cfg:
                        json.dump({"Authorization": "None"}, cfg)
                    raise Exception('user_config.json was created\n')
            else:
                print("'wiliot_testers/offline/configs' directory doesn't exist\n"
                      " Creating directory and user_config.json")
                os.mkdir(folder_path)
                file_path = os.path.join(folder_path, cfg_file_name)
                with open(file_path, 'w') as cfg:
                    json.dump({"Authorization": "None"}, cfg)
                raise Exception('user_config.json was created to Upload files please insert your'
                                ' Bearer token in file:\n'
                                'wiliot_testers/offline/configs/user_configs.json under \n'
                                '"Authorization": "<enter your Bearer token here>"\n')

            print('Upload to cloud has began (for tags ' + str(self.tags_in_batch) +
                  ')\nWill update when a server response is received')

            conn = http.client.HTTPSConnection("api.wiliot.com")
            payload = json.dumps(self.batch_dictionary['upload_data'])
            headers = {
                'Authorization': 'Bearer ' + bearer_token,
                'Content-Type': 'application/json'
            }
            conn.request("POST",  "/test/v1/owner/wiliotmnf/serialize", payload, headers)
            res = conn.getresponse()
            data = res.read()

            message = ''
            if str(res.status) == '500':
                message = 'There was a problem at the Server side (status 500), ' \
                          'please try to upload again or reach Wiliot'

            elif str(res.status) == '401':
                message = 'There was a problem with the authorization (status 401),\n ' \
                          'Please make sure your user name and password in wiliot_testers/' \
                          'offline/configs/user_configs.json is correct or reach Wiliot'

            elif str(res.status)[0:2] == '40':
                message = 'There was a problem with the request (status 40*), ' \
                          'please try to upload again or reach Wiliot \n' \
                          'Status code is: ' + str(res.status)

            elif str(res.status) == '200':
                message = 'uploaded Successfully'
            message = "Answer from cloud for uploading tags " + str(self.tags_in_batch) + ' is:\n' + message +\
                      '\nmessage received = ' + str(data.decode("utf-8"))
            print(message)
            if self.to_logging:
                logging.debug('Serialization: ' + str(message))
            with self.batch_dictionary['writing_lock']:
                self.batch_dictionary['response'] = message
            if not str(res.status) == '200':
                print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n'
                      'Serialization failed!! you will need to end this run and restart it.\n'
                      'you will also need register the following data manually:\n'
                      + str(self.batch_dictionary['upload_data']) +
                      '\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                self.kill_thread.set()
                raise Exception('Serialization failed')
        except Exception:
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)

        finally:
            self.kill_thread.wait()

    def get_response(self):
        with self.batch_dictionary['writing_lock']:
            return self.batch_dictionary['response']


def check_serialization_exception_queues(serialization_threads_working):
    """
    checks if there is any response for any serialization thread, if it is good (success) will terminate the thread,
    else will raise exception
    :type serialization_threads_working: list of SerializationAPI
    :param serialization_threads_working: the Serialization process that needs to be monitored
    """
    for thread in serialization_threads_working:
        tags_in_batch = []
        for i in range(len(thread.batch_dictionary['upload_data'])):
            tags_in_batch.append(thread.batch_dictionary['upload_data'][i]['tagId'])
        if not thread.exception_queue.empty():
            thread.exception_queue.get()
            thread.kill_thread.set()
            thread.join(timeout=0.5)
            raise Exception('Serialization failed for tags ' + str(tags_in_batch))


def check_serialization_response(serialization_threads_working):
    """
    checks if there is any response for any serialization thread, if it is good (success) will terminate the thread,
    else will raise exception
    :type serialization_threads_working: list of SerializationAPI
    :param serialization_threads_working: the Serialization process that needs to be monitored
    """
    for thread in serialization_threads_working:
        with thread.batch_dictionary['writing_lock']:
            response = thread.batch_dictionary['response']

        if response == 'waiting for cloud response':
            pass
        elif 'uploaded Successfully' in response:
            thread.kill_thread.set()
            thread.join(timeout=0.5)
        else:
            raise Exception('Unknown message received from server while serialization process happened')


def close_all_serialization_processes_when_they_done(serialization_threads_working):
    """
    terminates all serialization threads when they are done
    :type serialization_threads_working: list of SerializationAPI
    :param serialization_threads_working: the Serialization process that needs to be monitored
    """
    if len(serialization_threads_working) > 0:
        print('please wait until all serialization processes end,\n'
              'will let you know when it is done (not more than a minute)')
    for thread in serialization_threads_working:
        thread.kill_thread.set()

    for thread in serialization_threads_working:
        thread.join(timeout=0.5)
    if len(serialization_threads_working) > 0:
        print('All serialization processes ended')

###########################################
#         Multiple Events Functions       #
###########################################


def or_set(self):
    """
    :param self: threading.Event()
    """
    self._set()
    self.changed()


def or_clear(self):
    """
    :param self: threading.Event()
    """
    self._clear()
    self.changed()


def orify(e, changed_callback):
    """
    combines the events
    :type e: threading.Event()
    :param e: the event to be combined into
    :type changed_callback: threading.Event()
    :param changed_callback: the event to be combined into
    """
    e._set = e.set
    e._clear = e.clear
    e.changed = changed_callback
    e.set = lambda: or_set(e)
    e.clear = lambda: or_clear(e)


def or_event_set(*events):
    """
    creates an event the combines multiple events
    :type threading.Event() list
    :return: the said event
    """
    or_event = threading.Event()

    def changed():
        """
        makes sure all of the events are clear when the orEvent is created
        """
        bools = [e.is_set() for e in events]
        if any(bools):
            or_event.set()
        else:
            or_event.clear()

    for e in events:
        orify(e, changed)
    changed()
    return or_event


###########################################
#               Post-Process              #
###########################################


def process_encrypted_tags_data(data, packet_threshold, tester_type=TesterName.OFFLINE, fail_this_tag=False):
    """
    @type data: list
    @param data: list of dict with tag_data
    @type packet_threshold: int
    @param packet_threshold: amount of packets for tag to pass
    @type tester_type: TesterName()
    @param tester_type: what tester uses this function
    @type fail_this_tag: bool
    @param fail_this_tag: indicates if 'status' field should be 'Failed' (in case of duplications)
    @rtype: dict
    @rvalue: dictionary with defined values
    """
    df = pd.DataFrame(data)
    adv_addr = df['advAddress'].iloc[0]
    tag_location = df['tagLocation'].iloc[0]
    common_run_name = df['commonRunName'].iloc[0]  # get first value (common value to all tags in run)
    received_packet_count = len(data)  # data is list of dicts where every dict is from one packet
    raw_data = df[['packet_time', 'raw_data']].to_json(orient="records")

    status = 'Failed'
    if received_packet_count >= packet_threshold and not fail_this_tag:
        status = 'Passed'

    if tester_type.value == 'offline':
        if 'temperatureFromSensor' in df.columns:  # exists only if temperature sensor is enabled
            temperature_from_sensor = df['temperatureFromSensor'].iloc[0]
            external_id = set_external_id(df['externalId'].iloc[0])
            return {'advAddress': adv_addr,
                    'tagLocation': tag_location,
                    'externalId': external_id,
                    'status': status,
                    'commonRunName': common_run_name,
                    'temperatureFromSensor': temperature_from_sensor,
                    'rawData': raw_data}
        else:
            external_id = set_external_id(df['externalId'].iloc[0])
            return {'advAddress': adv_addr,
                    'tagLocation': tag_location,
                    'externalId': external_id,
                    'status': status,
                    'commonRunName': common_run_name,
                    'rawData': raw_data}
    else:
        return {'advAddress': adv_addr,
                'tagLocation': tag_location,
                'status': status,
                'commonRunName': common_run_name,
                'rawData': raw_data}


def set_external_id(external_id=None):
    """
    returns external ID value to calling function (returns 'None' for unconverted tags)
    @type external_id: str (default is None)
    @param external_id: ID to print on tag
    @rtype: str
    @rvalue: 'None' (for unconverted) or external_id string
    """
    if external_id is not None:
        return external_id
    else:
        return 'None'


###########################################
#                   Log                   #
###########################################

def snake_to_camel(word):
    ret_val = ''.join(x.capitalize() or '_' for x in word.split('_'))
    ret_val = ret_val[:1].lower() + ret_val[1:] if ret_val else ''
    return ret_val


def collect_errors(log_path='', log_file_lines=''):
    """
    collect errors from logfile
    @type log_path: str
    @param log_path: log path file
    @type log_file_lines: str
    @param log_file_lines: if empty (''), read log file
    @rtype: list
    @rvalue: list of errors occurred in test
    """
    reel_data = {'tested': 0, 'passed': 0, 'includingUnderThresholdPassed': 0}
    errors = []
    if log_file_lines == '':
        log_file = open(file=log_path)
        log_file_lines = log_file.readlines()
    tag_data = {'tagLocation': None, 'externalId': None, 'status': None, 'packets': None}
    for line in log_file_lines:
        if 'User set up is:' in line:
            parts = [p for p in line.split("{")]
            # the dictionary from main window
            parts2 = [p for p in parts[1].split("}")]
            config_dict_from_user = ast.literal_eval('{' + parts2[0] + '}')
            # the dictionary from memory
            parts2 = [p for p in parts[2].split("}")]
            config_dict_from_memory = ast.literal_eval('{' + parts2[0] + '}')
            # the printing string dictionary
            try:
                parts3 = [p for p in parts[3].split("}")]
                printing_dict_from_memory = ast.literal_eval('{' + parts3[0] + '}')
            except Exception:
                printing_dict_from_memory = {}

            config_dict = {**config_dict_from_user, **config_dict_from_memory}
            config_dict = {**config_dict, **printing_dict_from_memory}
            for key, value in config_dict.items():
                reel_data[key] = value
            reel_data['tested'] = 0
        line = line.strip()
        if 'DEBUG' in line:
            if 'Duplication' in line:
                tmp = {'errorLocation': reel_data['tested'], 'errorString': None}
                parts = [p for p in line.split("DEBUG ")]
                tmp['errorString'] = parts[1]
                errors.append(tmp)

            if 'Packet rssi is too high' in line:
                tmp = {'errorLocation': reel_data['tested'], 'errorString': None}
                parts = [p for p in line.split("DEBUG ")]
                tmp['errorString'] = parts[1]
                errors.append(tmp)

            if 'Received packet that is too short' in line:
                tmp = {'errorLocation': reel_data['tested'], 'errorString': None}
                parts = [p for p in line.split("DEBUG ")]
                tmp['errorString'] = parts[1]
                errors.append(tmp)

            if 'Exception happened:, exc_type = ' in line:
                tmp = {'errorLocation': reel_data['tested'], 'errorString': None}
                parts = [p for p in line.split("DEBUG ")]
                tmp['errorString'] = parts[1]
                errors.append(tmp)

        if 'INFO' in line:
            parts = [p for p in line.split("INFO")]

            if 'Tag location is: ' in parts[1]:
                parts[1] = parts[1].strip('Tag location is: ')
                parts = [p for p in parts[1].split(',')]
                tag_data['tagLocation'] = int(parts[0])
                reel_data['tested'] = int(tag_data['tagLocation']) + 1  # locations starts from 0

        if 'WARNING ' in line:  # the space is here to ignore the 'Warnings' print from the printer
            tmp = {'errorLocation': reel_data['tested'], 'errorString': None}
            parts = [p for p in line.split("WARNING ")]
            tmp['errorString'] = parts[1]
            errors.append(tmp)

        if len(errors) != 0:
            return errors
    return None


class CsvLog:
    """
    Class for csv logs
    """

    def __init__(self, header_type, path, headers=None, tester_type=TesterName.NONE, temperature_sensor=False):
        """
        :type header_type: HeaderType
        :param header_type:
        :param path:
        :param headers:
        :param tester_type:
        :type temperature_sensor: bool
        :param temperature_sensor: if True -> temperature sensor enabled -> add header. else: sensor is disabled
        """
        self.tags_header = ['advAddress', 'tagLocation', 'status', 'commonRunName', 'rawData']

        self.run_header = ['testerStationName', 'commonRunName', 'batchName', 'testerType',
                           'comments', 'errors',
                           'timeProfile', 'txPower', 'energizingPattern', 'rssiThreshold', 'packetThreshold',
                           'tested', 'passed', 'includingUnderThresholdPassed', 'includingUnderThresholdYield', 'yield',
                           'yieldOverTime', 'yieldOverTimeInterval', 'yieldOverTimeOn',
                           'inlayType', 'inlay']

        if header_type.value == 'tag':
            self.header = self.tags_header
        elif header_type.value == 'run':
            self.header = self.run_header
        else:
            self.header = []
        self.path = path

        # add additional columns per tester:
        self.temperature_sensor_enable = temperature_sensor
        self.add_headers(headers, header_type, tester_type)

    def add_headers(self, headers=None, header_type=HeaderType.RUN, tester_type=TesterName.NONE):
        """
        added additional headers to output file according to file type and tester type
        :type headers:
        :param headers: additional headers for output file (determined by user)
        :type header_type: HeaderType
        :param header_type: determines if the file generated stores run data or tags data
        :type tester_type: TesterName
        :param tester_type: determines unique headers to add according to tester type

        """
        if headers is None:
            if header_type.value == 'run':
                if tester_type.value == 'offline':
                    added_headers = ['testTime', 'maxTtfp', 'converted', 'surface', 'tagGen',
                                     'toPrint', 'passJobName', 'printingFormat', 'stringBeforeCounter',
                                     'digitsInCounter', 'gwVersion', 'desiredPass', 'desiredTags',
                                     'firstPrintingValue', 'missingLabel', 'maxMissingLabels']
                elif tester_type.value == 'tal15k':
                    added_headers = ['testersGwVersion', 'chargerGwVersion', 'rowsNum', 'columnsNum',
                                     'numOfTesters', 'chargingTime', 'timePerTag']
                elif tester_type.value == 'conversion':
                    added_headers = []
                else:
                    added_headers = []
            elif header_type.value == 'tag':
                if tester_type.value == 'offline':
                    if self.temperature_sensor_enable:
                        added_headers = ['externalId', 'temperatureFromSensor']
                    else:
                        added_headers = ['externalId']
                else:
                    added_headers = []
            else:
                added_headers = []
        else:
            added_headers = headers
        self.header += added_headers

    def open_csv(self):
        """
        create csv file if not exist
        """
        dir_path = self.path[:(len(self.path) - (len(self.path.split('/')[-1])+1))]
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        if not os.path.isfile(self.path):
            with open(self.path, 'w', newline='') as write_obj:
                csv_writer = writer(write_obj)
                csv_writer.writerow(self.header)

    def append_list_as_row(self, data_to_append):
        """
        append data list to existing csv
        @type data_to_append: list
        @param data_to_append: values to append to csv
        """
        # Open file in append mode
        with open(self.path, 'a+', newline='') as write_obj:
            # Create a writer object from csv module
            csv_writer = writer(write_obj)
            # Add contents of list as last row in the csv file
            csv_writer.writerow(data_to_append)

    def append_table(self, data_table):
        """
        append data table to existing csv (using append_list_as_row)
        @type: data_table: list (list of lists)
        @param data_table: values to append to csv
        """
        col = 0  # the table has only 1 column
        for i in range(len(data_table)):
            self.append_list_as_row(self.dict_to_list(data_table[i][col]))

    def dict_to_list(self, data):
        """
        convert dict to list
        @type data: dict
        @param data:
        @rtype: list
        """
        res_list = []
        for title in self.header:
            if title in data.keys():
                res_list.append(data[title])
            else:
                res_list.append('')
        return res_list

    def override_run_data(self, run_data):
        """
        override run_data.csv at the end of run
        @type run_data: dict
        @param run_data: run configurations and results such as passed, tested, yield, etc.
        """
        with open(self.path, 'w', newline='') as write_obj:
            csv_writer = writer(write_obj)
            csv_writer.writerow(self.header)
            # self.append_list_as_row(self.path, self.dict_to_list(run_data))
            csv_writer.writerow(self.dict_to_list(run_data))


if __name__ == '__main__':
    pass

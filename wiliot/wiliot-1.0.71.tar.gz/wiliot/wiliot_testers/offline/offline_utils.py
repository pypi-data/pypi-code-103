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
import os
import PySimpleGUI as SimGUI
import json
import joblib
import http.client
import ast
import numpy as np
from scipy import stats
import serial
import serial.tools.list_ports
from time import sleep
from wiliot.wiliot_testers.tester_utils import *


class ConfigDefaults(object):
    """
    contains the default values for the configuration json
    """

    def __init__(self):
        self.printer_defaults = {'TCP_IP': '192.168.7.61', 'TCP_PORT': '3003', 'TCP_BUFFER': '128',
                                 'printingFormat': 'SGTIN'}
        self.single_band_gw_defaults = {'energizingPattern': '20', 'timeProfile': '2,6', 'txPower': '3',
                                        'rssiThreshold': '70', 'plDelay': '150'}
        self.dual_band_gw_defaults = {'energizingPattern': '18', 'secondEnergizingPattern': '52', 'timeProfile': '5,10',
                                      'txPower': '3', 'rssiThreshold': '90', 'plDelay': '100'}

    def get_printer_defaults(self):
        return self.printer_defaults

    def get_single_band_gw_defaults(self):
        return self.single_band_gw_defaults

    def get_dual_band_gw_defaults(self):
        return self.dual_band_gw_defaults


class DefaultGUIValues:
    def __init__(self, gui_type):
        if gui_type == 'Main':
            self.default_gui_values = {'missingLabel': 'No',
                                       'maxMissingLabels': '6',
                                       'toPrint': 'No', 'printingFormat': 'SGTIN', 'batchName': 'test_reel',
                                       'tagGen': 'D2',
                                       'inlayType': 'Dual Band', 'inlay': '088', 'testTime': '10', 'maxTtfp': '5',
                                       'packetThreshold': '10',
                                       'desiredTags': '9999999', 'desiredPass': '9999999', 'surface': 'air',
                                       'converted': 'Yes',
                                       'comments': ''}
        elif gui_type == 'String':
            self.default_gui_values = {'passJobName': '', 'stringBeforeCounter': '', 'digitsInCounter': '',
                                       'firstPrintingValue': ''}
        elif gui_type == 'SGTIN':
            self.default_gui_values = {'passJobName': 'SGTIN_QR', 'sgtin': '(01)00850027865010(21)',
                                       'stringBeforeCounter': '',
                                       'reelNumManually': '', 'firstPrintingValue': '0'}
        else:
            self.default_gui_values = {}


def open_session():
    """
    gets the user inputs from first GUI
    :return: dictionary of the values
    """
    # move to r2r : return dict - r2r
    folder_name = 'configs'
    file_name = 'gui_inputs_do_not_delete.json'
    gui_inputs_values = open_json(folder_path=folder_name, file_path=os.path.join(folder_name, file_name),
                                  default_values=DefaultGUIValues(gui_type='Main').default_gui_values)

    def_layout = [[SimGUI.Text('Allow multiple missing label in a row?', size=(40, 1)),
                   SimGUI.InputCombo(('Yes', 'No'), default_value=gui_inputs_values['missingLabel'],
                                     key='missingLabel')],
                  [SimGUI.Text('Max missing labels in a row:', size=(40, 1)),
                   SimGUI.InputText(gui_inputs_values['maxMissingLabels'], key='maxMissingLabels')],
                  [SimGUI.Text('To print?', size=(40, 1)),
                   SimGUI.InputCombo(('Yes', 'No'), default_value=gui_inputs_values['toPrint'], key='toPrint')],
                  [SimGUI.Text('What is the printing job format?', size=(40, 1)),
                   SimGUI.InputCombo(('String', 'SGTIN'), default_value=gui_inputs_values['printingFormat'],
                                     key='printingFormat')],
                  [SimGUI.Text('Reel_name:', size=(40, 1)), SimGUI.InputText(gui_inputs_values['batchName'],
                                                                             key='batchName')],
                  [SimGUI.Text('Tags Generation:', size=(40, 1)),
                   SimGUI.InputCombo(('C0', 'D1', 'D2'), default_value=gui_inputs_values['tagGen'], key='tagGen')],
                  [SimGUI.Text('Inlay type:', size=(40, 1)),
                   SimGUI.InputCombo(('Dual Band', 'Single Band'), default_value=gui_inputs_values['inlayType'],
                                     key='inlayType')],
                  [SimGUI.Text('Inlay serial number (3 digits):', size=(40, 1)),
                   SimGUI.InputText(gui_inputs_values['inlay'], key='inlay')],
                  [SimGUI.Text('Test Time [sec]\n(reel2reel controller->delay between steps = 999):', size=(40, 2)),
                   SimGUI.InputText(gui_inputs_values['testTime'], key='testTime')],
                  [SimGUI.Text('Fail if no packet received until [sec]:', size=(40, 1)),
                   SimGUI.InputText(gui_inputs_values['maxTtfp'], key='maxTtfp')],
                  [SimGUI.Text('PacketThreshold:', size=(40, 1)),
                   SimGUI.InputText(gui_inputs_values['packetThreshold'], key='packetThreshold')],
                  [SimGUI.Text('Desired amount of tags\n(will stop the run after this amount of tags):', size=(40, 2)),
                   SimGUI.InputText(gui_inputs_values['desiredTags'], key='desiredTags')],
                  [SimGUI.Text('Desired amount of pass\n(will stop the run after this amount of passes):',
                               size=(40, 2)),
                   SimGUI.InputText(gui_inputs_values['desiredPass'], key='desiredPass')],
                  [SimGUI.Text('Surface:', size=(40, 1)),
                   SimGUI.InputCombo(('cardboard', 'Er3', 'Er3.5', 'Er5', 'Er7', 'Er12'),
                                     default_value=gui_inputs_values['surface'], key='surface')],
                  [SimGUI.Text('Is converted?', size=(40, 1)),
                   SimGUI.InputCombo(('Yes', 'No'), default_value=gui_inputs_values['converted'], key='converted')],
                  [SimGUI.Text('Comments:', size=(40, 1)), SimGUI.InputText(gui_inputs_values['comments'],
                                                                            key='comments')],
                  [SimGUI.Submit()]]

    layout = def_layout
    # TODO - continue with the advanced option
    window = SimGUI.Window('Offline Tester', layout)

    event, values = window.read()
    window.close()
    # to defend against user errors
    values['tagGen'] = values['tagGen'].upper()
    with open(os.path.join(folder_name, file_name), 'w') as f:
        json.dump(values, f)
    return values


def get_printed_value(string_before_the_counter: str, digits_in_counter: int, first_counter: str, printing_format: str):
    """
    builds the printed value
    :type string_before_the_counter: string
    :param string_before_the_counter: the sg1 Id of the tested reel
    :type digits_in_counter: int
    :param digits_in_counter: amount of digits in the tag counter field (usually 4)
    :type first_counter: string
    :param first_counter: counter of the run first tag
    :type printing_format: string
    :param printing_format: this run printing format (SGTIN, string)
    """
    first_print = str(string_before_the_counter)
    if 'SGTIN' in printing_format:
        first_print += 'T'
    if digits_in_counter < len(first_counter):
        is_ok = False
    else:
        dif_len = (digits_in_counter - len(first_counter))
        for i in range(digits_in_counter):
            # add zeros to where the counter is not needed
            if i < dif_len:
                first_print += '0'
            else:
                # add the first counter number by order to the string
                first_print += str(first_counter)
                break
        is_ok = True
    return first_print, is_ok


def printing_string_window():
    """
    opens the GUI for user input for string print
    :return: dictionary of user inputs
    """
    printing_format = 'String'
    folder_name = 'configs'
    file_name = 'gui_printer_inputs_do_not_delete.json'
    gui_inputs_values = open_json(folder_path=folder_name, file_path=os.path.join(folder_name, file_name),
                                  default_values=DefaultGUIValues(printing_format).default_gui_values)

    # Define the window's contents
    layout = [[SimGUI.Text('Job to print for pass:'), SimGUI.Input(), SimGUI.FileBrowse(key="passJobName")],
              [SimGUI.Text("Job to print for pass:"),
               SimGUI.Input(gui_inputs_values['passJobName'], key='passJobName2')],
              [SimGUI.Text('*write the passJobName or choose from files & use Job name parser')],
              [SimGUI.Checkbox('Use Job name parser?', default=True, key='checkbox')],
              [SimGUI.Text("What's the string before the counter?")],
              [SimGUI.Input(gui_inputs_values['stringBeforeCounter'], key='stringBeforeTheCounter')],
              [SimGUI.Text("How many digits are in the counter?")],
              [SimGUI.Input(gui_inputs_values['digitsInCounter'], key='digitsInCounter')],
              [SimGUI.Text("What is the first counter number?")],
              [SimGUI.Input(gui_inputs_values['firstPrintingValue'], key='firstPrintingValue')],
              [SimGUI.Text(size=(60, 3), key='-OUTPUT-')],
              [SimGUI.Button('Check String'), SimGUI.Button('Submit')]]

    # Create the window
    window = SimGUI.Window('Printing String', layout)

    # Display and interact with the Window using an Event Loop
    while True:
        # init:
        string_before_counter = None
        digits_in_counter = None
        first_counter = None
        pass_job_name = None
        is_ok = False

        event, values = window.read()
        should_submit = True
        # See if user wants to quit or window was closed
        if event == SimGUI.WINDOW_CLOSED:
            is_ok = False
            break
        if event == 'Submit':
            if values['checkbox']:
                parts = [p for p in values['passJobName'].split("/")]
                pass_job_name = parts[-1].split('.')[0]
                parts = [p for p in parts[-1].split("_")]
                if len(parts) < 2:
                    window['-OUTPUT-'].update('Please enter a pass Job name according to the convention '
                                              'to use the parser (<string_before_counter>+_+<digits_in_counter>)')
                    should_submit = False
                else:
                    parts[1] = parts[1].split('.')[0]
                    string_before_counter = parts[0]
                    digits_in_counter = int(parts[1])
                    first_counter = values['firstPrintingValue']
            else:
                if values['passJobName2'] == '':
                    window['-OUTPUT-'].update(
                        'Please enter a pass Job name to continue')
                    should_submit = False
                elif values['digitsInCounter'] == '':
                    window['-OUTPUT-'].update(
                        'Please enter a digits In Counter to continue')
                    should_submit = False
                elif values['firstPrintingValue'] == '':
                    window['-OUTPUT-'].update(
                        'Please enter a first Counter to continue')
                    should_submit = False
                else:
                    try:
                        pass_job_name = values['passJobName2']
                        string_before_counter = values['stringBeforeTheCounter']
                        digits_in_counter = int(values['digitsInCounter'])
                        first_counter = values['firstPrintingValue']
                        first_print, is_ok = get_printed_value(string_before_counter, digits_in_counter, first_counter,
                                                               printing_format)
                        # Output a message to the window
                        if not is_ok:
                            window['-OUTPUT-'].update('Counter digits number is not big enough for that first '
                                                      'counter number!!\nPlease enter a new first counter number')
                            should_submit = False
                        else:
                            window['-OUTPUT-'].update('The first tag printing value will be:\n' + first_print)
                    except Exception:
                        window['-OUTPUT-'].update(
                            'Please enter valid values to continue (digits In Counter should be int)')
                        should_submit = False
            if string_before_counter is not None and digits_in_counter is not None and first_counter is not None:
                if should_submit:
                    first_print, is_ok = get_printed_value(string_before_counter, digits_in_counter, first_counter,
                                                           printing_format)
                break

        if event == 'Check String':
            if values['checkbox']:
                if values['passJobName'] == '':
                    window['-OUTPUT-'].update(
                        'Please enter a pass Job name to continue')
                parts = [p for p in values['passJobName'].split("/")]
                pass_job_name = parts[-1].split('.')[0]
                parts = [p for p in parts[-1].split("_")]
                if len(parts) < 2:
                    window['-OUTPUT-'].update('Please enter a pass Job name according to the convention '
                                              'to use the parser \n(<string_before_counter>+_+<digits_in_counter>)')
                else:
                    # removes the file type
                    parts[1] = parts[1].split('.')[0]
                    string_before_counter = parts[0]
                    digits_in_counter = int(parts[1])
                    first_counter = values['firstPrintingValue']
                    first_print, is_ok = get_printed_value(string_before_counter, digits_in_counter, first_counter,
                                                           printing_format)
                    # Output a message to the window
                    if not is_ok:
                        window['-OUTPUT-'].update('Counter digits number is not big enough for that first '
                                                  'counter number!!\nPlease enter a new first counter number')
                    else:
                        window['-OUTPUT-'].update('The first tag printing value will be:\n' + first_print)
            else:
                if values['passJobName2'] == '':
                    window['-OUTPUT-'].update(
                        'Please enter a pass Job name to continue')
                elif values['digitsInCounter'] == '':
                    window['-OUTPUT-'].update(
                        'Please enter a digits In Counter to continue')
                elif values['firstPrintingValue'] == '':
                    window['-OUTPUT-'].update(
                        'Please enter a first Counter to continue')
                else:
                    try:
                        pass_job_name = values['passJobName2']
                        string_before_counter = values['stringBeforeTheCounter']
                        digits_in_counter = int(values['digitsInCounter'])
                        first_counter = values['firstPrintingValue']
                        first_print, is_ok = get_printed_value(string_before_counter, digits_in_counter, first_counter,
                                                               printing_format)
                        # Output a message to the window
                        if not is_ok:
                            window['-OUTPUT-'].update('Counter digits number is not big enough for that first '
                                                      'counter number!!\nPlease enter a new first counter number')
                        else:
                            window['-OUTPUT-'].update('The first tag printing value will be:\n' + first_print)
                    except Exception:
                        window['-OUTPUT-'].update(
                            'Please enter valid values to continue (digits In Counter should be int)')

    # Finish up by removing from the screen
    window.close()
    v = {'passJobName': pass_job_name, 'stringBeforeCounter': string_before_counter,
         'digitsInCounter': digits_in_counter,
         'firstPrintingValue': values['firstPrintingValue']}
    f = open(os.path.join(folder_name, file_name), "w")
    json.dump(v, f)
    f.close()
    return v, is_ok


def printing_sgtin_window():
    """
    opens the GUI for user input for SGTIN print
    :return: dictionary of user inputs
    """
    printing_format = 'SGTIN'
    folder_name = 'configs'
    file_name = 'gui_printer_inputs_4_SGTIN_do_not_delete.json'
    gui_inputs_values = open_json(folder_path=folder_name, file_path=os.path.join(folder_name, file_name),
                                  default_values=DefaultGUIValues(printing_format).default_gui_values)

    # Define the window's contents
    layout = [[SimGUI.Text('Job to print for pass:'),
               SimGUI.InputCombo(('SGTIN_only', 'SGTIN_QR'), default_value="SGTIN_QR", key='passJobName')],
              [SimGUI.Text("What is the first counter number?")],
              [SimGUI.Input(gui_inputs_values['firstPrintingValue'], key='firstPrintingValue')],
              [SimGUI.Checkbox('Insert reel number manually?', default=False, key='isManually')],
              [SimGUI.Text("for manual mode only - what is the sgtin number?", key='sgtinNumManuallyText'),
               SimGUI.Input(gui_inputs_values['sgtin'], key='sgtinNumManually')],
              [SimGUI.Text("for manual mode only - what is the reel number?", key='reelNumManuallyText'),
               SimGUI.Input(gui_inputs_values['reelNumManually'], key='reelNumManually')],
              [SimGUI.Text(size=(60, 3), key='-OUTPUT-')],
              [SimGUI.Button('Check first print'), SimGUI.Button('Submit')]]

    # Create the window
    window = SimGUI.Window('Printing SGTIN', layout)

    # Display and interact with the Window using an Event Loop
    tag_digits_num = 4
    pass_job_name = None
    reel_number = ''
    did_withdraw = False
    reel_num = {}
    is_ok = True
    while True:
        event, values = window.read()
        should_submit = True
        # See if user wants to quit or window was closed
        if event == SimGUI.WINDOW_CLOSED:
            is_ok = False
            break
        if event == 'Submit':
            # check if the first counter number is int
            try:
                # to check if it is int as it should
                tmp = int(values['firstPrintingValue'])
                # the user want to insert one manually
                if not values['isManually']:
                    # there is no reel number already
                    if not did_withdraw:
                        window['-OUTPUT-'].update(
                            'Please wait until reel number will received from cloud\nIt might take few seconds')
                        reel_num = get_reel_name_from_cloud_api()
                        # reelNum = {'data': 'blablabla11111111111111111'}
                        if 'data' in reel_num.keys() and len(reel_num['data']) == 26:
                            did_withdraw = True
                            reel_number = reel_num['data']
                        else:
                            should_submit = False
                            window['-OUTPUT-'].update(
                                'Data withdraw from cloud failed\nPlease try again or contact Wiliot')
                            continue
                    pass_job_name = values['passJobName']
                    first_counter = values['firstPrintingValue']
                    # Output a message to the window
                    if len(str(values['firstPrintingValue'])) > tag_digits_num:
                        window['-OUTPUT-'].update(
                            'First counter number is too big for counter digits number!!\n'
                            'Please enter a new first counter number')
                        should_submit = False
                    else:
                        first_print, is_ok = get_printed_value(reel_num['data'], tag_digits_num, first_counter,
                                                               printing_format)
                        window['-OUTPUT-'].update('The first tag printing value will be:\n' + first_print)
                        print('The first tag printing value will be: ' + first_print)
                        should_submit = True
                # manual input
                elif values['isManually']:
                    if len(str(values['firstPrintingValue'])) > tag_digits_num:
                        window['-OUTPUT-'].update(
                            'First counter number is too big for counter digits number!!\n'
                            'Please enter a new first counter number')
                        should_submit = False
                    else:
                        pass_job_name = values['passJobName']
                        reel_number = values['sgtinNumManually'] + values['reelNumManually']
                        first_counter = values['firstPrintingValue']
                        first_print, is_ok = get_printed_value(reel_number, tag_digits_num,
                                                               first_counter, printing_format)
                        # Output a message to the window
                        window['-OUTPUT-'].update('The first tag printing value will be:\n' + first_print)
                        should_submit = True
            except Exception:
                window['-OUTPUT-'].update(
                    'First counter is not a number!!\nPlease enter a new first counter number')
                should_submit = False

            if should_submit:
                break

        if event == 'Check first print':
            # check if the first counter number is int
            try:
                tmp = int(values['firstPrintingValue'])
                # the user want to insert one manually
                if not values['isManually']:
                    # there is no reel number already
                    if not did_withdraw:
                        window['-OUTPUT-'].update(
                            'Please wait until reel number will received from cloud\nIt might take few seconds')
                        reel_num = get_reel_name_from_cloud_api()
                        # reelNum = {'data': 'blablabla11111111111111111'}
                        if 'data' in reel_num.keys() and len(reel_num['data']) == 26:
                            did_withdraw = True
                            reel_number = reel_num['data']
                        else:
                            window['-OUTPUT-'].update(
                                'Data withdraw from cloud failed\nPlease try again or contact Wiliot')
                            continue
                    pass_job_name = values['passJobName']
                    first_counter = values['firstPrintingValue']
                    first_print, is_ok = get_printed_value(reel_num['data'], tag_digits_num,
                                                           first_counter, printing_format)
                    # Output a message to the window
                    if len(str(values['firstPrintingValue'])) > tag_digits_num:
                        window['-OUTPUT-'].update('First counter number is too big for counter digits number!!\n'
                                                  'Please enter a new first counter number')
                    else:
                        window['-OUTPUT-'].update('The first tag printing value will be:\n' + first_print)
                # manual input
                elif values['isManually']:
                    if len(str(values['firstPrintingValue'])) > tag_digits_num:
                        window['-OUTPUT-'].update('First counter number is too big for counter digits number!!\n'
                                                  'Please enter a new first counter number')
                    else:
                        pass_job_name = values['passJobName']
                        reel_number = values['sgtinNumManually'] + values['reelNumManually']
                        first_counter = values['firstPrintingValue']
                        first_print, is_ok = get_printed_value(reel_number, tag_digits_num,
                                                               first_counter, printing_format)
                        # Output a message to the window
                        window['-OUTPUT-'].update('The first tag printing value will be:\n' + first_print)
            except Exception:
                window['-OUTPUT-'].update(
                    'First counter is not a number!!\nPlease enter a new first counter number')

    # Finish up by removing from the screen
    window.close()
    v = {'passJobName': pass_job_name, 'stringBeforeCounter': reel_number, 'digitsInCounter': tag_digits_num,
         'firstPrintingValue': values['firstPrintingValue']}
    data_to_save = {'passJobName': pass_job_name, 'sgtin': reel_number[:22], 'reelNumManually': reel_number[22:26],
                    'firstPrintingValue': values['firstPrintingValue']}

    f = open(os.path.join(folder_name, file_name), "w")
    json.dump(data_to_save, f)
    f.close()

    return v, is_ok


def save_screen():
    """
    open last GUI
    :return dictionary with the user inputs (should upload, last comments)
    """
    layout = [
        [SimGUI.Text('Would you like to upload this log to the cloud?'),
         SimGUI.InputCombo(('Yes', 'No'), default_value="Yes", key='upload')],
        [SimGUI.Text('Post run comments:')],
        [SimGUI.InputText('', key='comments')],
        [SimGUI.Submit()]]

    window = SimGUI.Window('Offline Tester', layout)
    event, values = window.read()
    window.close()
    return values


def get_reel_name_from_cloud_api():
    """
    api to receive reel number from cloud (should use it to avoid duplications)
    :return: the reel number (in 0x)
    """
    assert ('R2R_station_name' in os.environ), 'R2R_station_name is missing from PC environment variables'
    r2r_station_name = os.environ['R2R_station_name']
    try:
        username = os.environ['FUSION_AUTH_USER']
        print('success in getting the FUSION_AUTH_USER environment variables')
        password = os.environ['FUSION_AUTH_PASSWORD']
        print('success in getting the environment variables')
        conn = http.client.HTTPSConnection("api.wiliot.com")
        headers = {'accept': "application/json"}
        conn.request("POST", "/v1/auth/token?password=" + password + "&username=" + username, headers=headers)
        res = conn.getresponse()
        data = res.read()
        tokens = json.loads(data.decode("utf-8"))
        token = tokens['access_token']
        headers = {
            'accept': "*/*",
            'authorization': "Bearer " + token + "",
            'content-type': "application/json"
        }
        body = json.dumps({"printerId": r2r_station_name})
        payload = body
        conn.request("POST", "/v1/owner/wiliot/tag/roll/print", payload, headers)
        res = conn.getresponse()
        data = res.read()
        print("get_reel_name_from_cloud_API answer is:")
        print(data.decode("utf-8"))
        return ast.literal_eval(data.decode("utf-8"))

    except Exception:
        print("An exception occurred at get_reel_name_from_cloud_API()")


class PrinterNeedsResetException(Exception):
    pass


class R2rGpio(object):
    """
    class to open and use communication to Arduino on R2R machine
    """

    def __init__(self):
        """
        initialize params and port
        """
        self.baud_rate = 1000000
        ports_list = [s.device for s in serial.tools.list_ports.comports()]
        if len(ports_list) == 0:
            ports_list = [s.name for s in serial.tools.list_ports.comports()]
            if len(ports_list) == 0:
                print("no serial ports were found. please check your connections", "init")
                return

        for port in ports_list:
            try:
                self.comport = port
                self.s = serial.Serial(self.comport, self.baud_rate, timeout=0, write_timeout=0)
                response = self.query("*IDN?")
                if ("Williot R2R GPIO" in response):
                    print('Found ' + response + " Serial Number " + self.query("SER?"))
                    self.s.flushInput()
                    break
                else:
                    self.s.close()
            except (OSError, serial.SerialException):
                pass
            except Exception as e:
                print(e)

    def __del__(self):
        if self.s is not None:
            self.s.close()

    def write(self, cmd):
        """
        Send the input cmd string via COM Socket
        """
        if self.s.isOpen():
            pass
        else:
            self.s.open()

        try:
            self.s.flushInput()
            self.s.write(str.encode(cmd))
        except Exception:
            pass

    def query(self, cmd):
        """
        Send the input cmd string via COM Socket and return the reply string
        :return: massage from arduino (w/o the '\t\n')
        """
        if self.s.isOpen():
            pass
        else:
            self.s.open()
            sleep(1)
        self.s.flushInput()
        sleep(1)
        try:
            self.s.write(str.encode(cmd))
            sleep(2)
            data = self.s.readlines()
            value = data[0].decode("utf-8")
            # Cut the last character as the device returns a null terminated string
            value = value[:-2]
        except Exception:
            value = ''
        return value

    def read(self):
        """
        Send the input cmd string via COM Socket and return the reply string
        :return: massage from arduino (w/o the '\t\n')
        """
        if self.s.isOpen():
            pass
        else:
            self.s.open()
        try:
            while self.s.in_waiting == 0:
                pass

            data = self.s.readlines()
            self.s.flushInput()
            value = data[0].decode("utf-8")
            # Cut the last character as the device returns a null terminated string
            value = value[:-2]
        except Exception:
            value = ''
        return value

    def gpio_state(self, gpio, state):
        """
        gets the gpio state:
            my_gpio.gpio_state(3, "ON")
               start"on"/stop"off"
            my_gpio.gpio_state(4, "ON")
               enable missing label
        :param gpio: what gpio to write to
        :param state: to what state to transfer (ON / OFF)
        :return: reply from Arduino
        """
        cmd = 'GPIO' + str(gpio) + "_" + state
        replay = self.query(cmd)
        return replay

    def pulse(self, gpio, time):
        """
        send a pulse to the r2r machine:
            my_gpio.pulse(1, 1000)
               Pass
            my_gpio.pulse(2, 1000)
               fail
        :param gpio: what gpio to write to
        :param time: how long is the pulse
        :return: True if succeeded, False otherwise
        """
        cmd = 'GPIO' + str(gpio) + '_PULSE ' + str(time)
        self.write(cmd)
        sleep(time * 2 / 1000)
        replay = self.read()
        if replay == "Completed Successfully":
            return True
        else:
            return False

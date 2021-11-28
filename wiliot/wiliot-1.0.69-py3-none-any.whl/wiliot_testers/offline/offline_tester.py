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
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import socket
import pyqtgraph as pg
from queue import Queue
from wiliot.gateway_api.gateway import *
from wiliot.wiliot_testers.tester_utils import *
from wiliot.wiliot_testers.offline.offline_utils import *
import time
import os
import threading
import json
from datetime import timedelta

# a global variable which will be in the log_file name that says the R2R code version
R2R_code_version = '12'
# running parameters
tested = 0
passed = 0
under_threshold = 0
missing_labels = 0
last_pass_string = 'No tag has passed yet :('

desired_pass_num = 999999999  # this will be set to the desired pass that we want to stop after
desired_tags_num = 999999999  # this will be set to the desired tags that we want to stop after
reel_name = ''
common_run_name = ''
log_name = ''
log_path = ''
run_data_path = ''
tags_data_path = ''
tags_data_log = None
run_data_log = None
temperature_sensor_enable = False
run_data_list = []
run_data_dict = {}
run_start_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

test_reel = False
external_id_for_printer = 999999999
yield_over_time = 0
calculate_interval = 10
calculate_on = 50


class Printer(threading.Thread):
    """
    thread that turns printer on, checks that the print was successful after every tag,

    Parameters:
    @type start_value: int
    @param start_value: first external ID to print on first tag
    @type pass_job_name: str
    @param pass_job_name: the printer pass job name
    @type events: class MainEvents (costume made class that has all of the Events of the program threads)
    @param events: has all of the Events of the program threads
    @type ports_and_guis: class PortsAndGuis (costume made class that has all of the ports and gui inputs for the
                        program threads)
    @param ports_and_guis: has all of the ports and gui inputs for the program threads

    Exceptions:
    @except PrinterNeedsResetException: means that we need to close the program:
            'The printer initialization process has failed in command:...',
            'Printer failed to switch to running mode',
            'The printer over-all-state is Shutdown',
            'The printer over-all-state is Starting up',
            'The printer over-all-state is Shutting down',
            'The printer over-all-state is Offline',
            'reopen_sock() failed'
    @except Exception: operate according to the description:
            'The printer error-state is Warnings present',
            'The printer error-state is Faults present',
            'The printer printed Fail to the previous tag',
            'The printer have not printed on the last tag'

    Events:
        listen/ waits on:
            events.r2r_ready_or_done2tag    => user pressed Stop (end the program)
            events.done_to_printer_thread             => user pressed Stop (end the program) - to avoid deadlock
            events.cont_to_printer_thread             => continue was pressed by user
            events.r2r_ready                => printing was made
            events.was_pass_to_printer      => the last printing was pass
        sets:
            events.printer_error            => the last print was not successful, will cause pause to this run
                                                (and will trigger exception according to the situation)
            events.printer_success          => the last print was successful

    Logging:
        the logging from this thread will be also to logging.debug()
    """

    def __init__(self, start_value, pass_job_name, events, ports_and_guis):
        """
        Initialize Constants
        """
        super(Printer, self).__init__()
        try:
            self.ports_and_guis = ports_and_guis
            self.TCP_BUFFER = self.ports_and_guis.configs_for_printer_values['TCP_BUFFER']
            self.job_name = ''
            self.line_number = ''
            self.sgtin = 'sgtin'
            self.reel_num = 'reel_num'
            self.first_tag_counter = 'tag_number'
            self.pass_counter = 0
            self.fail_counter = 0
            self.timer_is_done = False
            self.exception_queue = Queue()
            self.printing_format = self.ports_and_guis.Tag_Value['printingFormat']
            self.roll_sgtin = self.ports_and_guis.Tag_Printing_Value['stringBeforeCounter']
            self.events = events
            self.r2r_ready_or_done2tag_or_done_to_printer_thread = or_event_set(events.r2r_ready_or_done2tag,
                                                                                events.done_to_printer_thread)
            self.start_value = start_value
            self.cur_value = 0
            self.pass_job_name = pass_job_name
            self.fail_job_name = 'line_'

            # open the socket & config the printer
            self.initialization()

        except Exception:
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)

    def initialization(self, use_current_value=False):
        """
        Initialize Constants and socket
        @param use_current_value: will indicate that this is not the first initialization at this run
                                    (make the next print to continue from the last printed value)
        """
        try:
            cmds = []
            self.ports_and_guis.open_printer_socket()  # will open and connect the socket
            self.set_printer_to_running()
            # after printer crash - make sure the continue will be from a the old counter
            if use_current_value:
                global external_id_for_printer
                config_start_value = external_id_for_printer
            else:
                config_start_value = self.start_value
            # initialization protocol
            if self.printing_format == 'String':
                cmds = ['CLN|1|\r\n', 'CLN|2|\r\n',
                        'LAS|' + str(self.pass_job_name) + '|2|' + 'Field00' + '=' + str(config_start_value) + '|\r\n',
                        'LAS|' + self.fail_job_name + '|1|\r\n']
            elif self.printing_format == 'SGTIN':
                # SGTIN_QR has field for reel_num + 'T' and field for sgtin,
                # SGTIN_only acts the same (the QR will not be in the sticker itself)
                if self.pass_job_name == 'SGTIN_QR' or self.pass_job_name == 'SGTIN_only':
                    cmds = ['CAF\r\n', 'CQI\r\n', 'CLN|1|\r\n', 'CLN|2|\r\n',
                            'LAS|' + str(self.pass_job_name) + '|2|' + str(self.sgtin) + '=' + str(
                                self.roll_sgtin[:18]) + '|'
                            + str(self.reel_num) + '=' + str(self.roll_sgtin[18:26]) + 'T' + '|'
                            + str(self.first_tag_counter) + '=' + str(config_start_value) + '|\r\n',
                            'LAS|' + self.fail_job_name + '|1|\r\n']

            else:
                print('The print Job Name inserted is not supported at the moment, You will need to press Stop')

            for cmd in cmds:
                value = self.query(cmd)
                time.sleep(0.3)
                # check if the return value is good, if not retry again for 10 times
                counter = 0
                while counter < 10:
                    # 'CQI' fails if the queue is empty
                    if value == 'ERR' and 'CQI' not in cmd:
                        counter += 1
                        time.sleep(0.3)
                        value = self.query(cmd)
                    else:
                        break
                if counter >= 10:
                    self.events.printer_error.set()
                    raise PrinterNeedsResetException('The printer initialization process has failed in command: ' + cmd)
            # get the current counter value
            value = self.query(self.get_state_request())
            if value == 'ERR':
                self.events.printer_error.set()
                raise PrinterNeedsResetException(
                    'The printer initialization process has failed in command: ' + self.get_state_request())
            else:
                parts = [p for p in value.split("|")]
                self.cur_value = int(parts[5])

            if not self.events.printer_error.isSet():
                print('printer thread is ready after initialization')
                logging.debug('printer thread is ready after initialization')
                self.events.printer_success.set()
        except Exception:
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)

    def set_printer_to_running(self):
        """
        sets the printer to running mode
        Zipher Text Communications Protocol
        printer state machine:
           0 -> 1                      shutdown
           1 -> 4 (automatically)      starting-up
           2 -> 0 (automatically)      shutting-down
           3 -> 2, 4                   running
           4 -> 2, 3                   offline
        @except: PrinterNeedsResetException('Printer failed to switch to running mode')
        @return: None
        """
        res = self.query(self.get_state_request())
        parts = [p for p in res.split("|")]
        if parts[1] == '0':  # (Shut down)
            res = self.query(self.set_state_command('1'))
            if res == 'ACK':
                while True:
                    time.sleep(1)
                    res = self.query(self.set_state_command('3'))
                    if res == 'ACK':
                        return
        elif parts[1] == '3':  # (Running)
            return
        elif parts[1] == '4':  # (Offline)
            res = self.query(self.set_state_command('3'))
            if res == 'ACK':
                return

        self.events.printer_error.set()
        raise PrinterNeedsResetException('Printer failed to switch to running mode')

    def run(self):
        """
        runs the thread
        """
        global passed
        # this flag will tell the printer to restart its run() (for a case of connectionError)
        do_the_thread_again = True
        while do_the_thread_again:
            do_the_thread_again = False
            logging.debug('starts printer inner loop')
            while not self.events.done_to_printer_thread.isSet():
                try:
                    self.r2r_ready_or_done2tag_or_done_to_printer_thread.wait()
                    if self.events.done_to_printer_thread.isSet():
                        break
                    # to avoid wrong counter in edge cases of printer crash
                    if self.events.cont_to_printer_thread.isSet():
                        self.events.cont_to_printer_thread.clear()
                        # get the current counter value
                        value = self.query(self.get_state_request())
                        if value == 'ERR':
                            self.events.printer_error.set()
                            raise PrinterNeedsResetException(
                                'The printer initialization process has failed in command: ' + self.get_state_request())
                        else:
                            parts = [p for p in value.split("|")]
                            self.cur_value = int(parts[5])

                    # timer goal - to give the printer enough time to process the command (precaution measure)
                    # if you wish to make the timer longer, please make the tagThread->r2rTimer longer accordingly
                    self.timer = threading.Timer(1, self.end_of_time)
                    self.timer.start()
                    # this loop should never happen
                    # checking both for the case that r2r_ready happens in the middle of the timer
                    while not self.timer_is_done and not self.events.r2r_ready.isSet():
                        time.sleep(0.3)
                        if self.events.r2r_ready.isSet():
                            self.timer.cancel()
                            self.timer_is_done = False
                            self.timer = threading.Timer(1, self.end_of_time)
                            self.timer.start()
                            self.events.r2r_ready.clear()
                            self.cur_value += 1

                    if self.events.r2r_ready.isSet():
                        self.timer.cancel()
                        self.timer_is_done = False
                        self.events.r2r_ready.clear()
                        self.cur_value += 1
                        self.timer = threading.Timer(1, self.end_of_time)
                        self.timer.start()
                        while not self.timer_is_done:
                            time.sleep(0.1)  # wait until the command has been processed by printer

                    res = self.query(self.get_state_request())
                    parts = [p for p in res.split("|")]
                    if parts[1] != '3':
                        if parts[1] == '0':
                            self.events.printer_error.set()
                            raise PrinterNeedsResetException('The printer over-all-state is Shutdown')
                        if parts[1] == '1':
                            self.events.printer_error.set()
                            raise PrinterNeedsResetException('The printer over-all-state is Starting up')
                        if parts[1] == '2':
                            self.events.printer_error.set()
                            raise PrinterNeedsResetException('The printer over-all-state is Shutting down')
                        if parts[1] == '4':
                            self.events.printer_error.set()
                            raise PrinterNeedsResetException('The printer over-all-state is Offline')
                    if parts[2] != '0':
                        if parts[2] == '1':
                            self.events.printer_error.set()
                            raise Exception('The printer error-state is Warnings present')
                        if parts[2] == '2':
                            self.events.printer_error.set()
                            raise Exception('The printer error-state is Faults present')
                        self.events.printer_error.set()
                    # the prev tag passed
                    print('self.cur_value is: ' + str(self.cur_value))  # to make sure the cur_value counter is correct
                    if self.events.was_pass_to_printer.isSet():
                        self.events.was_pass_to_printer.clear()
                        # the counter is correct
                        if int(parts[5]) == self.cur_value:
                            # pass was printed
                            if parts[3] == self.pass_job_name:
                                self.events.printer_success.set()
                            else:
                                self.events.printer_error.set()
                                raise Exception('The printer printed Fail to the previous tag')
                        else:
                            self.events.printer_error.set()
                            raise Exception('The printer have not printed on the last tag')

                        self.ports_and_guis.update_printer_gui_inputs()  # will add one to last printing value

                    # the tag failed
                    else:
                        # the counter is correct
                        if int(parts[5]) == self.cur_value:
                            self.events.was_fail_to_printer.clear()
                            # fail was printed
                            if parts[3] == self.fail_job_name:
                                self.events.printer_success.set()
                            else:
                                self.events.printer_error.set()
                                raise Exception('The printer printed Pass to the previous tag')
                        else:
                            self.events.printer_error.set()
                            raise Exception('The printer have not printed on the last tag')
                except Exception:
                    exception_details = sys.exc_info()
                    self.exception_queue.put(exception_details)
                    exc_type, exc_obj, exc_trace = exception_details
                    self.events.printer_error.set()  # to avoid deadlocks
                    # ConnectionResetError => exc_obj = 'An existing connection was forcibly closed by the remote host'
                    if isinstance(exc_obj, PrinterNeedsResetException):
                        self.r2r_ready_or_done2tag_or_done_to_printer_thread.wait()
                        break
                    elif isinstance(exc_obj, ConnectionResetError):
                        self.r2r_ready_or_done2tag_or_done_to_printer_thread.wait()
                        try:
                            self.reopen_sock()
                            do_the_thread_again = True
                            self.events.done_to_printer_thread.clear()
                            continue
                        except Exception:
                            print('self.reopen_sock() in printer thread failed, will end this run')
                            logging.debug('self.reopen_sock() in printer thread failed, will end this run')
                            exception_details = sys.exc_info()
                            self.exception_queue.put(exception_details)
                            exc_type, exc_obj, exc_trace = exception_details
                            self.events.printer_error.set()  # to avoid deadlocks
                            if isinstance(exc_obj, PrinterNeedsResetException):
                                self.r2r_ready_or_done2tag_or_done_to_printer_thread.wait()
                                break
                    else:
                        self.r2r_ready_or_done2tag_or_done_to_printer_thread.wait()

        self.closure()
        print("Exited the while loop of printer thread")
        logging.debug("Exited the while loop of printer thread")
        return

    def end_of_time(self):
        """
        is triggered at the end of timer
        """
        self.timer_is_done = True

    def query(self, cmd):
        """Send the input cmd string via TCPIP Socket

        @return: the reply string
        """

        self.ports_and_guis.Printer_socket.send(cmd.encode())
        data = self.ports_and_guis.Printer_socket.recv(int(self.TCP_BUFFER))
        value = data.decode("utf-8")
        # Cut the last character as the device returns a null terminated string
        value = value[:-1]
        print(datetime.datetime.now().time(), "Sent command to printer: ", cmd.strip('\r\n'))
        print(datetime.datetime.now().time(), "Received answer from printer: ", value.strip('\r\n'))
        logging.debug("Sent command to printer: " + cmd.strip('\r\n'))
        logging.debug("Received answer from printer: " + value.strip('\r\n'))

        return value

    def closure(self):
        """
        set printer to shutting down and close the socket
        """
        try:
            self.query(self.set_state_command('2'))  # for regular closure (not when connection error happens)
            self.ports_and_guis.Printer_socket.close()
        except Exception:
            try:
                self.ports_and_guis.Printer_socket.close()
            except Exception:
                print('s.close() failed')
                logging.debug('s.close() failed')
                pass

    def reopen_sock(self):
        """
        close and reopens the printer sock
        """
        try:
            self.closure()
            time.sleep(1)  # to make sure the socket is closed when we start the reopen
            self.initialization()
        except Exception:
            print('reopen_sock() failed, please end this run')
            logging.debug('reopen_sock() failed')
            raise (PrinterNeedsResetException('reopen_sock() failed'))

    def line_assigment(self, job_name, line_number, field_name, field_value):
        """
        builds the command to send to printer for configuration of the printing format
        @param job_name: (string) what is the job name (should be the same as in the printer)
        @param line_number: what is the line to assign to (2 = pass, 1 = fail)
        @param field_name: field name in the printer
        @param field_value: what to put in this field
        @return: the cmd to send to printer
        """
        # Send Line Assignment Command: job name + line number+starting value
        cmd = 'LAS|' + str(job_name) + '|' + str(line_number) + '|' + str(field_name) + '=' + str(
            field_value) + '|\r\n'
        # changing to bytes
        return cmd

    def clear_line(self, line_number):
        """
        builds the command to send to printer for clearing a line
        @param line_number: the line to clear
        @return: the cmd to send to printer
        """
        # On success, returns the default success response (ACK). On failure, returns the default failure response (ERR)
        cmd = 'CLN|' + str(line_number) + '|\r\n'
        return cmd

    def set_state_command(self, desired_state):
        """
        builds the command to send to printer for setting a printer state
        @param desired_state: the state to enter to, according to the following description
        0 Shut down
        1 Starting up
        2 Shutting down
        3 Running
        4 Offline
        @return: the cmd to send to printer
        """
        cmd = 'SST|' + str(desired_state) + '|\r\n'
        return cmd

    def get_job_name(self):
        """
        gets the last job that were used by the printer
        @return: the name of the current job in the printer in the following format:
            JOB|<job name>|<line number>|<CR>
        """
        cmd = 'GJN\r\n'
        return cmd

    def get_state_request(self):
        """
        gets the situation of the printer
        @return: the situation in the printer in the following format:
            STS|<overallstate>|<errorstate>|<currentjob>|<batchcount>|<totalcount>|<
        """
        cmd = 'GST\r\n'
        return cmd


class TagThread(threading.Thread):
    """
    Thread that controls the gateway, tests each tag and saves data to csv output file
    Parameters:
        @type events: class MainEvents (costume made class that has all of the Events of the program threads)
        @param events: has all of the Events of the program threads
        @type ports_and_guis: class PortsAndGuis (costume made class that has all of the ports and gui inputs for the
                            program threads)
        @param ports_and_guis: has all of the ports and gui inputs for the program threads

    Exceptions:
        @except 'Exception happened in Tag thread initialization. need to kill this run'
                means that connecting to GW or temperature sensor failed, the run will pause and wait for
                stop button from user

        @except Exception: 'tag_checker_thread got an Exception, press Continue or Stop'
                            exception details will be printed

        @except (OSError, serial.SerialException):
                Problems with GW connection, requires user to press "Stop" and end the run

        @except Exception: exception occurred while testing a tag (inside new_tag function)

        @raise Exception('R2R moved before timer ended') :
               Either R2R moved before or received packet is not valid tag packet
               The run will pause

        @except Exception: 'Warning: packet_decoder could not decode packet, will skip it'
                           In case encrypted_packet_decoder() failed in decoding packet, packet is skipped and
                           threads waits for next packet.
                           Run won't pause in that case. If tag reaches timeout, it will marked as fail

    Events:
        listen/ waits on:
            events.r2r_ready_or_done2tag => user pressed Stop (end the program) or r2r has finished to write the command
            events.done_or_printer_event => waits for printer event or for done_to_tag_thread (closes TagThread)
            events.done_to_tag_thread => closes TagThread at the end of the run
            events.cont_to_tag_thread => wait for continue from MainWindow thread
            events.pause_to_tag_thread => pauses thread if exception happened of user pressed Pause
            events.printer_error => the last print was not successful, will cause pause to this run
                                                (and will trigger exception according to the situation)

        sets:
            events.cont_to_main_thread => send continue from TagThread to MainWindow thread
            events.tag_thread_is_ready_to_main => notifies MainWindow thread TagThread is ready
            events.pause_to_tag_thread => pauses thread if exception happened of user pressed Pause
            events.was_pass_to_printer => tag has passed. report "Pass" to printer
            events.was_fail_to_printer => tag has failed. report "Fail" to printer
            events.disable_missing_label_to_r2r_thread => if set, the run will pause if missing label is detected
            events.enable_missing_label_to_r2r_thread => if set, the run will not pause if missing label is detected
                                                        (up to maxMissingLabels set by user)
            events.start_to_r2r_thread => enable/disable R2R movement. Sends pulse on "Start/Stop machine" GPIO line
            events.stop_to_r2r_thread => stops the R2R from running in case of end of run or exception
            events.pass_to_r2r_thread => notify if current tag passed. if set, send pulse on "Pass" GPIO line,
                                         The R2R will advance to next tag
            events.fail_to_r2r_thread => notify if current tag failed. if set, send pulse on "Fail" GPIO line,
                                         The R2R will advance to next tag

    Logging:
        logging to logging.debug(), logging.info() and logging.warning()
    """
    def __init__(self, events, ports_and_guis):
        """
        Initialize Constants
        """
        super(TagThread, self).__init__()
        self.ports_and_guis = ports_and_guis
        self.events = events
        self.test_times_up = False
        self.r2r_response_times_up = False
        self.ttfp_times_up = False
        self.tag_list = []
        self.tag_list_len = 5000  # TODO - decide how many tags to use here
        self.cur_tag_name = ''
        self.cur_tag_adv_addr = ''
        self.adv_addr = ''
        self.cur_tag_min_rssi = 1000  # big value, any real value will be much smaller
        # variables for using serialization API
        self.num_of_tags_per_upload_batch = 10
        self.serialization_data_for_all_run = []  # list of data_to_upload lists
        # the tags that have not been started the upload yet
        self.next_batch_to_serialization = {'response': '', 'upload_data': []}
        self.serialization_threads_working = []  # the actual threads that do the serialization
        self.get_new_token = True  # flag to indicate if a new token is needed
        self.time_delta_for_new_token = timedelta(hours=1)  # will generate new token after this time
        self.last_time_token_was_generated = None

        self.pass_job_name = ''  # will be set inside config
        self.to_print = False
        self.printing_value = {'passJobName': None, 'stringBeforeCounter': None, 'digitsInCounter': 10,
                               'firstPrintingValue': '0'}  # will be set in config()
        self.done_or_printer_event = or_event_set(self.events.done_to_tag_thread, events.printer_event)
        self.fetal_error = False
        self.exception_queue = Queue()

        try:
            self.GwObj, self.t = self.config()
        except Exception:
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)
            print('Exception happened in Tag thread initialization. need to kill this run')
            # to pause the run if exception happens
            self.events.cont_to_tag_thread.wait()
            self.events.cont_to_tag_thread.clear()
            self.events.pause_to_tag_thread.clear()
            self.events.cont_to_main_thread.set()

        self.time_out_to_missing_label = float(self.value['testTime']) + 10
        self.r2r_timer = ''
        self.timer = ''
        self.timer_for_ttfp = ''
        self.printed_external_id = ''

        self.need_to_pause = False
        self.tag_location = 0
        self.group_id_hist = {}  # histogram of the group_id in this run
        self.events.tag_thread_is_ready_to_main.set()

    @pyqtSlot()
    def run(self):
        """
        runs the thread
        """
        if self.value['missingLabel'] == 'No':
            self.events.disable_missing_label_to_r2r_thread.set()
            self.is_missing_label_mode = False
        elif self.value['missingLabel'] == 'Yes':
            self.events.enable_missing_label_to_r2r_thread.set()
            self.is_missing_label_mode = True

        self.events.tag_thread_is_ready_to_main.set()
        die = False
        self.missing_labels_in_a_row = 0

        while not die:
            try:
                check_serialization_exception_queues(self.serialization_threads_working)
                self.events.r2r_ready_or_done2tag.wait()
                if self.events.done_to_tag_thread.is_set():
                    die = True
                else:  # the r2r_ready event happened , done_or_printer_event.wait will happen after start GW
                    # start of tags loop ###########################
                    # the long timer (will cause +1 missing label)
                    self.r2r_response_times_up = False
                    # will wait 10 seconds after the tag timer should have ended
                    # and then will enforce a start_r2r & fail_r2r
                    self.r2r_timer = threading.Timer(self.time_out_to_missing_label, self.end_of_time,
                                                     ['r2r is stuck'])
                    self.r2r_timer.start()
                    # check if the serialization process so far are OK
                    check_serialization_exception_queues(self.serialization_threads_working)
                    check_serialization_response(self.serialization_threads_working)
                    # new_tag will set the events (pass_to_r2r_thread, fail_to_r2r_thread)
                    result = self.new_tag(self.t)
                    if result == 'Exit':
                        die = True

                    # will upload a batch at the end of the run or after self.num_of_tags_per_upload_batch
                    if (len(self.next_batch_to_serialization['upload_data']) ==
                            self.num_of_tags_per_upload_batch or
                        (die and len(self.next_batch_to_serialization['upload_data']) > 0))\
                            and not self.to_print:  # TODO - remove the not

                        self.serialization_data_for_all_run.append(self.next_batch_to_serialization)
                        self.next_batch_to_serialization = {'response': '', 'upload_data': []}
                        check_serialization_exception_queues(self.serialization_threads_working)
                        # check when was the last time we generate a new token
                        get_new_token = False
                        if self.last_time_token_was_generated is not None and \
                                self.last_time_token_was_generated - datetime.datetime.now() > \
                                self.time_delta_for_new_token:
                            get_new_token = True
                        else:
                            self.last_time_token_was_generated = datetime.datetime.now()
                            get_new_token = True
                        self.serialization_threads_working.append(
                            SerializationAPI(batch_dictionary=self.serialization_data_for_all_run[-1], to_logging=True,
                                             get_new_token=get_new_token))
                        self.serialization_threads_working[-1].start()

                    self.tag_location += 1
                    # end of tags loop ###############################
            except (OSError, serial.SerialException):
                if self.events.done_to_tag_thread.is_set():
                    die = True
                exception_details = sys.exc_info()
                self.exception_queue.put(exception_details)
                print("Problems with gateway serial connection - click on stop and exit the app")
                self.fetal_error = True
            except Exception:
                if self.events.done_to_tag_thread.is_set():
                    die = True
                exception_details = sys.exc_info()
                self.exception_queue.put(exception_details)
                # wait until user press Continue
                if not self.r2r_timer == '':
                    self.r2r_timer.cancel()

                if not die:
                    self.events.cont_to_tag_thread.wait()
                self.events.cont_to_tag_thread.clear()
                self.events.pause_to_tag_thread.clear()
                self.events.cont_to_main_thread.set()
        self.closure_fn()

    def end_of_time(self, kind):
        """
        sets the correct flag to True when a timer is done
        @param kind: the kind of the timer
        """
        if kind == 'tag':
            self.test_times_up = True
            print("Tag reached Time-Out")
        if kind == 'r2r is stuck':
            self.r2r_response_times_up = True
            print("R2R is stuck, Tag reached Time-Out")
            logging.debug("R2R is stuck, Tag reached Time-Out")
        if kind == 'no packet arrived':  # ttfp timer
            self.ttfp_times_up = True
            print("First packet did not arrive for more than " + self.value['maxTtfp'] + " seconds")

    def config(self):
        """
        configuration of GW, logging and run_data
        @return:  Gw's Com port Obj, temperature sensor
        """
        self.value = self.ports_and_guis.Tag_Value
        if self.value['batchName'] == 'test_reel':
            global test_reel
            test_reel = True
        if self.value['comments'] == '':
            self.value['comments'] = None

        self.internal_value = self.ports_and_guis.configs_for_gw_values
        # for the case we do not print
        self.externalId = 0
        self.pass_job_name = ''

        if self.value['toPrint'] == 'Yes':
            self.to_print = True
            self.printing_value, is_OK = self.ports_and_guis.Tag_Printing_Value, self.ports_and_guis.Tag_is_OK
            self.externalId = int(self.printing_value['firstPrintingValue'])
            self.pass_job_name = self.printing_value['passJobName']

        log_path = self.ports_and_guis.Tag_pathForLog
        # save the reel & log name for upload to the cloud at the end

        parts = [p for p in log_path.split("/")]
        global log_name
        log_name = parts[2]
        logging.basicConfig(filename=log_path, filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S', level=logging.DEBUG)
        # setting up the global variables ###################################################
        global desired_pass_num
        global desired_tags_num
        desired_tags_num = int(self.value['desiredTags'])
        desired_pass_num = int(self.value['desiredPass'])

        # config GW, temp sens and classifier ###############################################
        self.GwObj = self.ports_and_guis.GwObj
        # +30 to let us see the high rssi packets in the PC (will be captured in the encrypted_packet_filter())
        self.GwObj.write('!set_energizing_pattern 52')
        time.sleep(0.2)
        self.GwObj.write('!set_energizing_pattern 51')
        time.sleep(0.2)
        config_gw(self.GwObj, rssi_threshold=(int(self.internal_value['rssiThreshold']) + 30),
                  energizing_pattern=self.internal_value['energizingPattern'],
                  tx_power=self.internal_value['txPower'], time_profile='0,6',
                  set_interrupt=True, pl_delay=self.internal_value['plDelay'])
        # self.GwObj.check_current_config()  # for debugging
        global temperature_sensor_enable
        if temperature_sensor_enable:
            t = self.ports_and_guis.Tag_t
        else:
            t = None
        self.internal_value['testerStationName'] = self.ports_and_guis.tag_tester_station_name

        global run_data_list
        run_data_list.append(self.value)
        run_data_list.append(self.internal_value)
        run_data_list.append(self.printing_value)
        global run_start_time
        logging.info('Start time is: ' + run_start_time + ', User set up is: %s, %s, %s',
                     self.value, self.internal_value, self.printing_value)
        global run_data_dict
        global run_data_log

        if run_data_log is None:
            run_data_log = CsvLog(header_type=HeaderType.RUN, path=run_data_path, tester_type=TesterName.OFFLINE)
            run_data_log.open_csv()
            print("run_data log file has been created")
        for dic in run_data_list:
            for key in dic.keys():
                if key in run_data_log.header:
                    run_data_dict[key] = dic[key]

        run_data_dict['commonRunName'] = common_run_name
        run_data_dict['testerType'] = 'offline'
        sw_version, _ = self.GwObj.get_gw_version()
        run_data_dict['gwVersion'] = sw_version
        global yield_over_time
        global calculate_interval
        global calculate_on
        global passed
        global tested
        run_data_dict['yieldOverTime'] = yield_over_time
        run_data_dict['yieldOverTimeInterval'] = calculate_interval
        run_data_dict['yieldOverTimeOn'] = calculate_on
        run_data_dict['passed'] = passed
        run_data_dict['tested'] = tested
        if tested > 0:  # avoid division by zero
            run_data_dict['yield'] = passed / tested
        if tested == 0:
            run_data_dict['yield'] = -1.0
            run_data_dict['includingUnderThresholdPassed'] = -1
            run_data_dict['includingUnderThresholdYield'] = -1.0
        run_data_log.append_list_as_row(run_data_log.dict_to_list(run_data_dict))
        return self.GwObj, t

    def encrypted_packet_filter(self, raw_data, group_id=None):
        """
        checks if the packet is good in terms of RSSI, tag UID
        @param raw_data: raw data of the tags (return value from packet_listener)
        @type group_id: string
        @param group_id: the packet group_id
        @return: is_good_packet - is the packet legal,
                    need_to_switch - the tag that is currently in test is not the correct tag
                     and you should switch to the tag that sent this packet,
                     need_to_pause - you should pause the run due to Duplication
        """
        try:
            # check if the tag group_id is the same as the rest of the tags
            bad_group_id = False
            if group_id is not None:
                if group_id not in self.group_id_hist.keys():
                    if len(self.group_id_hist) > 0:
                        max_group_id = max(self.group_id_hist.values())
                        for i, (group, group_val) in enumerate(self.group_id_hist.items()):
                            if group_val == max_group_id and not group_id == group:
                                bad_group_id = True
                    self.group_id_hist[group_id] = 1
                else:
                    if len(self.group_id_hist) > 0:
                        max_group_id = max(self.group_id_hist.values())
                        for i, (group, group_val) in enumerate(self.group_id_hist.items()):
                            if group_val == max_group_id and not group_id == group:
                                bad_group_id = True
                    self.group_id_hist[group_id] += 1
                if bad_group_id:
                    msg = str(raw_data['raw_data']) + " - packet with wrong group_id found (group_id = " + \
                          str(group_id) + ', group_id seen so far (from all packets) = ' + str(self.group_id_hist) + ')'
                    logging.debug(msg)
                    print(msg)
                    return False, False, True

            # check if the RSSI is good
            if str(raw_data['rssi']) > self.internal_value['rssiThreshold']:
                msg = str(raw_data['raw_data']) + " - Packet rssi is too high and wasn't accounted for"
                logging.debug(msg)
                print(msg)
                return False, False, False

            # check if the tag was already caught in the GW
            if str(raw_data['advAddress']) in self.tag_list:
                msg = str(raw_data['raw_data']) + " - Duplication from a tag we have seen before (advAddress = " \
                      + raw_data['advAddress'] + ")"
                logging.debug(msg)
                print(msg)
                return False, False, True

            # check if this packet is from new tag
            if self.cur_tag_adv_addr != raw_data['advAddress'] and self.cur_tag_min_rssi != 1000:
                if raw_data['rssi'] >= self.cur_tag_min_rssi:
                    msg = str(raw_data['raw_data']) + " - Duplication from new tag (advAddress = " + \
                          str(raw_data['advAddress']) \
                          + ") we have not seen before (new tag rssi = " + str(raw_data['rssi']) \
                          + ', current tag rssi = ' + str(self.cur_tag_min_rssi) + ')'
                    logging.debug(msg)
                    print(msg)
                    return False, False, True
                else:
                    msg = str(raw_data['raw_data']) + " - Duplication with smaller RSSI, need to change tag " \
                        "(to advAddress = " + str(raw_data['advAddress']) + ") (new tag rssi = " \
                        + str(raw_data['rssi']) + ', current tag rssi = ' + str(self.cur_tag_min_rssi) + ')'
                    logging.debug(msg)
                    print(msg)
                    return False, True, True

            return True, False, False
        except Exception as e:
            print('Exception during packet filter: {}'.format(e))
            logging.debug('Exception during packet filter: {}'.format(e))
            return False, False, False

    def new_tag(self, t):
        """
        will run a loop to count the packets for 1 tag and decide pass/fail
        @param t: temperature sensor
        """
        global tags_data_log
        global tags_data_path
        global under_threshold
        global missing_labels
        global temperature_sensor_enable
        tag_data_list = []
        self.timer, self.timer_for_ttfp, raw_data = '', '', ''
        self.start_GW_happened = False  # will say if the r2r is in place, if not -> busy wait in the while loop
        self.test_times_up = False
        self.ttfp_times_up = False
        self.cur_tag_name = ''
        self.cur_tag_adv_addr = ''
        self.cur_tag_min_rssi = 1000  # big value, any real value will be much smaller
        temperature_from_sensor = 0
        if self.need_to_pause:
            if self.events.done_to_tag_thread.isSet():
                return
            else:
                self.events.cont_to_tag_thread.wait()
                self.events.cont_to_tag_thread.clear()
                self.events.pause_to_tag_thread.clear()
                self.events.cont_to_main_thread.set()

        self.need_to_pause = False
        need_to_switch = False
        self.did_change_pattern = False

        def clear_timers():
            if not self.timer == '':
                self.timer.cancel()
                self.test_times_up = False
            if not self.timer_for_ttfp == '':
                self.timer_for_ttfp.cancel()
                self.ttfp_times_up = False
            if not self.r2r_timer == '':
                self.r2r_timer.cancel()
                self.r2r_response_times_up = False

        logging.debug('************ new tag test ************')
        print('************ new tag test ************')
        self.GwObj.reset_buffer()
        config_gw(self.GwObj, time_profile=self.internal_value['timeProfile'])  # starting to transmit
        # self.GwObj.check_current_config()  # for debugging
        logging.debug('Changed the GW duty cycle to ' + str(self.internal_value['timeProfile']))
        print('Changed the GW duty cycle to ' + str(self.internal_value['timeProfile']))

        try:
            clear_timers()
        except Exception as e:
            pass
        while len(tag_data_list) < int(self.value['packetThreshold']) and not self.test_times_up and \
                not self.r2r_response_times_up and not self.ttfp_times_up and \
                not self.events.pause_to_tag_thread.is_set() and \
                not self.events.cont_to_tag_thread.is_set() and not self.events.done_to_tag_thread.is_set():
            time.sleep(0)  # to prevent run slowdown by gateway_api
            if temperature_sensor_enable:
                temperature_from_sensor = t.get_currentValue()

            if not self.start_GW_happened:
                # wait until the GPIO is triggered /max time is done. ignore all packets until done
                gw_answer = self.GwObj.read_specific_message(msg="Start Production Line GW",
                                                             read_timeout=self.time_out_to_missing_label)
                if gw_answer == '':
                    self.r2r_response_times_up = True  # will be treated as missing label
                    break
                # resets the counters
                self.GwObj.reset_buffer()
                self.GwObj.run_packets_listener(tag_packets_only=False, do_process=True)
                print(gw_answer)
                logging.info('%s' % gw_answer)
                global tested
                tested += 1
                self.printed_external_id, is_OK = get_printed_value(self.printing_value['stringBeforeCounter'],
                                                                    self.printing_value['digitsInCounter'],
                                                                    str(self.externalId),
                                                                    self.value['printingFormat'])
                if not is_OK:
                    msg = 'printing counter reached a value that is bigger than the counter possible space.' \
                          ' the program will exit now'
                    print(msg)
                    logging.warning(msg)
                    sys.exit(0)
                print("----------------- Tag location: {} -----------------".format(
                    self.tag_location) + "expected tag external ID is: " + self.printed_external_id)
                logging.info(
                    "Tag location is: {}".format(self.tag_location) + ", expected tag external ID is: {} ".format(
                        self.printed_external_id))
                tag_data_list = []

                logging.debug("New Tag timer started (" + self.value['testTime'] + " secs)")
                print("New Tag timer started (" + self.value['testTime'] + " secs)")
                # set timer for new tag
                self.timer = threading.Timer(float(self.value['testTime']), self.end_of_time, ['tag'])
                self.timer.start()
                self.timer_for_ttfp = threading.Timer(float(self.value['maxTtfp']), self.end_of_time,
                                                      ['no packet arrived'])
                self.timer_for_ttfp.start()
                self.start_GW_happened = True

            # if we received a packet we will process it and add it to the tag data list

            if self.GwObj.is_data_available():
                gw_answer = self.GwObj.get_data(action_type=ActionType.FIRST_SAMPLES, num_of_packets=1,
                                                data_type=DataType.PROCESSED)
                if gw_answer and \
                        not gw_answer['is_valid_tag_packet'] and "Start Production Line GW" in gw_answer['packet']:
                    if self.start_GW_happened:
                        print("gw answer is:", gw_answer)
                        logging.warning(gw_answer)
                        clear_timers()  # verify times are cleared before next tag
                        raise Exception('R2R moved before timer ended')
                elif gw_answer and gw_answer['is_valid_tag_packet']:
                    # for the tag to keep running until the end of main timer if there was any packet
                    self.timer_for_ttfp.cancel()
                    # in packet decoder we will decide the correct way to decode the packet
                    try:
                        raw_data = encrypted_packet_decoder(gw_answer)
                        self.adv_addr = raw_data['advAddress']
                        raw_data['tagLocation'] = self.tag_location
                        raw_data['commonRunName'] = common_run_name
                        raw_data['externalId'] = self.printed_external_id
                        logging.info('packet_decoder result is: ' + str(raw_data))
                    except Exception:
                        msg = 'Warning: packet_decoder could not decode packet, will skip it'
                        print(msg)
                        logging.warning(msg)
                        continue
                    # this will make sure that we do not have any duplication
                    # count when there are two new tags simultaneously
                    self.is_good_packet, need_to_switch, self.need_to_pause = \
                        self.encrypted_packet_filter(raw_data, group_id=gw_answer['group_id'])

                    if temperature_sensor_enable:
                        logging.info('%s' % gw_answer + ', temperatureFromSensor = ' + str(temperature_from_sensor))
                        raw_data['temperatureFromSensor'] = t.get_currentValue()

                    if self.is_good_packet:
                        if self.cur_tag_adv_addr == '':
                            self.cur_tag_adv_addr = self.adv_addr
                        if self.cur_tag_min_rssi > raw_data['rssi']:
                            self.cur_tag_min_rssi = raw_data['rssi']

                    if self.need_to_pause:
                        print('Due to current settings, the run will pause')
                        tag_data_list.append(raw_data)  # so we will know what caused the duplication

                        self.events.pause_to_tag_thread.set()
                        self.events.stop_to_r2r_thread.set()
                        break

                    if need_to_switch:
                        self.cur_tag_adv_addr = self.adv_addr
                        self.cur_tag_min_rssi = raw_data['rssi']
                        tag_data_list = []

                    if not self.is_good_packet:
                        continue
                    tag_data_list.append(raw_data)
                    if 'advAddress' in raw_data.keys():
                        print("------- Tag location: {} -------".format(self.tag_location),
                              "------- Tag advAddress: {} -------".format(str(raw_data['advAddress'])))
                    print(gw_answer)

                    # make the GW do only 900MHz energy pattern in order to test
                    # sub1G harvester (after calibration from first packet)
                    if 'Dual' in self.value['inlayType'] and not self.did_change_pattern:
                        self.did_change_pattern = True
                        config_gw(self.GwObj,
                                  energizing_pattern=self.internal_value['secondEnergizingPattern'],
                                  time_profile='0,6')
                        # self.GwObj.check_current_config()  # for debugging
                        # in order to clean all previous packets
                        sleep(0.005)  # the max amount of time per rdr (end of energy until transmission)
                        self.GwObj.reset_buffer()
                        config_gw(self.GwObj,
                                  energizing_pattern=self.internal_value['secondEnergizingPattern'],
                                  time_profile=self.internal_value['timeProfile'])
                        # restart the timer of ttfp
                        # the long timers will continue to count from the beginning of this test
                        if self.timer_for_ttfp is not '':
                            self.timer_for_ttfp.cancel()
                        self.ttfp_times_up = False
                        self.timer_for_ttfp = threading.Timer(float(self.value['maxTtfp']), self.end_of_time,
                                                              ['no packet arrived'])
                        self.timer_for_ttfp.start()
        # end of packet loop ########################################

        # close packets listeners:
        self.GwObj.stop_processes()  # run_packet_listener will restart the listening at the start of the next iteration
        self.GwObj.reset_buffer()

        # stop transmitting energy:
        if 'Dual' in self.value['inlayType'] and self.did_change_pattern:
            self.did_change_pattern = False  # double check
            config_gw(self.GwObj,
                      energizing_pattern=self.internal_value['energizingPattern'],
                      time_profile='0,6')
            # self.GwObj.check_current_config()  # for debugging
            logging.debug('Changed the GW duty cycle to 0,6 and energizing pattern back to '
                          + str(self.internal_value['energizingPattern']))
            print('Changed the GW duty cycle to 0,6 and energizing pattern back to '
                  + str(self.internal_value['energizingPattern']))
        else:
            config_gw(self.GwObj, time_profile='0,6')
            # self.GwObj.check_current_config()  # for debugging
            logging.debug('Changed the GW duty cycle to 0,6 - stop transmitting')
            print('Changed the GW duty cycle to 0,6 - stop transmitting')

        # for the previous tag print - make sure the last tag was printed:
        if self.to_print:
            if self.events.done_to_tag_thread.isSet():
                return
            else:
                self.done_or_printer_event.wait()

        # run several checks before moving to the next tag:
        # ------------------------------------------------
        # check if the stop button was pressed:
        if self.events.done_to_tag_thread.is_set():
            self.events.was_fail_to_printer.set()  # to avoid deadlock
            logging.info("The User pressed STOP")
            clear_timers()
            logging.debug('stop pressed after start GW happened. the last tag will be ignored')
            return 'Exit'
        # check if the pause button was pressed:
        elif self.events.pause_to_tag_thread.isSet():
            clear_timers()
            if self.need_to_pause:
                print("Tag will be registered as failed")
                logging.debug("Tag will be registered as failed")
                # write the data of the tag in case it failed with packets
                if len(tag_data_list) > 0:
                    data = process_encrypted_tags_data(tag_data_list, int(self.value['packetThreshold']),
                                                       fail_this_tag=True)
                    under_threshold += 1
                    if tags_data_log is None:
                        tags_data_log = CsvLog(header_type=HeaderType.TAG, path=tags_data_path,
                                               tester_type=TesterName.OFFLINE,
                                               temperature_sensor=temperature_sensor_enable)
                        tags_data_log.open_csv()
                        print("tags_data log file has been created")
                    tags_data_log.append_list_as_row(tags_data_log.dict_to_list(data))
                    logging.info("The data to the classifier is: " + str(data))

                # add the tag to the tags we have already seen
                # the last packet will always have good rssi if it is a good tag
                if not raw_data == '' and str(raw_data['rssi']) < self.internal_value['rssiThreshold'] and \
                        len(tag_data_list) > 1:  # if the len is bigger than 1 it means
                    # we saw a good packet from a new tag and we should save it
                    if len(self.tag_list) <= self.tag_list_len:
                        self.tag_list.append(str(raw_data['advAddress']))
                    else:
                        del self.tag_list[0]
                        self.tag_list.append(str(raw_data['advAddress']))
                # write the log if there were any packets.
                if len(tag_data_list) > 0:
                    if 'tag_id' in raw_data.keys():
                        logging.info("Tag {} has failed!".format(str(raw_data['tag_id'])))
                    elif 'advAddress' in raw_data.keys():
                        logging.info("Tag with advAddress {} has failed!".format(str(raw_data['advAddress'])))

                # will be printed as fail, will pause the run immediately after
                if not self.to_print:
                    self.events.r2r_ready.clear()
                self.events.fail_to_r2r_thread.set()
                if self.to_print:
                    self.events.was_fail_to_printer.set()

            if self.events.done_to_tag_thread.isSet():
                return
            else:
                self.events.cont_to_tag_thread.wait()
                self.events.cont_to_tag_thread.clear()
                self.events.pause_to_tag_thread.clear()
                self.events.cont_to_main_thread.set()
        # check if the continue button was pressed:
        elif self.events.cont_to_tag_thread.isSet():
            clear_timers()
            self.events.cont_to_tag_thread.clear()
            self.events.pause_to_tag_thread.clear()
            self.events.cont_to_main_thread.set()
        # check if we received enough packets to pass the current tag:
        elif len(tag_data_list) == int(self.value['packetThreshold']) and not self.need_to_pause:
            self.missing_labels_in_a_row = 0
            clear_timers()
            # add the tag to the tags we have already seen
            if len(self.tag_list) <= self.tag_list_len:
                self.tag_list.append(str(raw_data['advAddress']))
            else:
                del self.tag_list[0]
                self.tag_list.append(str(raw_data['advAddress']))
            print('Tag reached packet Threshold')
            data = process_encrypted_tags_data(data=tag_data_list, packet_threshold=int(self.value['packetThreshold']))
            if tags_data_log is None:
                tags_data_log = CsvLog(header_type=HeaderType.TAG, path=tags_data_path,
                                       tester_type=TesterName.OFFLINE,
                                       temperature_sensor=temperature_sensor_enable)
                tags_data_log.open_csv()
                print("tags_data log file has been created")
            tags_data_log.append_list_as_row(tags_data_log.dict_to_list(data))

            logging.info("The tag summary data is: " + str(data))
            # the tag is good
            self.printed_external_id, is_OK = get_printed_value(self.printing_value['stringBeforeCounter'],
                                                                self.printing_value['digitsInCounter'],
                                                                str(self.externalId), self.value['printingFormat'])
            if not is_OK:
                msg = 'printing counter reached a value that is bigger than the counter possible space.' \
                      ' the program will exit now'
                print(msg)
                logging.warning(msg)
                sys.exit(0)
            if temperature_sensor_enable:
                try:
                    print("*****************Tag with advAddress {} has passed, ".format(
                        str(raw_data['advAddress'])) + 'tag location is ' + str(
                        self.tag_location) + ' , '
                          + str(
                        {'advAddress': str(raw_data['advAddress']), 'externalId': self.printed_external_id,
                         'temperatureFromSensor': data['temperatureFromSensor']})
                          + '*****************')
                    logging.info(
                        "Tag with advAddress {} has passed!".format(
                            str(raw_data['advAddress'])) + ' tag location is: ' + str(
                            self.tag_location)
                        + ' ' + str(
                            {'advAddress': str(raw_data['advAddress']), 'externalId': self.printed_external_id,
                             'temperatureFromSensor': data['temperatureFromSensor']}))
                except Exception:
                    print("*****************Tag with advAddress {} has passed, ".format(
                        str(raw_data['advAddress'])) + 'tag location is ' + str(
                        self.tag_location) + ' , '
                          + str(
                        {'advAddress': str(raw_data['advAddress']), 'externalId': self.printed_external_id,
                         'temperatureFromSensor': data['temperatureFromSensor']})
                          + '*****************')
                    logging.info(
                        "Tag with advAddress {} has passed!".format(
                            str(raw_data['advAddress'])) + ' tag location is: ' + str(
                            self.tag_location)
                        + ' ' + str(
                            {'advAddress': str(raw_data['advAddress']), 'externalId': self.printed_external_id,
                             'temperatureFromSensor': data['temperatureFromSensor']}))
            else:
                try:
                    print("*****************Tag with advAddress {} has passed, ".format(
                        str(raw_data['advAddress'])) + 'tag location is ' + str(
                        self.tag_location) + ' , '
                          + str(
                        {'advAddress': str(raw_data['advAddress']), 'externalId': self.printed_external_id})
                          + '*****************')
                    logging.info(
                        "Tag with advAddress {} has passed!".format(
                            str(raw_data['advAddress'])) + ' tag location is: ' + str(
                            self.tag_location)
                        + ' ' + str(
                            {'advAddress': str(raw_data['advAddress']), 'externalId': self.printed_external_id}))
                except Exception:
                    print("*****************Tag with advAddress {} has passed, ".format(
                        str(raw_data['advAddress'])) + 'tag location is ' + str(
                        self.tag_location) + ' , '
                          + str(
                        {'advAddress': str(raw_data['advAddress']), 'externalId': self.printed_external_id})
                          + '*****************')
                    logging.info(
                        "Tag with advAddress {} has passed!".format(
                            str(raw_data['advAddress'])) + ' tag location is: ' + str(
                            self.tag_location)
                        + ' ' + str(
                            {'advAddress': str(raw_data['advAddress']), 'externalId': self.printed_external_id}))
            if not self.to_print:
                self.events.r2r_ready.clear()
            self.events.pass_to_r2r_thread.set()
            global passed
            passed += 1
            global last_pass_string
            last_pass_string = 'last pass tag\nadvAddress: ' + str(self.adv_addr) + ', tag location: ' + str(
                self.tag_location) + ', external ID: ' + self.printed_external_id
            if self.to_print:
                self.events.was_pass_to_printer.set()
                self.externalId += 1

                # payload = raw_data['raw_data']
                # if len(self.next_batch_to_serialization['upload_data']) == 0:
                #     self.next_batch_to_serialization = {'response': '',
                #                                         'upload_data': [{"payload": payload,
                #                                                          "tagId": self.printed_external_id}],
                #                                         'writing_lock': threading.Lock()}
                # else:
                #     self.next_batch_to_serialization['upload_data'].append({"payload": payload,
                #                                                             "tagId": self.printed_external_id})
                    # upload happens in TagThread.run()
            else:
                self.externalId += 1
                # TODO - remove next part and enable this part under toPrint....
                payload = raw_data['raw_data']
                if len(self.next_batch_to_serialization['upload_data']) == 0:
                    self.next_batch_to_serialization = {'response': '',
                                                        'upload_data': [{"payload": payload,
                                                                         "tagId": self.printed_external_id}],
                                                        'writing_lock': threading.Lock()}
                else:
                    self.next_batch_to_serialization['upload_data'].append({"payload": payload,
                                                                            "tagId": self.printed_external_id})
        # tag did not transmit for too long (self.value['maxTtfp']
        elif self.ttfp_times_up:
            if self.start_GW_happened:
                self.missing_labels_in_a_row = 0
            clear_timers()
            logging.debug("Tag has failed! did not transmit for {} seconds".format(str(self.value['maxTtfp'])))

            if not self.to_print:
                self.events.r2r_ready.clear()
            self.events.fail_to_r2r_thread.set()
            if self.to_print:
                self.events.was_fail_to_printer.set()
        # time is up  - tag failed
        elif self.start_GW_happened:
            self.missing_labels_in_a_row = 0
            clear_timers()
            logging.debug("Tag time is over.")
            # write the data of the tag in case it failed with packets
            if len(tag_data_list) > 0:
                data = process_encrypted_tags_data(tag_data_list, int(self.value['packetThreshold']))
                under_threshold += 1
                if tags_data_log is None:
                    tags_data_log = CsvLog(header_type=HeaderType.TAG, path=tags_data_path,
                                           tester_type=TesterName.OFFLINE,
                                           temperature_sensor=temperature_sensor_enable)
                    tags_data_log.open_csv()
                    print("tags_data log file has been created")
                tags_data_log.append_list_as_row(tags_data_log.dict_to_list(data))
                logging.info("The data to the classifier is: " + str(data))

            # add the tag to the tags we have already seen
            # the last packet will always have good rssi if it is a good tag
            if not raw_data == '' and str(raw_data['rssi']) < self.internal_value['rssiThreshold']:
                if len(self.tag_list) <= self.tag_list_len:
                    if len(tag_data_list) > 0:
                        self.tag_list.append(str(tag_data_list[-1]['advAddress']))
                else:
                    if len(tag_data_list) > 0:
                        del self.tag_list[0]
                        self.tag_list.append(str(tag_data_list[-1]['advAddress']))
            # write the log if there were any packets.
            if len(tag_data_list) > 0:
                if 'tag_id' in raw_data.keys():
                    logging.info("Tag {} has failed!".format(str(raw_data['tag_id'])))
                elif 'advAddress' in raw_data.keys():
                    logging.info("Tag with advAddress {} has failed!".format(str(raw_data['advAddress'])))
            if not self.to_print:
                self.events.r2r_ready.clear()
            self.events.fail_to_r2r_thread.set()
            if self.to_print:
                self.events.was_fail_to_printer.set()
        # missing label
        elif self.r2r_response_times_up:
            clear_timers()
            self.start_GW_happened = False
            print('R2R has not move for ' + str(self.time_out_to_missing_label)
                  + ' seconds , enforce a start_r2r & fail_r2r (the last spot will be fail)')
            logging.debug('R2R has not move for ' + str(
                self.time_out_to_missing_label) + ', enforce a start_r2r & fail_r2r')
            missing_labels += 1

            # will take care of the missing labels in a row situation
            if self.missing_labels_in_a_row > 0:
                self.missing_labels_in_a_row += 1
            else:
                self.missing_labels_in_a_row = 1

            if self.events.done_to_tag_thread.isSet():
                return
            else:
                if not self.is_missing_label_mode:
                    msg = 'missing label has been detected. The R2R will stop now'
                    print('Missing label has been detected. The R2R will stop now (you are in disable missing label mode)')
                    logging.warning(msg)
                    print('Please check the reel is OK and press Continue')
                    self.events.stop_to_r2r_thread.set()
                    self.events.cont_to_tag_thread.wait()
                    self.missing_labels_in_a_row = 0
                    self.events.cont_to_tag_thread.clear()
                    self.events.cont_to_main_thread.set()
                elif self.missing_labels_in_a_row > int(self.value['maxMissingLabels']):
                    msg = str(self.missing_labels_in_a_row) \
                          + ' missing labels in a row has been detected. The R2R will stop now'
                    print(str(self.missing_labels_in_a_row) + ' missing labels in a row has been detected')
                    print('The R2R will stop now')
                    logging.warning(msg)
                    print('Please check the reel is OK and press Continue')
                    self.events.stop_to_r2r_thread.set()
                    self.events.cont_to_tag_thread.wait()
                    self.missing_labels_in_a_row = 0
                    self.events.cont_to_tag_thread.clear()
                    self.events.cont_to_main_thread.set()
                else:
                    msg = str(self.missing_labels_in_a_row) + ' missing labels in a row has been detected'
                    print(msg)
                    logging.warning(msg)
                    if not self.to_print:
                        self.events.r2r_ready.clear()
                    self.events.start_to_r2r_thread.set()
        # check if printer error occurs:
        elif self.to_print:
            if self.events.done_to_tag_thread.isSet():
                return
            else:
                self.done_or_printer_event.wait()
            # to make sure that the tag thread will not proceed if an error occur
            if self.events.printer_error.isSet():
                clear_timers()
                if self.events.done_to_tag_thread.isSet():
                    return
                else:
                    self.events.cont_to_tag_thread.wait()
                    self.events.cont_to_tag_thread.clear()
                    self.events.pause_to_tag_thread.clear()
                    self.events.cont_to_main_thread.set()
                    self.events.printer_error.clear()
            else:
                self.events.printer_success.clear()

        # doing it last for the case of printer crash in the middle of the new_tag()
        global external_id_for_printer
        external_id_for_printer = self.externalId

    def closure_fn(self):
        """
           turn off the GW (reset) and closes the GW Comport
           Logging:
               'User pressed Stop!'
           """
        close_all_serialization_processes_when_they_done(self.serialization_threads_working)
        self.GwObj.stop_processes()
        self.GwObj.reset_buffer()
        self.GwObj.write('!reset')
        self.GwObj.close_port(is_reset=True)
        logging.debug("User pressed Stop!")
        print("TagThread is done")


class R2RThread(threading.Thread):
    """
    Thread that controls R2R machine

    Parameters:
        @type events: class MainEvents (costume made class that has all of the Events of the program threads)
        @param events: has all of the Events of the program threads
        @type ports_and_guis: class PortsAndGuis (costume made class that has all of the ports and gui inputs for the
              program threads)
        @param ports_and_guis: has all of the ports and gui inputs for the program threads

    Exceptions:

    @except Exception: 'r2r_thread got an Exception, press Continue or Stop'
            exception details will be printed
            Exception might be either:
                1. Send GPIO pulse failed
                2. GPIO pulse was sent twice

    Events:
        listen/ waits on:
        events.done_or_stop => event that equals to (events.done_to_r2r_thread OR events.stop_to_r2r_thread)
        events.done_to_r2r_thread => kills R2R thread main loop if set
        events.pass_to_r2r_thread => notify if current tag passed. if set, send pulse on "Pass" GPIO line
        events.fail_to_r2r_thread => notify if current tag failed. if set, send pulse on "Fail" GPIO line
        events.start_to_r2r_thread => enable/disable R2R movement. Sends pulse on "Start/Stop machine" GPIO line
        events.enable_missing_label_to_r2r_thread => notify if missing label mode is enabled
            (skips current tag location in case of missing label up to maxMissingLabels set by user)


        sets:
        events.r2r_ready => notify if R2R in ready for movement
        events.stop_to_r2r_thread => stops the R2R from running in case of end of run or exception

    Logging:
        the logging from this thread will be to logging.debug()
        """
    def __init__(self, events, ports_and_guis):
        """
        Initialize Constants
        """
        super(R2RThread, self).__init__()

        self.exception_queue = Queue()
        self.events = events
        self.done_or_stop = or_event_set(self.events.done_to_r2r_thread, self.events.stop_to_r2r_thread)
        self.r2r_events_or = or_event_set(self.events.pass_to_r2r_thread, self.events.fail_to_r2r_thread,
                                          self.events.start_to_r2r_thread, self.done_or_stop,
                                          self.events.enable_missing_label_to_r2r_thread)
        self.en_missing_label = False
        self.ports_and_guis = ports_and_guis

        self.my_gpio = self.ports_and_guis.R2R_myGPIO

    @pyqtSlot()
    def run(self):
        """
        runs the thread
        """
        die = False
        while not die:
            try:
                self.r2r_events_or.wait()
                if self.done_or_stop.is_set():
                    self.my_gpio.gpio_state(3, "OFF")
                    print("PC send stop to R2R")
                    self.events.stop_to_r2r_thread.clear()
                    if self.events.done_to_r2r_thread.isSet():
                        die = True
                if self.events.pass_to_r2r_thread.is_set():
                    self.my_gpio.pulse(1, 50)
                    print("^^^^^^^^^^^^^^^^^^ PC send pass to R2R ^^^^^^^^^^^^^^^^^^")
                    logging.debug(" ^^^^^^^^^^^^^^^^^^ PC send pass to R2R ^^^^^^^^^^^^^^^^^^")
                    self.events.pass_to_r2r_thread.clear()
                    self.events.r2r_ready.set()
                if self.events.fail_to_r2r_thread.is_set():
                    self.my_gpio.pulse(2, 50)
                    print("PC send fail to R2R")
                    logging.debug("PC send fail to R2R")
                    self.events.fail_to_r2r_thread.clear()
                    self.events.r2r_ready.set()
                if self.events.start_to_r2r_thread.is_set():
                    if self.en_missing_label:
                        self.my_gpio.gpio_state(3, "OFF")
                        time.sleep(0.5)  # just to be on the safe side
                    self.my_gpio.gpio_state(3, "ON")
                    time.sleep(0.5)  # just to be on the safe side
                    self.my_gpio.pulse(2, 50)
                    if self.en_missing_label:
                        print("PC send stop + start + fail to R2R")
                    else:
                        print("PC send start + fail to R2R")
                    self.events.start_to_r2r_thread.clear()
                    self.events.r2r_ready.set()
                if self.events.enable_missing_label_to_r2r_thread.is_set():
                    self.my_gpio.gpio_state(4, "ON")
                    print("PC send 'enable missing label' to R2R")
                    self.events.enable_missing_label_to_r2r_thread.clear()
                    self.en_missing_label = True
                if self.events.disable_missing_label_to_r2r_thread.is_set():
                    self.my_gpio.gpio_state(4, "OFF")
                    print("PC send 'disable missing label' to R2R")
                    self.events.disable_missing_label_to_r2r_thread.clear()
                    self.en_missing_label = False
            except Exception:
                exception_details = sys.exc_info()
                self.exception_queue.put(exception_details)
                self.events.stop_to_r2r_thread.set()  # to avoid from the run to continue printing in this case


class MainEvents:
    """
    Contains events that connect between all threads
    Events are set or cleared by threads
    Events are divided to four primary groups:
        1. TagThread events
        2. MainWindow events
        3. R2R (reel to reel machine) events
        4. Printer events

    Parameters: None
    Exceptions: None
    Events: None
    Logging: None
    """
    def __init__(self):
        """
        Initialize the events for the entire run
        """

        # set by tag_checker
        self.pass_to_r2r_thread = threading.Event()
        self.fail_to_r2r_thread = threading.Event()
        # set by main
        self.start_to_r2r_thread = threading.Event()
        self.stop_to_r2r_thread = threading.Event()
        self.cont_to_tag_thread = threading.Event()
        # only to be sure we initialize the counters to the printer counter
        self.cont_to_printer_thread = threading.Event()
        self.cont_to_main_thread = threading.Event()
        self.pause_to_tag_thread = threading.Event()
        self.enable_missing_label_to_r2r_thread = threading.Event()
        self.disable_missing_label_to_r2r_thread = threading.Event()
        self.done_to_tag_thread = threading.Event()
        self.done_to_printer_thread = threading.Event()
        self.done2r2r_ready = threading.Event()
        self.done_to_r2r_thread = threading.Event()
        self.tag_thread_is_ready_to_main = threading.Event()

        # set by r2r
        # both printer and tag thread will wait on it. only printer will .clear() it (in printing mode)
        self.r2r_ready = threading.Event()

        # printer events
        self.was_pass_to_printer = threading.Event()
        self.was_fail_to_printer = threading.Event()
        self.printer_success = threading.Event()
        self.printer_error = threading.Event()
        self.printer_event = or_event_set(self.printer_success, self.printer_error)

        # being used in printer thread too
        self.r2r_ready_or_done2tag = or_event_set(self.r2r_ready, self.done2r2r_ready)


class PortsAndGuis:
    """
    class which is responsible for initializing peripheral's ports and get data from run GUIs

    Parameters: None
    Exceptions: None
    Events: None
    Logging: None
    """
    def __init__(self):
        """
        Initialize the runs ports and gets data from the guis
        """

        # run values (1st GUI)
        self.Tag_Value = open_session()

        # Getting the config values
        self.init_config_values()

        # for Tag thread ###########

        # printing values (2nd GUI)
        if self.Tag_Value['toPrint'] == 'Yes':
            self.to_print = True
            if self.Tag_Value['printingFormat'] == 'String':
                self.Tag_Printing_Value, self.Tag_is_OK = printing_string_window()
                if not self.Tag_is_OK:
                    print('Impossible printing values entered by the user, the program will exit now')
                    sys.exit(0)
            elif self.Tag_Value['printingFormat'] == 'SGTIN':
                self.Tag_Printing_Value, self.Tag_is_OK = printing_sgtin_window()
            else:
                print('user chose unsupported printing format!!!')
        # path for log file
        new_path = 'logs/' + str(self.Tag_Value['batchName'])
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        global log_path, R2R_code_version
        global run_start_time, common_run_name
        global reel_name
        reel_name = self.Tag_Value['batchName']
        common_run_name = reel_name + run_start_time
        self.Tag_pathForLog = new_path + '/' + common_run_name + '@ver=' + R2R_code_version + '.log'
        self.Tag_pathForLog = self.Tag_pathForLog.replace(':', '-')
        log_path = self.Tag_pathForLog

        # temperature sensor
        global temperature_sensor_enable
        folder_path = 'configs'
        cfg_file_name = 'test_configs.json'
        # if file or folder doesn't exist will create json file with temperatureSensorEnable = 'No' and raise exception
        if os.path.isdir(folder_path):
            file_path = os.path.join(folder_path, cfg_file_name)
            if os.path.exists(file_path):
                cfg_data = open_json(folder_path=folder_path, file_path=os.path.join(folder_path, cfg_file_name))
            else:
                print("Config file doesn't exist\n Creating test_config.json")
                with open(file_path, 'w') as cfg:
                    json.dump({"temperatureSensorEnable": "No"}, cfg)
                raise Exception('test_config.json was created\n Temperature sensor is disabled\n'
                                'You will need to press Stop')
        else:
            print("'configs' directory doesn't exist\n Creating directory and test_config.json")
            os.mkdir(folder_path)
            file_path = os.path.join(folder_path, cfg_file_name)
            with open(file_path, 'w') as cfg:
                json.dump({"temperatureSensorEnable": "No"}, cfg)
            raise Exception('test_config.json was created\n Temperature sensor is disabled\n'
                            'You will need to press Stop')

        if cfg_data['temperatureSensorEnable'].upper() == 'NO':
            temperature_sensor_enable = False
        elif cfg_data['temperatureSensorEnable'].upper() == 'YES':
            temperature_sensor_enable = True
        else:  # illegal inputs will be ignored
            raise Exception("Valid values for temperatureSensorEnable are 'Yes' or 'No'\n You will need to press Stop")
        if temperature_sensor_enable:
            self.Tag_t = set_temperature()
        else:
            self.Tag_t = None
        # check if the system variable exist
        assert ('testerStationName' in os.environ), 'testerStationName is missing from PC environment variables, ' \
                                                    'please add it in the following convention:' \
                                                    ' <company name>_<tester number>'
        self.tag_tester_station_name = os.environ['testerStationName']
        # serial for GW
        self.GwObj = WiliotGateway(auto_connect=True, logger_name='root')

        # for Printer thread ###########
        self.Printer_socket = ''  # will only be opened by the thread
        if self.Tag_Value['printingFormat'] == 'String':
            self.filename = 'gui_printer_inputs_do_not_delete.json'
        elif self.Tag_Value['printingFormat'] == 'SGTIN':
            self.filename = 'gui_printer_inputs_4_SGTIN_do_not_delete.json'

        else:
            print('The print Job Name inserted is not supported at the moment, You will need to press Stop')

        # check printing configs and save it locally
        folder_path = 'configs'
        self.data_for_printing = open_json(folder_path=folder_path, file_path=os.path.join(folder_path, self.filename),
                                           default_values=DefaultGUIValues(
                                               self.Tag_Value['printingFormat']).default_gui_values)

        # create log filenames
        global run_data_path
        global tags_data_path
        self.tags_data_path = new_path + '/' + common_run_name + '@offline_tester@tags_data' + \
                                                                 '@ver=' + R2R_code_version + '.csv'
        self.tags_data_path = self.tags_data_path.replace(':', '-')
        self.run_data_path = new_path + '/' + common_run_name + '@offline_tester@run_data' + \
                                                                '@ver=' + R2R_code_version + '.csv'
        self.run_data_path = self.run_data_path.replace(':', '-')
        run_data_path = self.run_data_path
        tags_data_path = self.tags_data_path
        # create log files
        global tags_data_log
        if tags_data_log is None:
            tags_data_log = CsvLog(header_type=HeaderType.TAG, path=tags_data_path, tester_type=TesterName.OFFLINE,
                                   temperature_sensor=temperature_sensor_enable)
            tags_data_log.open_csv()
            print("tags_data log file has been created")

        # for R2R thread ###########
        self.R2R_myGPIO = R2rGpio()

    def open_printer_socket(self):
        """
        opens the printer socket
        """
        self.Printer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Printer_socket.connect((self.configs_for_printer_values['TCP_IP'],
                                     int(self.configs_for_printer_values['TCP_PORT'])))

    def update_printer_gui_inputs(self):
        """
        save the last pass value for crash support.
        passed global variable will be updated at tag Thread and should be correct here
        """
        self.data_for_printing['firstPrintingValue'] = str(int(self.data_for_printing['firstPrintingValue']) + 1)
        file_path = os.path.join('configs', self.filename)
        json.dump(self.data_for_printing, open(file_path, "w"))

    def init_config_values(self):
        """
        initialize the config values for the run
        """
        self.dir_config = 'configs'
        self.configs_for_gw_file_values_path = self.dir_config + '/configs_for_gw_values.json'
        self.configs_for_gw_file_values_path_dual_band = self.dir_config + '/configs_for_gw_values_dual_band.json'
        config_defaults = ConfigDefaults()
        if 'Dual' in self.Tag_Value['inlayType']:
            self.configs_for_gw_values = open_json(self.dir_config, self.configs_for_gw_file_values_path_dual_band,
                                                   config_defaults.get_dual_band_gw_defaults())
        else:
            self.configs_for_gw_values = open_json(self.dir_config, self.configs_for_gw_file_values_path,
                                                   config_defaults.get_single_band_gw_defaults())

        self.configs_for_printer_file_values_path = self.dir_config + '/configs_for_printer_values.json'
        self.configs_for_printer_values = open_json(self.dir_config, self.configs_for_printer_file_values_path,
                                                    config_defaults.get_printer_defaults())


class MainWindow(QMainWindow):
    """
    Thread that opens and controls the GUI, opens all threads, sets/clears timers for all threads and handles exceptions
    This class will call for upload to cloud

    Parameters:
        values set by user in Offline Tester GUI:
            @Allow multiple missing label in row: dropdown list "Yes"/"No"
                If set to "No" the run will pause when a missing label is detected
            @Max missing labels in a row: int
                In case this number of missing label in row is reached, the run will pause
            @To print?: dropdown list "Yes"/"No"
                Enable/Disable printer. If set to "Yes" printing GUI will be opened after user pressed "Submit"
            @What is the printing job format?: dropdown list "SGTIN"/"String"
            @Reel_name: str
            @Tags Generation: dropdown list with tags generation (e.g. "D2")
            @Inlay type: dropdown list with inlay types (e.g. "Dual Band")
            @Inlay serial number (3 digits): serial number for given inlay type
            @Test time [sec] (reel2reel controller->delay between steps = 999): max time before R2R moves to next tag
            @Fail if no packet received until [sec]: Max time TagThread will wait for first packet from tag
            @PacketThreshold: minimum amount of valid received packets from tag to pass
            @Desired amount of tags (will stop the run after this amount of tags): int.
                The run will pause after the amount written is reached. The user can choose to stop the run or continue.
            @Desired amount of pass (will stop the run after this amount of passes): int
                The run will pause after the amount written is reached in tags that passed.
                The user can choose to stop the run or continue.
            @Surface: dropdown list with various testing surfaces with given dielectric constant (Er)
            @Is converted?: dropdown list "Yes"/"No"  => if tag is converted or not
            @comments: text box for user comments

    Exceptions:
        @except Exception: exception occurred in one of the threads => calls look_for_exceptions()
            look_for_exceptions() will call handle_r2r_exception() which prints and handles the exception if possible

    Events:
        listen/ waits on:
            events.tag_thread_is_ready_to_main => event from TagThread. if set, TagThread is ready
            events.printer_event => wait for response from printer (printer_success or printer_error)
            events.printer_success => the last print was successful
            events.cont_to_main_thread => continue response received from TagThread
            events.r2r_ready => notify if R2R in ready for movement

        sets:
            events.start_to_r2r_thread => enable/disable R2R movement. Sends pulse on "Start/Stop machine" GPIO line
            events.stop_to_r2r_thread => stops the R2R from running in case of end of run or exception
            events.pause_to_tag_thread => pauses TagThread if exception happened of user pressed Pause
            events.done_to_tag_thread => closes TagThread at the end of the run
            events.cont_to_tag_thread => send continue to paused TagThread after user pressed continue
            events.done2r2r_ready => closes R2RThread
            events.done_to_r2r_thread => kills R2R thread main loop if set
            events.done_to_printer_thread => user pressed Stop (end the program) - to avoid deadlock
            events.cont_to_printer_thread => send continue to PrinterThread after Continue pressed by user


    Logging:
        logging to logging.debug() and logging.info()
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the runs threads and classes
        """
        try:
            super(MainWindow, self).__init__(*args, **kwargs)
            self.events = MainEvents()
            self.passed_every_50 = []
            self.last_tested_num = 0
            self.last_passed_num = 0
            self.yield_over_time = []
            self.calculate_interval = 10
            global calculate_interval
            calculate_interval = self.calculate_interval
            self.calculate_on = 50
            global calculate_on
            calculate_on = self.calculate_on
            self.first_reached_to_desired_passes = False
            self.first_reached_to_desired_tags = False
            self.yield_drop_happened = False
            self.yield_was_high_lately = True
            self.prev_y_len = 0
            self.waiting_for_user_to_press_stop_because_printer = False

            self.ports_and_guis = PortsAndGuis()

            self.r2r_thread = R2RThread(self.events, self.ports_and_guis)
            self.tag_checker_thread = TagThread(self.events, self.ports_and_guis)

            self.events.tag_thread_is_ready_to_main.wait()
            self.events.tag_thread_is_ready_to_main.clear()

            self.pass_job_name = self.tag_checker_thread.printing_value['passJobName']  # will be set inside config
            self.to_print = self.tag_checker_thread.to_print
            self.start_value = int(self.tag_checker_thread.printing_value['firstPrintingValue'])

            # printer set-up ####################################################################
            # happens here so we will wait less until the printer will start up (will happen in the background)
            if self.to_print:
                self.printer = Printer(self.start_value, self.pass_job_name, self.events, self.ports_and_guis)

            self.open_ui()  # starts recurring_timer() that starts look_for_exceptions()

            self.r2r_thread.start()
            self.tag_checker_thread.start()
            self.events.tag_thread_is_ready_to_main.wait()
            self.events.tag_thread_is_ready_to_main.clear()
            if self.to_print:
                self.printer.start()
                self.events.printer_event.wait()
                if self.events.printer_success.isSet():
                    self.events.printer_success.clear()
                    print('Printer is ready to start')

            self.events.start_to_r2r_thread.set()
        except Exception:
            exception_details = sys.exc_info()
            print('Exception detected during initialization:')
            logging.debug('Exception detected during initialization:')
            print_exception(exception_details)
            self.look_for_exceptions()

        # done will be raised from stop_fn (user pressed done)

    def open_ui(self):
        """
        opens the run main GUI that will present the run data and gives to the user ability to Stop/Continue/Pause
        """
        self.stop_label = QLabel("If you want to end this run, press stop")
        self.cont_label = QLabel("If you want to skip and fail this location, press Continue")
        self.reel_label = QLabel("Reel Name: ")
        self.reel_label.setStyleSheet('.QLabel {padding-top: 10px; font-weight: bold; font-size: 25px; color:#ff5e5e;}')
        self.tested = QLabel("Tested = 0, Passed = 0, Yield = -1%")
        self.last_pass = QLabel("No tag has passed yet :(")
        layout = QVBoxLayout()

        self.continue_ = QPushButton("Continue")
        self.continue_.setStyleSheet("background-color: green")
        self.continue_.pressed.connect(self.continue_fn)

        self.pause = QPushButton("Pause")
        self.pause.setStyleSheet("background-color: orange")
        self.pause.pressed.connect(self.pause_fn)

        self.stop = QPushButton("Stop")
        self.stop.setStyleSheet("background-color: red")
        self.stop.pressed.connect(self.stop_fn)

        self.graphWidget = pg.PlotWidget()
        self.x = []  # 0 time points
        self.y = []  # will contain the yield over time
        self.graphWidget.setBackground('w')
        # Add Title
        self.graphWidget.setTitle("Yield over time", color="b", size="30pt")
        styles = {"color": "#f00", "font-size": "20px"}
        self.graphWidget.setLabel("left", "Yield for the last 50 tags [%]", **styles)
        self.graphWidget.setLabel("bottom", "Last tag location [x*" + str(self.calculate_interval) + "+" +
                                  str(self.calculate_on) + "]", **styles)
        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line = self.graphWidget.plot(self.x, self.y, pen=pen)

        layout.addWidget(self.reel_label)
        layout.addWidget(self.cont_label)
        layout.addWidget(self.continue_)
        layout.addWidget(self.pause)
        layout.addWidget(self.stop_label)
        layout.addWidget(self.stop)
        layout.addWidget(self.last_pass)
        layout.addWidget(self.tested)
        layout.addWidget(self.graphWidget)

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)
        self.show()

        # updates the GUI and stops all if exception happened
        self.update_timer = QTimer()
        self.update_timer.setInterval(500)
        self.update_timer.timeout.connect(self.recurring_timer)
        self.update_timer.start()

    # GUI functions ##########################################################
    def stop_fn(self):
        """
        will be triggered by the Stop button and will end the run.
        will upload run's data to cloud and close the threads.
        """
        global tested
        global passed
        global missing_labels
        global last_pass_string
        global under_threshold
        if tested == 0:
            yield_ = -1.0
        else:
            yield_ = passed / tested * 100
        logging.debug("Stopped by the operator.")
        self.events.pause_to_tag_thread.set()
        self.update_timer.stop()
        values = save_screen()
        logging.info('Reels yield_over_time is: |' + str(self.yield_over_time) + '| interval: |' +
                     str(self.calculate_interval) + '|, on: |' + str(self.calculate_on))
        logging.info('Last words: ' + values['comments'])
        print('Tested = ' + str(tested) + ', Passed = ' + str(passed) + ', Yield = ' + str(yield_) + '%'
              + ', Missing labels = ' + str(missing_labels))
        logging.debug('Tested = ' + str(tested) + ', Passed = ' + str(passed) + ', Yield = ' + str(yield_) + '%'
                      + ', Missing labels = ' + str(missing_labels))
        self.events.done_to_tag_thread.set()
        self.events.done_to_printer_thread.set()
        self.events.done2r2r_ready.set()
        self.events.cont_to_tag_thread.set()  # to avoid deadlock
        self.events.done_to_r2r_thread.set()
        self.r2r_thread.join()
        # save last printed value, also being done after every pass by the printer thread (for crash support):
        if self.to_print:
            if self.tag_checker_thread.value['printingFormat'] == 'SGTIN':
                filename = 'gui_printer_inputs_4_SGTIN_do_not_delete.json'
                printing_format = 'SGTIN'
            else:
                filename = 'gui_printer_inputs_do_not_delete.json'
                printing_format = 'String'

            folder_path = 'configs'
            data = open_json(folder_path=folder_path, file_path=os.path.join(folder_path, filename),
                             default_values=DefaultGUIValues(printing_format).default_gui_values)
            data['firstPrintingValue'] = str(int(data['firstPrintingValue']) + 1)
            f = open(os.path.join(folder_path, filename), "w")
            json.dump(data, f)
            f.close()

        global run_data_log, log_path, run_data_dict, run_data_path
        if run_data_log is None:
            run_data_log = CsvLog(header_type=HeaderType.RUN, path=run_data_path, tester_type=TesterName.OFFLINE)
            run_data_log.open_csv()
        run_data_dict['passed'] = passed
        run_data_dict['tested'] = tested
        if tested > 0:  # avoid division by zero
            run_data_dict['yield'] = passed / tested
        if tested == 0:
            run_data_dict['yield'] = -1.0
        run_data_dict['yieldOverTime'] = self.yield_over_time
        run_data_dict['includingUnderThresholdPassed'] = under_threshold + passed
        if tested > 0:  # avoid division by zero
            run_data_dict['includingUnderThresholdYield'] = run_data_dict['includingUnderThresholdPassed'] / tested
        run_data_dict['errors'] = collect_errors(log_path)
        run_data_log.override_run_data(run_data_dict)

        global reel_name, test_reel, tags_data_path
        global log_name
        if values['upload'] == 'Yes' and not test_reel:
            parts1 = [i for i in run_data_path.split('/')]
            parts2 = [i for i in tags_data_path.split('/')]
            try:
                res = upload_to_cloud_api(batch_name=reel_name, tester_type='offline', run_data_csv_name=parts1[-1],
                                          tags_data_csv_name=parts2[-1], to_logging=True)
            except Exception:
                exception_details = sys.exc_info()
                print_exception(exception_details=exception_details)
                res = False

            if not res:
                logging.debug('Uploaded to cloud? ' + 'got an error while uploading to cloud')
                print('Upload to cloud failed!!!!!!!!!\n' + 'got an error while uploading to cloud')
            else:
                logging.debug('Uploaded to cloud? ' + values['upload'])
        else:
            logging.debug('Uploaded to cloud? No')

        self.tag_checker_thread.join()
        if self.to_print and not self.waiting_for_user_to_press_stop_because_printer:
            self.printer.join()

        sys.exit(0)

    def continue_fn(self):
        """
        will be triggered by the Continue button and will resume the run after Pause/ run got stuck if possible.
        """
        if not self.events.cont_to_tag_thread.isSet() and not self.waiting_for_user_to_press_stop_because_printer\
                and not self.tag_checker_thread.fetal_error:
            logging.debug("Continued by the operator after R2R has stopped.")
            print("user pressed Continue, the R2R will advance now (the last spot will be fail)")
            self.look_for_exceptions()
            self.events.cont_to_tag_thread.set()
            self.events.cont_to_printer_thread.set()
            self.events.cont_to_main_thread.wait()
            self.events.cont_to_main_thread.clear()
            self.events.start_to_r2r_thread.set()

    def pause_fn(self):
        """
        will be triggered by the Pause button and will pause the run if possible.
        """
        if not self.events.pause_to_tag_thread.isSet() and not self.waiting_for_user_to_press_stop_because_printer\
                and not self.tag_checker_thread.fetal_error:
            logging.debug("Paused by the operator.")
            print("user pressed Pause, the R2R will pause now (the current spot will be fail)")
            self.events.stop_to_r2r_thread.set()
            self.events.pause_to_tag_thread.set()

    def recurring_timer(self):
        """
        update the runs main GUI, checks that the other threads are OK (no exceptions)
        """
        global tested
        global passed
        global missing_labels
        global last_pass_string
        global reel_name

        if tested == 0:
            yield_ = -1.0
            self.reel_label.setText("Reel Name: " + reel_name)
        else:
            yield_ = passed / tested * 100
        self.tested.setText('Tested = ' + str(tested) + ', Passed = ' + str(passed) + ', Yield = ' + str(yield_) + '%'
                            + '\nMissing labels = ' + str(missing_labels))
        self.last_pass.setText(last_pass_string)
        # update the graph, if there was change in the tested amount
        # because passed and tested are been updated in different times
        # we will check the passed of the prev tag => tested -1
        if tested > self.last_tested_num:
            if self.calculate_on >= tested > self.last_tested_num:
                if passed - self.last_passed_num > 0:
                    self.passed_every_50.append(1)
                else:
                    self.passed_every_50.append(0)
            elif tested > 0:
                del self.passed_every_50[0]
                if passed - self.last_passed_num > 0:
                    self.passed_every_50.append(1)
                else:
                    self.passed_every_50.append(0)

            if len(self.passed_every_50) > self.calculate_on:
                print('self.passed_every_50 length is too long (self.passed_every_50 = ' +
                      str(self.passed_every_50) + ')')
            if tested % self.calculate_interval == 1 and tested > self.calculate_on:
                self.y.append(sum(self.passed_every_50) / self.calculate_on * 100)
                self.x = range(len(self.y))
                self.data_line.setData(self.x, self.y)  # Update the data.
                self.yield_over_time.append(int(sum(self.passed_every_50) / self.calculate_on * 100))
            if 0 < len(self.y) != self.prev_y_len and self.yield_was_high_lately:
                self.prev_y_len = len(self.y)
                if self.y[-1] == 0:  # 50 fails in a row => Pause the run
                    print('There are 50 fails in a row, please make sure everything is OK and press Continue')
                    logging.debug('There are 50 fails in a row, waiting to operator to press Continue')
                    self.yield_drop_happened = True
                    self.yield_was_high_lately = False
                    if not self.events.pause_to_tag_thread.isSet():
                        self.events.stop_to_r2r_thread.set()
                        self.events.pause_to_tag_thread.set()
                elif self.y[-1] < 40 and len(self.y) > 15:  # under 40% yield-over-time for 200 tags => Pause the run
                    self.yield_drop_happened = True
                    for ii in range(1, 15):
                        if self.y[-ii] < 40:
                            continue
                        else:
                            self.yield_drop_happened = False
                            break
                    if self.yield_drop_happened:
                        print('*' * 100)
                        print('The yield-over-time of the last 200 tags is below 40%,'
                              ' please make sure everything is OK and press Continue')
                        print('*' * 100)
                        logging.debug('The yield-over-time of the last 200 tags is below 40%,'
                                      ' waiting to operator to press Continue')
                        self.yield_was_high_lately = False
                        if not self.events.pause_to_tag_thread.isSet():
                            self.events.stop_to_r2r_thread.set()
                            self.events.pause_to_tag_thread.set()
                elif self.y[-1] > 50 and len(self.y) > 15:
                    self.yield_was_high_lately = True
            global yield_over_time
            yield_over_time = self.yield_over_time
            # update the prev counters
            self.last_tested_num += 1
            if passed > self.last_passed_num:
                self.last_passed_num += 1

        if tested == desired_tags_num and not self.first_reached_to_desired_tags:
            print('---------------------------Desired tags have reached (' + str(tested) +
                  ') , If you wish to proceed, press Continue---------------------------')
            logging.debug('Desired tags have reached (' + str(tested) + ') , If you wish to proceed, press Continue')
            self.first_reached_to_desired_tags = True
            self.pause_fn()
        if passed == desired_pass_num and not self.first_reached_to_desired_passes:
            print('---------------------------Desired passes have reached (' + str(passed) +
                  ') , If you wish to proceed, press Continue---------------------------')
            logging.debug('Desired passes have reached (' + str(passed) + ') , If you wish to proceed, press Continue')
            self.first_reached_to_desired_passes = True
            self.pause_fn()
        if not self.waiting_for_user_to_press_stop_because_printer:
            self.look_for_exceptions()

    def look_for_exceptions(self):
        """
        search for exceptions in the threads Exceptions Queues.
        """
        if self.to_print:
            if not self.printer.exception_queue.empty() or not self.tag_checker_thread.exception_queue.empty() or \
                    not self.r2r_thread.exception_queue.empty():
                if not self.events.pause_to_tag_thread.isSet():
                    logging.debug("Paused because an exception happened")
                    print("Paused because an exception happened, the R2R will pause now "
                          "(the current spot will be fail)")
                    self.events.stop_to_r2r_thread.set()
                    self.events.pause_to_tag_thread.set()
                self.handle_r2r_exception()
        elif not self.tag_checker_thread.exception_queue.empty() or not self.r2r_thread.exception_queue.empty():
            if not self.events.pause_to_tag_thread.isSet():
                logging.debug("Paused because an exception happened")
                print("Paused because an exception happened, the R2R will pause now (the current spot will be fail)")
                self.events.stop_to_r2r_thread.set()
                self.events.pause_to_tag_thread.set()
            self.handle_r2r_exception()

    def handle_r2r_exception(self):
        """
        handle the exception if possible. prints the exception to screen and log
        """
        if self.to_print:
            if not self.printer.exception_queue.empty():
                exception_details = self.printer.exception_queue.get()
                print('Printer got an Exception:')
                logging.debug('Printer got an Exception:')
                print_exception(exception_details)  # using logging.warning that will be parsed to errors
                exc_type, exc_obj, exc_trace = exception_details
                # ConnectionResetError => exc_obj = 'An existing connection was forcibly closed by the remote host'
                if isinstance(exc_obj, PrinterNeedsResetException):
                    print('please press Stop and start a new run')
                    logging.debug('Waiting for an operator to press Stop')
                    self.waiting_for_user_to_press_stop_because_printer = True
                    self.events.printer_error.set()  # to avoid deadlock when printer thread crashed before
                elif isinstance(exc_obj, ConnectionResetError):
                    self.events.done_to_printer_thread.set()
                    print('Will close socket to Printer and restart it, please wait...')
                    logging.debug('Will close socket to Printer and restart it')
                    self.events.printer_event.wait()
                else:
                    if self.events.r2r_ready.isSet():
                        self.events.r2r_ready.clear()
                    print('Please check everything is OK and press Continue')

        if not self.tag_checker_thread.exception_queue.empty():
            exception_details = self.tag_checker_thread.exception_queue.get()
            print('tag_checker_thread got an Exception, press Continue or Stop')
            logging.debug('tag_checker_thread got an Exception, waiting for an operator to press Continue or Stop')
            print_exception(exception_details)
        if not self.r2r_thread.exception_queue.empty():
            exception_details = self.r2r_thread.exception_queue.get()
            print('r2r_thread got an Exception, press Continue or Stop')
            logging.debug('r2r_thread got an Exception, waiting for an operator to press Continue or Stop')
            print_exception(exception_details)


# --------  main code:  ---------- #
app = QApplication([])
window = MainWindow()
app.exec_()

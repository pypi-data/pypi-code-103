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
import threading
from wiliot.gateway_api.gateway import *
from wiliot.wiliot_testers.tester_utils import *
from queue import Queue
import serial.tools.list_ports


tested = 0
passed = 0
printingLock = threading.Lock()


class CounterThread(threading.Thread):
    def __init__(self, events, ports_and_guis):
        super(CounterThread, self).__init__()
        self.events = events
        self.baud = '9600'
        self.ports_and_guis = ports_and_guis

    def run(self):
        buf = b''
        global tested
        while not self.events.stop.isSet():
            data = self.ports_and_guis.counter_port.readline()
            buf = b''
            if data.__len__() > 0:
                buf += data
                if b'\n' in buf:
                    try:
                        tmp = buf.decode().strip(' \t\n\r')
                        if "pulses detected" in tmp:
                            tested += 1
                        # if tested % 10 == 0:
                        #     with printingLock:
                        #         print("Counter: " + str(tmp))
                        buf = b''
                    except Exception:
                        with printingLock:
                            print('Warning: Could not decode counter data')
                        logging.debug('Warning: Could not decode counter data')
                        buf = b''
                        continue

        self.ports_and_guis.counter_close()


class PortsAndGuis:
    # TODO - fix description
    """
    holds all of the out side communication (gui or comports)
    class which holds all of the out side communication (GUI or comports)

    Parameters:
        @type value: dictionary
        @param value: output of open_session() (start GUI)
        @type testers_ports: list of serial.tools.list_ports.comports()[x].device()
        @param testers_ports: contains all GWs connected to PC except the charger
        @type charger_port: serial.tools.list_ports.comports()[x].device()
        @param charger_port: charger GW
        @type events: class MainEvents (costume made class that has all of the Events of the program threads)
        @param events: has all of the Events of the program threads

    Exceptions:
        @except Exception('No Arduino ports was found'): no Wiliot Arduino was found
        @except Exception("illegal gpio_command sent to gpio"): the command sent to Arduino was not 'end of charge',
            'bad<x>' or 'good<x>'  (<x> is tester number)

    Events:
        sets:
            events.testers_are_silent[tester_num] => tester <tester_num> stopped transmitting
            events.charger_is_silent => charger stopped transmitting

    Logging:
        logging.info() and logging.debug()
    """

    def __init__(self, value, testers_ports, charger_port, events):
        self.exception_queue = Queue()
        try:
            self.counter_baud = '9600'
            self.events = events
            # will be updated by loop thread, will be used by testers threads [batch, column, row]
            # loop thread is starting by adding 1 to location 0 -> batch starts from -1
            self.location_in_batch = [-1, 0, 0]  # [0-inf, 0-columns_num-1, 0-rows_num-1]
            self.init_config_values()
            self.testers_ports = testers_ports
            # for Charger thread ###########
            self.charger_port = charger_port
            # for Main thread ###########
            # run values
            self.value = value

            # check if the system variable exist
            assert ('TESTER_STATION_NAME' in os.environ), 'TESTER_STATION_NAME is missing from PC environment variables'
            self.tester_station_name = os.environ['TESTER_STATION_NAME']
            # todo write the station name to log and data frame
            # for Testers thread ###########
            self.testers_comPortObj = []
            # will have some empty parts, but will be more comfortable to read
            for i in range(len(self.testers_ports)):
                self.testers_comPortObj.append(WiliotGateway())
            # for counter thread ###########
            self.read_and_write_time_out_gpio = 0.5
            self.counter_find_and_open_port()
            self.gw_lock = threading.Lock()

        except Exception:
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)

    def counter_find_and_open_port(self):
        """
        @return: none
        """
        arduino_found = False
        self.counter_port = None
        try:
            ports_list = list(serial.tools.list_ports.comports())
            for port in ports_list:
                self.comport = port
                if 'Arduino' not in str(port):
                    continue
                try:
                    self.counter_port = serial.Serial(self.comport.device, self.counter_baud,
                                                      timeout=self.read_and_write_time_out_gpio,
                                                      write_timeout=self.read_and_write_time_out_gpio)
                    if self.counter_port.isOpen():
                        pass
                    else:
                        self.counter_port.open()
                    response = ''
                    self.counter_port.flushInput()
                    try:
                        self.counter_port.write(str.encode("*IDN?"))
                        time.sleep(0.4)
                        data = self.counter_port.readline()
                        response = data.decode("utf-8")
                        # Cut the last character as the device returns a null terminated string
                        with printingLock:
                            print('gpio unit response = ' + str(response))
                    except Exception:
                        with printingLock:
                            print(datetime.datetime.now().time(), "Sent: ", "*IDN?")
                            print(datetime.datetime.now().time(), "Recv: ", str(response))
                        exception_details = sys.exc_info()
                        self.exception_queue.put(exception_details)
                        return False

                    if "Wiliot Tester GPIO unit" in response:
                        if not arduino_found:
                            with printingLock:
                                print('Found ' + response)
                            self.counter_port.flushInput()
                            arduino_found = True
                        else:
                            with printingLock:
                                print("too many USB Serial Device connected, can't figure out which is the counter")
                            raise Exception('too many Arduino ports was found')
                    else:
                        self.counter_port.close()

                except Exception:
                    with printingLock:
                        print('failed to open the counter port')
                    exception_details = sys.exc_info()
                    self.exception_queue.put(exception_details)
                    print_exception(exception_details, printingLock)
            if not arduino_found:
                with printingLock:
                    print('No Arduino port was found. please connect the counter or call for support')
                raise Exception('No Arduino ports was found')
        except Exception:
            exception_details = sys.exc_info()
            self.exception_queue.put(exception_details)

    def counter_close(self):
        if self.counter_port is not None:
            self.counter_port.close()
        with printingLock:
            print("Counter: done")
        logging.info("Counter: done")


class MainEvents:
    """
    Contains events that connect between all threads
    Events are set or cleared by threads
    Events are divided to four primary groups:
        1. CounterThread events
        2. MainWindow events
        3. ChargerThread events
        4. TesterThread events

    Parameters: None
    Exceptions: None
    Events: None
    Logging: None
    """

    def __init__(self, ):
        self.done = threading.Event()
        self.stop = threading.Event()  # need to end this run because an severe error happened
        self.pause = threading.Event()
        self.continue_ = threading.Event()

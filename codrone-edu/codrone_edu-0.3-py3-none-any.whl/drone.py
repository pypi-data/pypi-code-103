import serial
import binascii
import random
import queue
import threading
from threading import Thread
from time import sleep
from struct import *
import time
from serial.tools.list_ports import comports
from queue import Queue
from operator import eq
import colorama
from colorama import Fore, Back, Style

from codrone_edu.protocol import *
from codrone_edu.storage import *
from codrone_edu.receiver import *
from codrone_edu.system import *
from codrone_edu.crc import *


def convertByteArrayToString(dataArray):
    if dataArray == None:
        return ""

    string = ""

    if (isinstance(dataArray, bytes)) or (isinstance(dataArray, bytearray)) or (not isinstance(dataArray, list)):
        for data in dataArray:
            string += "{0:02X} ".format(data)

    return string


class Drone:

    # BaseFunctions Start

    def __init__(self, flagCheckBackground=True, flagShowErrorMessage=False, flagShowLogMessage=False,
                 flagShowTransferData=False, flagShowReceiveData=False):

        self._serialport = None
        self._bufferQueue = Queue(4096)
        self._bufferHandler = bytearray()
        self._index = 0

        self._thread = None
        self._flagThreadRun = False

        self._receiver = Receiver()

        self._flagCheckBackground = flagCheckBackground

        self._flagShowErrorMessage = flagShowErrorMessage
        self._flagShowLogMessage = flagShowLogMessage
        self._flagShowTransferData = flagShowTransferData
        self._flagShowReceiveData = flagShowReceiveData

        self._eventHandler = EventHandler()
        self._storageHeader = StorageHeader()
        self._storage = Storage()
        self._storageCount = StorageCount()
        self._parser = Parser()

        self._devices = []  # Save a list of discovered devices when you autoconnect
        self._flagDiscover = False  # Indicate if the device is being scanned for autoconnect
        self._flagConnected = False  # Lets you know if you're connected to a device when you connect automatically

        self.timeStartProgram = time.time()  # Program Start Time Recording

        self.systemTimeMonitorData = 0
        self.monitorData = []

        self.altitude_data = [0, 0, 0, 0, 0]
        self.motion_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.state_data = [0, 0, 0, 0, 0, 0, 0]
        self.position_data = [0, 0, 0, 0]
        self.flow_data = [0, 0, 0]
        self.range_data = [0, 0, 0]
        self.joystick_data = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.color_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.trim_data = [0, 0, 0, 0, 0]

        # set the event handlers for the sensor requests
        self.setEventHandler(DataType.Altitude, self.update_altitude_data)
        self.setEventHandler(DataType.State, self.update_state_data)
        self.setEventHandler(DataType.Motion, self.update_motion_data)
        self.setEventHandler(DataType.Position, self.update_position_data)
        self.setEventHandler(DataType.RawFlow, self.update_flow_data)
        self.setEventHandler(DataType.Range, self.update_range_data)
        self.setEventHandler(DataType.Joystick, self.update_joystick_data)
        self.setEventHandler(DataType.CardColor, self.update_color_data)
        self.setEventHandler(DataType.Trim, self.update_trim_data)

        for i in range(0, 36):
            self.monitorData.append(i)

        self._control = ControlQuad8()

        colorama.init()

    def __del__(self):

        self.close()

    def update_altitude_data(self, drone_type):
        """
        temperature	Float32	4 Byte	-	temp.(℃)
        pressure	Float32	4 Byte	-	pressure
        altitude	Float32	4 Byte	-	Converting pressure to elevation above sea level(m)
        rangeHeight	Float32	4 Byte	-	Height value output from distance sensor(m)
        """

        self.altitude_data[0] = time.time() - self.timeStartProgram
        self.altitude_data[1] = drone_type.temperature
        self.altitude_data[2] = drone_type.pressure
        self.altitude_data[3] = drone_type.altitude
        self.altitude_data[4] = drone_type.rangeHeight

    def get_altitude_data(self, delay=0.01):
        self.sendRequest(DeviceType.Drone, DataType.Altitude)
        time.sleep(delay)
        return self.altitude_data

    def update_range_data(self, drone_type):
        '''
        Uses a time of flight sensor to detect the distance to an object
        Bottom range sensor will not update unless flying.
        Will display -1000 by default

        Front:  millimeters
        Bottom: millimeters
        '''
        self.range_data[0] = time.time() - self.timeStartProgram
        self.range_data[1] = drone_type.front
        self.range_data[2] = drone_type.bottom

    def get_range_data(self, delay=0.01):
        self.sendRequest(DeviceType.Drone, DataType.Range)
        time.sleep(delay)
        return self.range_data

    def get_front_range(self):
        return self.get_range_data()[1]

    def get_bottom_range(self):
        return self.get_range_data()[2]

    def update_color_data(self, drone_type):
        '''
        Reads the current sent over Hue, Saturation, Value, Luminosity
        values from the color sensors.
        There are 2 color sensors one in the front and one in the rear.
        Both positioned at the bottom of the drone

        front sensor: H,S,V,L
        read sensor : H,S,V,L
        Color       : color1, color2
        Card        : color_card
        '''

        self.color_data[0] = time.time() - self.timeStartProgram
        self.color_data[1] = drone_type.hsvl[0][0]
        self.color_data[2] = drone_type.hsvl[0][1]
        self.color_data[3] = drone_type.hsvl[0][2]
        self.color_data[4] = drone_type.hsvl[0][3]
        self.color_data[5] = drone_type.hsvl[1][0]
        self.color_data[6] = drone_type.hsvl[1][1]
        self.color_data[7] = drone_type.hsvl[1][2]
        self.color_data[8] = drone_type.hsvl[1][3]
        self.color_data[9] = drone_type.color[0]
        self.color_data[10] = drone_type.color[1]
        self.color_data[11] = drone_type.card

    def get_color_data(self, delay=0.01):
        self.sendRequest(DeviceType.Drone, DataType.CardColor)
        time.sleep(delay)
        return self.color_data

    def update_position_data(self, drone_type):
        """
        location of the drone
        x	Float32	4 Byte	-	X axis in meters
        y	Float32	4 Byte	-	Y axis in meters
        z	Float32	4 Byte	-	z axis in meters
        """
        self.position_data[0] = time.time() - self.timeStartProgram
        self.position_data[1] = drone_type.x
        self.position_data[2] = drone_type.y
        self.position_data[3] = drone_type.z

    def get_position_data(self, delay=0.01):
        self.sendRequest(DeviceType.Drone, DataType.Position)
        time.sleep(delay)
        return self.position_data

    def get_pos_x(self):
        return self.get_position_data()[1]

    def get_pos_y(self):
        return self.get_position_data()[2]

    def get_pos_z(self):
        return self.get_position_data()[3]

    def get_height(self):
        return self.get_position_data()[3]

    def update_flow_data(self, drone_type):
        """
        Relative position value calculated by optical flow sensor
        x	Float32	4 Byte	-	X axis(m)
        y	Float32	4 Byte	-	Y axis(m)
        """
        self.flow_data[0] = time.time() - self.timeStartProgram
        self.flow_data[1] = drone_type.x
        self.flow_data[2] = drone_type.y

    def get_flow_data(self, delay=0.01):
        self.sendRequest(DeviceType.Drone, DataType.RawFlow)
        time.sleep(delay)
        return self.flow_data

    def get_flow_x(self):
        return self.get_flow_data()[1]

    def get_flow_y(self):
        return self.get_flow_data()[2]


    def update_state_data(self, drone_type):

        """
        variable name	    form	          size	    range	Explanation
        modeSystem	        ModeSystem	      1 Byte	-	    System operating mode
        modeFlight	        ModeFlight	      1 Byte	-	    Flight controller operating mode
        modeControlFlight	ModeControlFlight 1 Byte	-	    flight control mode
        modeMovement	    ModeMovement	  1 Byte	-	    Moving state
        headless	        Headless	      1 Byte	-	    Headless setting status
        sensorOrientation	SensorOrientation 1 Byte	-	    Sensor orientation
        battery	            UInt8	          1 Byte	0~100	Drone battery level
        """
        self.state_data[0] = time.time() - self.timeStartProgram
        self.state_data[1] = drone_type.modeSystem
        self.state_data[2] = drone_type.modeFlight
        self.state_data[3] = drone_type.modeControlFlight
        self.state_data[4] = drone_type.headless
        self.state_data[5] = drone_type.sensorOrientation
        self.state_data[6] = drone_type.battery

    def get_state_data(self, delay=0.01):
        self.sendRequest(DeviceType.Drone, DataType.State)
        time.sleep(delay)
        return self.state_data

    def get_battery(self):
        return self.get_state_data()[6]

    def update_motion_data(self, drone_type):

        """
            Variable    Name    Type        Size          Range Unit     Description
        [0] time_elapsed          float                                 seconds
        [1] accelX	    Int16	2 Byte	-1568 ~ 1568 (-156.8 ~ 156.8)	m/s2 x 10	 X
        [2] accelY	    Int16	2 Byte	-1568 ~ 1568 (-156.8 ~ 156.8)	m/s2 x 10	 Y
        [3] accelZ	    Int16	2 Byte	-1568 ~ 1568 (-156.8 ~ 156.8)	m/s2 x 10	 Z
        [4] gyroRoll	Int16	2 Byte	-2000 ~ 2000	degree/second Roll
        [5] gyroPitch	Int16	2 Byte	-2000 ~ 2000	degree/second Pitch
        [6] gyroYaw  	Int16	2 Byte	-2000 ~ 2000	degree/second Yaw
        [7] angleRoll	Int16	2 Byte	-180 ~ 180	degree Roll
        [8] anglePitch	Int16	2 Byte	-180 ~ 180	degree Pitch
        [9] angleYaw	Int16	2 Byte	-180 ~ 180	degree Yaw
        """
        self.motion_data[0] = time.time() - self.timeStartProgram
        self.motion_data[1] = drone_type.accelX
        self.motion_data[2] = drone_type.accelY
        self.motion_data[3] = drone_type.accelZ
        self.motion_data[4] = drone_type.gyroRoll
        self.motion_data[5] = drone_type.gyroPitch
        self.motion_data[6] = drone_type.gyroYaw
        self.motion_data[7] = drone_type.angleRoll
        self.motion_data[8] = drone_type.anglePitch
        self.motion_data[9] = drone_type.angleYaw

    def get_motion_data(self, delay=0.01):
        self.sendRequest(DeviceType.Drone, DataType.Motion)
        time.sleep(delay)
        return self.motion_data

    def get_x_angle(self):
        return self.get_motion_data()[7]

    def get_y_angle(self):
        return self.get_motion_data()[8]

    def get_z_angle(self):
        return self.get_motion_data()[9]

    def update_joystick_data(self, drone_type):
        """
        variable  form	              size	    Range	    Explanation
        x	      Int8	              1 Byte	-100~100	X-axis value
        y	      Int8	              1 Byte	-100~100	Y-axis value
        direction Joystick Direction  1 Byte	-	        joystick direction
        event	  JoystickEvent	      1 Byte	-	        Event
        """
        self.joystick_data[0] = time.time() - self.timeStartProgram
        self.joystick_data[1] = drone_type.left.x
        self.joystick_data[2] = drone_type.left.y
        self.joystick_data[3] = drone_type.left.direction.name
        self.joystick_data[4] = drone_type.left.event.name
        self.joystick_data[5] = drone_type.right.x
        self.joystick_data[6] = drone_type.right.y
        self.joystick_data[7] = drone_type.right.direction.name
        self.joystick_data[8] = drone_type.right.event.name

    def get_joystick_data(self, delay=0.01):
        self.sendRequest(DeviceType.Drone, DataType.Joystick)
        time.sleep(delay)
        return self.joystick_data

    def update_trim_data(self, drone_type):
        """
        Updates and reads the trim values for
        roll, pitch, yaw, and throttle
        that are set on the drones internal memory.
        :param drone_type:
        :return: N/A
        """
        self.trim_data[0] = time.time() - self.timeStartProgram
        self.trim_data[1] = drone_type.roll
        self.trim_data[2] = drone_type.pitch
        self.trim_data[3] = drone_type.yaw
        self.trim_data[4] = drone_type.throttle

    def get_trim_data(self, delay=0.01):
        self.sendRequest(DeviceType.Drone, DataType.Trim)
        time.sleep(delay)
        return self.trim_data

    def _receiving(self):
        while self._flagThreadRun:

            self._bufferQueue.put(self._serialport.read())

            # Automatic update of data when incoming data background check is enabled
            if self._flagCheckBackground:
                while self.check() != DataType.None_:
                    pass

            # sleep(0.001)

    def isOpen(self):
        if self._serialport is not None:
            return self._serialport.isOpen()
        else:
            return False

    def isConnected(self):
        if not self.isOpen():
            return False
        else:
            return self._flagConnected

    def open(self, portname=None):
        """
        Open a serial port to the remote on a baud rate of 57600
        Checks the VID vendor ID 1155 for the CoDrone EDU remote
        in order to verify the correct device.

        Sends a battery request in order to verify a
        connection to the drone and displays the battery level

        :param portname: usb port path
        :return: Boolean (True if successful connection and false if not)
        """
        cde_remote_vid = 1155

        if portname is None:
            nodes = comports()
            size = len(nodes)

            for item in nodes:
                if item.vid == cde_remote_vid:
                    portname = item.device
                    print("Found CoDrone EDU remote ", portname)
                    break
        try:

            print("Connecting to remote")
            self._serialport = serial.Serial(
                port=portname,
                baudrate=57600)

            if self.isOpen():

                self._flagThreadRun = True
                self._thread = Thread(target=self._receiving, args=(), daemon=True)
                self._thread.start()
                self._printLog("Connected.({0})".format(portname))

            else:

                self._printError("Could not connect to device.")
                print("Serial port is not open")
                return False

        # TODO: Fix this bare except
        except:
            self._printError("Could not connect to device.")
            print("Could not find a CoDrone EDU remote")
            return False
        # check about 10 times
        for i in range(10):
            state = self.get_state_data()
            state_flight = state[2]
            if state_flight is ModeFlight.Ready:
                break

        if state_flight is ModeFlight.Ready:
            print("Connected to CoDrone EDU")
            battery = state[6]
            print("Battery =", battery, "%")
            for i in range(10):
                # disable the previous YPRT commands
                self.sendControl(0, 0, 0, 0)
                time.sleep(0.1)
        else:
            print("Could not find CoDrone EDU")
            print(state_flight)

        return True

    def close(self):
        # log output
        if self.isOpen():
            self._printLog("Closing serial port.")

        self._printLog("Thread Flag False.")

        if self._flagThreadRun:
            self._flagThreadRun = False
            sleep(0.1)

        self._printLog("Thread Join.")

        if self._thread is not None:
            self._thread.join(timeout=1)

        self._printLog("Port Close.")

        if self.isOpen():
            self._serialport.close()
            sleep(0.2)

    def makeTransferDataArray(self, header, data):
        if (header is None) or (data is None):
            return None

        if not isinstance(header, Header):
            return None

        if isinstance(data, ISerializable):
            data = data.toArray()

        crc16 = CRC16.calc(header.toArray(), 0)
        crc16 = CRC16.calc(data, crc16)

        dataArray = bytearray()
        dataArray.extend((0x0A, 0x55))
        dataArray.extend(header.toArray())
        dataArray.extend(data)
        dataArray.extend(pack('H', crc16))

        return dataArray

    def transfer(self, header, data):
        if not self.isOpen():
            return

        dataArray = self.makeTransferDataArray(header, data)

        self._serialport.write(dataArray)

        # send data output
        self._printTransferData(dataArray)

        return dataArray

    def check(self):
        while not self._bufferQueue.empty():
            dataArray = self._bufferQueue.get_nowait()
            self._bufferQueue.task_done()

            if (dataArray is not None) and (len(dataArray) > 0):
                # receive data output
                self._printReceiveData(dataArray)

                self._bufferHandler.extend(dataArray)

        while len(self._bufferHandler) > 0:
            stateLoading = self._receiver.call(self._bufferHandler.pop(0))

            # error output
            if stateLoading == StateLoading.Failure:
                # Incoming data output (skipped)
                self._printReceiveDataEnd()

                # Error message output
                self._printError(self._receiver.message)

            # log output
            if stateLoading == StateLoading.Loaded:
                # Incoming data output (skipped)
                self._printReceiveDataEnd()

                # Log output
                self._printLog(self._receiver.message)

            if self._receiver.state == StateLoading.Loaded:
                self._handler(self._receiver.header, self._receiver.data)
                return self._receiver.header.dataType

        return DataType.None_

    def checkDetail(self):
        while not self._bufferQueue.empty():
            dataArray = self._bufferQueue.get_nowait()
            self._bufferQueue.task_done()

            if (dataArray is not None) and (len(dataArray) > 0):
                # Receive data output
                self._printReceiveData(dataArray)

                self._bufferHandler.extend(dataArray)

        while len(self._bufferHandler) > 0:
            stateLoading = self._receiver.call(self._bufferHandler.pop(0))

            # Error output
            if stateLoading == StateLoading.Failure:
                # Incoming data output (skipped)
                self._printReceiveDataEnd()

                # Error message output
                self._printError(self._receiver.message)

            # Log output
            if stateLoading == StateLoading.Loaded:
                # Incoming data output (skipped)
                self._printReceiveDataEnd()

                # Log output
                self._printLog(self._receiver.message)

            if self._receiver.state == StateLoading.Loaded:
                self._handler(self._receiver.header, self._receiver.data)
                return self._receiver.header, self._receiver.data

        return None, None

    def _handler(self, header, dataArray):

        # Save incoming data
        self._runHandler(header, dataArray)

        # Run a callback event
        self._runEventHandler(header.dataType)

        # Monitor data processing
        self._runHandlerForMonitor(header, dataArray)

        # Verify data processing complete
        self._receiver.checked()

        return header.dataType

    def _runHandler(self, header, dataArray):

        # General data processing
        if self._parser.d[header.dataType] is not None:
            self._storageHeader.d[header.dataType] = header
            self._storage.d[header.dataType] = self._parser.d[header.dataType](dataArray)
            self._storageCount.d[header.dataType] += 1

    def _runEventHandler(self, dataType):
        if (isinstance(dataType, DataType)) and (self._eventHandler.d[dataType] is not None) and (
                self._storage.d[dataType] is not None):
            return self._eventHandler.d[dataType](self._storage.d[dataType])
        else:
            return None

    def _runHandlerForMonitor(self, header, dataArray):

        # Monitor data processing
        # Parse the received data self.monitorData[] Putting data in an array
        if header.dataType == DataType.Monitor:

            monitorHeaderType = MonitorHeaderType(dataArray[0])

            if monitorHeaderType == MonitorHeaderType.Monitor0:

                monitor0 = Monitor0.parse(dataArray[1:1 + Monitor0.getSize()])

                if monitor0.monitorDataType == MonitorDataType.F32:

                    dataCount = (dataArray.len() - 1 - Monitor0.getSize()) / 4

                    for i in range(0, dataCount):

                        if monitor0.index + i < len(self.monitorData):
                            index = 1 + Monitor0.getSize() + (i * 4)
                            self.monitorData[monitor0.index + i], = unpack('<f', dataArray[index:index + 4])

            elif monitorHeaderType == MonitorHeaderType.Monitor4:

                monitor4 = Monitor4.parse(dataArray[1:1 + Monitor4.getSize()])

                if monitor4.monitorDataType == MonitorDataType.F32:

                    self.systemTimeMonitorData = monitor4.systemTime

                    dataCount = (dataArray.len() - 1 - Monitor4.getSize()) / 4

                    for i in range(0, dataCount):

                        if monitor4.index + i < len(self.monitorData):
                            index = 1 + Monitor4.getSize() + (i * 4)
                            self.monitorData[monitor4.index + i], = unpack('<f', dataArray[index:index + 4])

            elif monitorHeaderType == MonitorHeaderType.Monitor8:

                monitor8 = Monitor8.parse(dataArray[1:1 + Monitor8.getSize()])

                if monitor8.monitorDataType == MonitorDataType.F32:

                    self.systemTimeMonitorData = monitor8.systemTime

                    dataCount = (dataArray.len() - 1 - Monitor8.getSize()) / 4

                    for i in range(0, dataCount):

                        if monitor8.index + i < len(self.monitorData):
                            index = 1 + Monitor8.getSize() + (i * 4)
                            self.monitorData[monitor8.index + i], = unpack('<f', dataArray[index:index + 4])

    def setEventHandler(self, dataType, eventHandler):

        if not isinstance(dataType, DataType):
            return

        self._eventHandler.d[dataType] = eventHandler

    def getHeader(self, dataType):

        if not isinstance(dataType, DataType):
            return None

        return self._storageHeader.d[dataType]

    def getData(self, dataType):

        if not isinstance(dataType, DataType):
            return None

        return self._storage.d[dataType]

    def getCount(self, dataType):

        if not isinstance(dataType, DataType):
            return None

        return self._storageCount.d[dataType]

    def _printLog(self, message):

        # Log output
        if self._flagShowLogMessage and message is not None:
            print(Fore.GREEN + "[{0:10.03f}] {1}".format((time.time() - self.timeStartProgram),
                                                         message) + Style.RESET_ALL)

    def _printError(self, message):

        # Error message output
        if self._flagShowErrorMessage and message is not None:
            print(
                Fore.RED + "[{0:10.03f}] {1}".format((time.time() - self.timeStartProgram), message) + Style.RESET_ALL)

    def _printTransferData(self, dataArray):

        # Send data output
        if self._flagShowTransferData and (dataArray is not None) and (len(dataArray) > 0):
            print(Back.YELLOW + Fore.BLACK + convertByteArrayToString(dataArray) + Style.RESET_ALL)

    def _printReceiveData(self, dataArray):

        # Receive data output
        if self._flagShowReceiveData and (dataArray is not None) and (len(dataArray) > 0):
            print(Back.CYAN + Fore.BLACK + convertByteArrayToString(dataArray) + Style.RESET_ALL, end='')

    def _printReceiveDataEnd(self):

        # Incoming data output (skipped)
        if self._flagShowReceiveData:
            print("")

    # BaseFunctions End

    # Common Start

    def sendPing(self, deviceType):

        if not isinstance(deviceType, DeviceType):
            return None

        header = Header()

        header.dataType = DataType.Ping
        header.length = Ping.getSize()
        header.from_ = DeviceType.Base
        header.to_ = deviceType

        data = Ping()

        data.systemTime = 0

        return self.transfer(header, data)

    def sendRequest(self, deviceType, dataType):

        if (not isinstance(deviceType, DeviceType)) or (not isinstance(dataType, DataType)):
            return None

        header = Header()

        header.dataType = DataType.Request
        header.length = Request.getSize()
        header.from_ = DeviceType.Base
        header.to_ = deviceType

        data = Request()

        data.dataType = dataType

        return self.transfer(header, data)

    def sendPairing(self, deviceType, address0, address1, address2, scramble, channel0, channel1, channel2, channel3):

        if ((not isinstance(deviceType, DeviceType)) or
                (not isinstance(address0, int)) or
                (not isinstance(address1, int)) or
                (not isinstance(address2, int)) or
                (not isinstance(scramble, int)) or
                (not isinstance(channel0, int)) or
                (not isinstance(channel1, int)) or
                (not isinstance(channel2, int)) or
                (not isinstance(channel3, int))):
            return None

        header = Header()

        header.dataType = DataType.Pairing
        header.length = Pairing.getSize()
        header.from_ = DeviceType.Base
        header.to_ = deviceType

        data = Pairing()

        data.address0 = address0
        data.address1 = address1
        data.address2 = address2
        data.scramble = scramble
        data.channel0 = channel0
        data.channel1 = channel1
        data.channel2 = channel2
        data.channel3 = channel3

        return self.transfer(header, data)

    # Common Start

    # Control Start
    def pair(self, portname=None):
        self.open(portname)

    def disconnect(self):
        self.close()

    def takeoff(self):
        self.reset_YPRT()
        self.sendTakeOff()

        timeout = 4
        init_time = time.time()
        time_elapsed = time.time() - init_time
        while time_elapsed < timeout:
            time_elapsed = time.time() - init_time
            state = self.get_state_data()
            state_flight = state[2]
            if state_flight is ModeFlight.TakeOff:
                print(state_flight)
                break
            else:
                self.sendTakeOff()

    def land(self):
        self.reset_YPRT()
        self.sendLanding()

        timeout = 4
        init_time = time.time()
        time_elapsed = time.time() - init_time
        while time_elapsed < timeout:
            time_elapsed = time.time() - init_time
            state = self.get_state_data()
            state_flight = state[2]
            if state_flight is ModeFlight.Landing:
                print(state_flight)
                break
            else:
                self.sendLanding()

        time.sleep(4)

    def emergency_stop(self):
        self.reset_YPRT()
        self.sendStop()

    def hover(self, duration=0.01):
        """
        :param duration: number of seconds to perform the hover command
        TODO: Make this command use the sensors to attempt to stay at that position
        :return: N/A
        """
        self.sendControl(0, 0, 0, 0)
        time.sleep(duration)


    # Movement control

    def reset_YPRT(self, attempts = 3):
        """
        resets the values of Yaw, Pitch, Roll and Throttle
        and sends them to the Drone.
        """
        # make sure the drone doesnt have any previous YPRT
        for i in range(attempts):
            self.hover()

    def set_roll(self, power):
        """
        sets the roll must be used with the move command
        :param power: int from 0-100
        :return:
        """
        self._control.roll = power

    def set_pitch(self, power):
        """
        sets the pitch must be used with the move command
        :param power: int from 0-100
        :return:
        """
        self._control.pitch = power

    def set_yaw(self, power):
        """
        sets the yaw must be used with the move command
        :param power: int from 0-100
        :return:
        """
        self._control.yaw = -power

    def set_throttle(self, power):
        """
        sets the throttle must be used with the move command
        :param power: int from 0-100
        :return:
        """
        self._control.throttle = power

    def move(self, duration=None):
        """
        Used with the set_pitch, set_yaw, set_throttle commands.
        used to the set values to be sent over to the drone.
        :param duration: Number of seconds to perform the action
        :return:
        """
        if duration is None:
            self.sendControl(*vars(self._control).values())
            time.sleep(0.005)

        else:
            milliseconds = int(duration * 1000)
            self.sendControlWhile(*vars(self._control).values(), milliseconds)
            sleep(duration)

    def print_move_values(self):
        """
        Prints what the current pitch , yaw
        and roll values are set to
        :return: None
        """
        print(*vars(self._control).values())

    def sendTakeOff(self):

        header = Header()

        header.dataType = DataType.Command
        header.length = Command.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Drone

        data = Command()

        data.commandType = CommandType.FlightEvent
        data.option = FlightEvent.TakeOff.value

        return self.transfer(header, data)

    def sendLanding(self):

        self._control.roll = 0
        self._control.pitch = 0
        self._control.yaw = 0
        self._control.throttle = 0

        header = Header()

        header.dataType = DataType.Command
        header.length = Command.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Drone

        data = Command()

        data.commandType = CommandType.FlightEvent
        data.option = FlightEvent.Landing.value

        return self.transfer(header, data)

    def sendStop(self):

        header = Header()

        header.dataType = DataType.Command
        header.length = Command.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Drone

        data = Command()

        data.commandType = CommandType.Stop
        data.option = 0

        return self.transfer(header, data)

    def sendControl(self, roll, pitch, yaw, throttle):
        '''
        It can be used for flying.

        roll	-100 ~ 100	Roll
        pitch	-100 ~ 100	Pitch
        yaw	-100 ~ 100	Yaw
        throttle	-100 ~ 100	Throttle
        :param roll: -100 ~ 100	Roll
        :param pitch: -100 ~ 100	Pitch
        :param yaw: -100 ~ 100	Yaw
        :param throttle:
        :return: transfer()
        '''

        if ((not isinstance(roll, int)) or (not isinstance(pitch, int)) or (not isinstance(yaw, int)) or (
                not isinstance(throttle, int))):
            return None

        header = Header()

        header.dataType = DataType.Control
        header.length = ControlQuad8.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Drone

        '''
        data = ControlQuad8()

        data.roll = roll
        data.pitch = pitch
        data.yaw = yaw
        data.throttle = throttle
        '''
        self._control.roll = roll
        self._control.pitch = pitch
        self._control.yaw = yaw
        self._control.throttle = throttle

        return self.transfer(header, self._control)

    def sendControlWhile(self, roll, pitch, yaw, throttle, timeMs):
        """
        It can be used for flying.
        Sends control commands continuously for the ms specified in timeMs.

        :param roll: -100 ~ 100	Roll
        :param pitch: -100 ~ 100	Pitch
        :param yaw: -100 ~ 100	Yaw
        :param throttle: -100 ~ 100	Throttle
        :param timeMs: 0 ~ 1,000,000	Operation time (milliseconds) must be an Integer
        :return:
        """

        if ((not isinstance(roll, int)) or
                (not isinstance(pitch, int)) or
                (not isinstance(yaw, int)) or
                (not isinstance(throttle, int))):
            return None

        time_sec = timeMs / 1000
        time_start = time.perf_counter()

        while (time.perf_counter() - time_start) < time_sec:
            self.sendControl(roll, pitch, yaw, throttle)
            sleep(0.02)

        return self.sendControl(roll, pitch, yaw, throttle)

    def sendControlPosition16(self, positionX, positionY, positionZ, velocity, heading, rotationalVelocity):
        """
        drone movement command

        Instead of using 2 byte integers for all variables,
         we apply x10 to the values of position and velocity.

        :param positionX: Int16	-100 ~ 100(-10.0 ~ 10.0)	meter x 10	Front (+), Back (-)
        :param positionY: Int16	-100 ~ 100(-10.0 ~ 10.0)	meter x 10	Left(+), Right(-)
        :param positionZ: Int16	-100 ~ 100(-10.0 ~ 10.0)	meter x 10	Up (+), Down (-)
        :param velocity: Int16	5 ~ 20(0.5 ~ 2.0)	m/s x 10	position movement speed
        :param heading: Int16	-360 ~ 360	degree	Turn left (+), turn right (-)
        :param rotationalVelocity: Int16	10 ~ 360	degree/s	left and right rotation speed
        :return:
        """

        if ((not isinstance(positionX, int)) or
                (not isinstance(positionY, int)) or
                (not isinstance(positionZ, int)) or
                (not isinstance(velocity, int))):
            return None

        if ((not isinstance(heading, int)) or
                (not isinstance(rotationalVelocity, int))):
            return None

        header = Header()

        header.dataType = DataType.Control
        header.length = ControlPosition16.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Drone

        data = ControlPosition16()

        data.positionX = positionX
        data.positionY = positionY
        data.positionZ = positionZ
        data.velocity = velocity
        data.heading = heading
        data.rotationalVelocity = rotationalVelocity

        return self.transfer(header, data)

    def sendControlPosition(self, positionX, positionY, positionZ, velocity, heading, rotationalVelocity):
        """
        drone movement command

        Use real values for position and velocity, and
        integer values for heading and rotational Velocity.
        :param positionX: float	-10.0 ~ 10.0	meter	Front (+), Back (-)
        :param positionY: float	-10.0 ~ 10.0	meter	Left(+), Right(-)
        :param positionZ: float	-10.0 ~ 10.0	meter	Up (+), Down (-)
        :param velocity: float	0.5 ~ 2.0	m/s	position movement speed
        :param heading: Int16	-360 ~ 360	degree	Turn left (+), turn right (-)
        :param rotationalVelocity:
        :return: Int16	10 ~ 360	degree/s	left and right rotation speed
        """

        if not (isinstance(positionX, float) or isinstance(positionX, int)):
            return None

        if not (isinstance(positionY, float) or isinstance(positionY, int)):
            return None

        if not (isinstance(positionZ, float) or isinstance(positionZ, int)):
            return None

        if not (isinstance(velocity, float) or isinstance(velocity, int)):
            return None

        if (not isinstance(heading, int)) or (not isinstance(rotationalVelocity, int)):
            return None

        header = Header()

        header.dataType = DataType.Control
        header.length = ControlPosition.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Drone

        data = ControlPosition()

        data.positionX = float(positionX)
        data.positionY = float(positionY)
        data.positionZ = float(positionZ)
        data.velocity = float(velocity)
        data.heading = heading
        data.rotationalVelocity = rotationalVelocity

        return self.transfer(header, data)

    # Control End
    def percent_error(self, desired, current):

        error_percent = (100 * (current - desired) / desired)

        # cap the value between -100% and 100%
        if error_percent > 100:
            error_percent = 100
        elif error_percent < -100:
            error_percent = -100

        return error_percent

    def turn_degree(self,degree, timeout=3):
        """
        turns relative to its current degree.
        as of right now it is only limited between +180 and -180
        :param degree: the degrees to turn - or + value
        :param timeout: seconds program will run
        :return:
        """

        # make sure you arent moving
        self.hover(0.01)
        p_value = 5
        init_time = time.time()
        time_elapsed = time.time() - init_time
        init_angle = self.get_z_angle()
        desired_angle = degree + init_angle
        if desired_angle > 180:
            remainder = desired_angle - 180
            desired_angle = 180

        elif desired_angle < -180:
            remainder = desired_angle - -180
            desired_angle = -180

        while time_elapsed < timeout:
            time_elapsed = time.time() - init_time
            current_angle = self.get_z_angle()
            error_percent = self.percent_error(desired=desired_angle,current=current_angle)
            error_percent = int(error_percent*p_value)
            # cap the value between -100% and 100%
            if error_percent > 100:
                error_percent = 100
            elif error_percent < -100:
                error_percent = -100

            self.sendControl(0, 0, -1*error_percent, 0)
            time.sleep(0.01)
        #stop any movement just in case
        self.hover()


    # Flight Sequences Start
    def avoid_wall(self, timeout=2, distance= 500):
        """
        A looped method that makes the drone fly forward until it reaches
        a desired distance. Once this distance is reached
        the drone will stop.
        range of front sensor is from 0-1000mm
        so from 0cm to 100cm

        :param timeout: in seconds, duration program
         will last
        :param distance: the distance at which
        the drone will stop. In millimeters
        :return:
        """
        threshold = 10
        p_value = 0.7

        init_time = time.time()
        time_elapsed = time.time() - init_time
        while time_elapsed < timeout:
            time_elapsed = time.time() - init_time
            current_distance = self.get_front_range()
            error_percent = self.percent_error(desired= distance,current= current_distance)
            # speed can range from -100 to 100
            speed = int(error_percent * p_value)

            if current_distance > distance + threshold or current_distance < distance - threshold:
                self.sendControl(0, speed, 0, 0)
                time.sleep(0.01)
            else:
                for i in range(20):
                    self.hover()
                break

    def keep_distance(self, timeout=2, distance= 500):
        """
        A looped method that makes the drone fly forward until it reaches
        a desired distance. Once this distance is reached
        the drone will stop.
        range of front sensor is from 0-1000mm
        so from 0cm to 100cm

        :param timeout: in seconds, duration program
         will last
        :param distance: the distance at which
        the drone will stop. In millimeters
        :return:
        """
        threshold = 10
        p_value = 0.7

        init_time = time.time()
        time_elapsed = time.time() - init_time
        while time_elapsed < timeout:
            time_elapsed = time.time() - init_time
            current_distance = self.get_front_range()
            error_percent = self.percent_error(desired= distance,current= current_distance)
            # speed can range from -100 to 100
            speed = int(error_percent * p_value)

            if current_distance > distance + threshold or current_distance < distance - threshold:
                self.sendControl(0, speed, 0, 0)
                time.sleep(0.01)
            else:
                self.hover()

    def detect_wall(self, distance= 500):
        """
        Once a distance below the input one it detected by the drone
        will return True
        range of front sensor is from 0-1000mm
        so from 0cm to 100cm

        :param distance: the distance in millimeters
        :return: Boolean
        """
        current_distance = self.get_front_range()

        if current_distance < distance:
            return True
        else:
            return False

    def square(self, speed=60, seconds=2, direction=1):

        power = speed
        duration_ms = int(seconds * 1000)
        for i in range(4):
            self.sendControlWhile(0, power, 0, 0, duration_ms)  # Pitch
            self.sendControlWhile(0, 0, power * direction, 0, duration_ms)
        sleep(1)

    def triangle(self, speed=60, seconds=2, direction=1):

        power = speed
        duration_ms = int(seconds * 1000)
        self.sendControlWhile(power * direction, power, 0, 0, duration_ms)
        self.sendControlWhile(power * direction, -power, 0, 0, duration_ms)
        self.sendControlWhile(-power * direction, 0, 0, 0, duration_ms)
        sleep(1)

    # Flight Sequences End

    # Setup Start

    def sendCommand(self, commandType, option=0):
        """
        Used to send commands to the drone.
        The option must contain either a value value
         of each format or a numeric value.
        https://dev.byrobot.co.kr/documents/kr/products/e_drone/library/python/e_drone/04_protocol/#CommandType
        :param commandType: CommandType	command type
        :param option: 	ModeControlFlight	option
                        FlightEvent
                        Headless
                        Trim
                        UInt8
        :return: transfer()
        """

        if ((not isinstance(commandType, CommandType)) or
                (not isinstance(option, int))):
            return None

        header = Header()

        header.dataType = DataType.Command
        header.length = Command.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Drone

        data = Command()

        data.commandType = commandType
        data.option = option

        return self.transfer(header, data)

    # Lights

    def set_drone_LED(self, r, g, b, brightness):

        self.sendLightModeColor(LightModeDrone.BodyHold, brightness, r, g, b)
        sleep(0.01)

    def set_remote_LED(self, r, g, b, brightness):
        self.sendLightModeColor(LightModeController.BodyHold, brightness, r, g, b)
        sleep(0.01)

    def sendCommandLightEvent(self, commandType, option, lightEvent, interval, repeat):
        """
        Command + LED Event
        Used to send commands to the drone.
        The option must contain either a value value of each format or a numeric value.

        :param commandType: CommandType	command type
        :param option:
        ModeControlFlight	option
        FlightEvent
        Headless
        Trim
        UInt8
        :param lightEvent: UInt8	LED operating mode
        :param interval: 0 ~ 65535	Internal brightness control function call cycle
        :param repeat: 0 ~ 255	number of repetitions
        :return: transfer()
        """

        if ((not isinstance(commandType, CommandType)) or
                (not isinstance(option, int)) or
                (not isinstance(interval, int)) or
                (not isinstance(repeat, int))):
            return None

        header = Header()

        header.dataType = DataType.Command
        header.length = CommandLightEvent.getSize()
        header.from_ = DeviceType.Base

        data = CommandLightEvent()

        if isinstance(lightEvent, LightModeDrone):
            header.to_ = DeviceType.Drone
            data.event.event = lightEvent.value

        elif isinstance(lightEvent, LightModeController):
            header.to_ = DeviceType.Controller
            data.event.event = lightEvent.value

        elif isinstance(lightEvent, int):
            header.to_ = DeviceType.Drone
            data.event.event = lightEvent

        else:
            return None

        data.command.commandType = commandType
        data.command.option = option

        data.event.interval = interval
        data.event.repeat = repeat

        return self.transfer(header, data)

    def sendCommandLightEventColor(self, commandType, option, lightEvent, interval, repeat, r, g, b):

        if ((not isinstance(commandType, CommandType)) or
                (not isinstance(option, int)) or
                (not isinstance(interval, int)) or
                (not isinstance(repeat, int)) or
                (not isinstance(r, int)) or
                (not isinstance(g, int)) or
                (not isinstance(b, int))):
            return None

        header = Header()

        header.dataType = DataType.Command
        header.length = CommandLightEventColor.getSize()
        header.from_ = DeviceType.Base

        data = CommandLightEventColor()

        if isinstance(lightEvent, LightModeDrone):
            header.to_ = DeviceType.Drone
            data.event.event = lightEvent.value

        elif isinstance(lightEvent, LightModeController):
            header.to_ = DeviceType.Controller
            data.event.event = lightEvent.value

        elif isinstance(lightEvent, int):
            header.to_ = DeviceType.Drone
            data.event.event = lightEvent

        else:
            return None

        data.command.commandType = commandType
        data.command.option = option

        data.event.interval = interval
        data.event.repeat = repeat

        data.color.r = r
        data.color.g = g
        data.color.b = b

        return self.transfer(header, data)

    def sendCommandLightEventColors(self, commandType, option, lightEvent, interval, repeat, colors):

        if ((not isinstance(commandType, CommandType)) or
                (not isinstance(option, int)) or
                (not isinstance(interval, int)) or
                (not isinstance(repeat, int)) or
                (not isinstance(colors, Colors))):
            return None

        header = Header()

        header.dataType = DataType.Command
        header.length = CommandLightEventColors.getSize()
        header.from_ = DeviceType.Base

        data = CommandLightEventColors()

        if isinstance(lightEvent, LightModeDrone):
            header.to_ = DeviceType.Drone
            data.event.event = lightEvent.value

        elif isinstance(lightEvent, LightModeController):
            header.to_ = DeviceType.Controller
            data.event.event = lightEvent.value

        elif isinstance(lightEvent, int):
            header.to_ = DeviceType.Drone
            data.event.event = lightEvent

        else:
            return None

        data.command.commandType = commandType
        data.command.option = option

        data.event.interval = interval
        data.event.repeat = repeat

        data.colors = colors

        return self.transfer(header, data)

    def sendModeControlFlight(self, modeControlFlight):

        if not isinstance(modeControlFlight, ModeControlFlight):
            return None

        header = Header()

        header.dataType = DataType.Command
        header.length = Command.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Drone

        data = Command()

        data.commandType = CommandType.ModeControlFlight
        data.option = modeControlFlight.value

        return self.transfer(header, data)

    def sendHeadless(self, headless):

        if not isinstance(headless, Headless):
            return None

        header = Header()

        header.dataType = DataType.Command
        header.length = Command.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Drone

        data = Command()

        data.commandType = CommandType.Headless
        data.option = headless.value

        return self.transfer(header, data)

    def sendTrim(self, roll, pitch, yaw, throttle):

        if ((not isinstance(roll, int)) or (not isinstance(pitch, int)) or (not isinstance(yaw, int)) or (
                not isinstance(throttle, int))):
            return None

        header = Header()

        header.dataType = DataType.Trim
        header.length = Trim.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Drone

        data = Trim()

        data.roll = roll
        data.pitch = pitch
        data.yaw = yaw
        data.throttle = throttle

        return self.transfer(header, data)

    def sendWeight(self, weight):

        header = Header()

        header.dataType = DataType.Weight
        header.length = Weight.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Drone

        data = Weight()

        data.weight = weight

        return self.transfer(header, data)

    def sendLostConnection(self, timeNeutral, timeLanding, timeStop):

        header = Header()

        header.dataType = DataType.LostConnection
        header.length = LostConnection.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Drone

        data = LostConnection()

        data.timeNeutral = timeNeutral
        data.timeLanding = timeLanding
        data.timeStop = timeStop

        return self.transfer(header, data)

    def sendFlightEvent(self, flightEvent):

        if ((not isinstance(flightEvent, FlightEvent))):
            return None

        header = Header()

        header.dataType = DataType.Command
        header.length = Command.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Drone

        data = Command()

        data.commandType = CommandType.FlightEvent
        data.option = flightEvent.value

        return self.transfer(header, data)

    def sendClearBias(self):

        header = Header()

        header.dataType = DataType.Command
        header.length = Command.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Drone

        data = Command()

        data.commandType = CommandType.ClearBias
        data.option = 0

        return self.transfer(header, data)

    def sendClearTrim(self):

        header = Header()

        header.dataType = DataType.Command
        header.length = Command.getSize()
        header.from_ = DeviceType.Tester
        header.to_ = DeviceType.Drone

        data = Command()

        data.commandType = CommandType.ClearTrim
        data.option = 0

        return self.transfer(header, data)

    def sendSetDefault(self, deviceType):

        if ((not isinstance(deviceType, DeviceType))):
            return None

        header = Header()

        header.dataType = DataType.Command
        header.length = Command.getSize()
        header.from_ = DeviceType.Base
        header.to_ = deviceType

        data = Command()

        data.commandType = CommandType.SetDefault
        data.option = 0

        return self.transfer(header, data)

    def sendBacklight(self, flagPower):

        if ((not isinstance(flagPower, bool))):
            return None

        header = Header()

        header.dataType = DataType.Command
        header.length = Command.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Controller

        data = Command()

        data.commandType = CommandType.Backlight
        data.option = int(flagPower)

        return self.transfer(header, data)

    # Setup End

    # Device Start

    def sendMotor(self, motor0, motor1, motor2, motor3):

        if ((not isinstance(motor0, int)) or
                (not isinstance(motor1, int)) or
                (not isinstance(motor2, int)) or
                (not isinstance(motor3, int))):
            return None

        header = Header()

        header.dataType = DataType.Motor
        header.length = Motor.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Drone

        data = Motor()

        data.motor[0].rotation = Rotation.Clockwise
        data.motor[0].value = motor0

        data.motor[1].rotation = Rotation.Counterclockwise
        data.motor[1].value = motor1

        data.motor[2].rotation = Rotation.Clockwise
        data.motor[2].value = motor2

        data.motor[3].rotation = Rotation.Counterclockwise
        data.motor[3].value = motor3

        return self.transfer(header, data)

    def sendMotorSingle(self, target, rotation, value):

        if ((not isinstance(target, int)) or
                (not isinstance(rotation, Rotation)) or
                (not isinstance(value, int))):
            return None

        header = Header()

        header.dataType = DataType.MotorSingle
        header.length = MotorSingle.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Drone

        data = MotorSingle()

        data.target = target
        data.rotation = rotation
        data.value = value

        return self.transfer(header, data)

    # Device End

    # Light Start

    def sendLightManual(self, deviceType, flags, brightness):

        if ((not isinstance(deviceType, DeviceType)) or
                (not isinstance(flags, int)) or
                (not isinstance(brightness, int))):
            return None

        header = Header()

        header.dataType = DataType.LightManual
        header.length = LightManual.getSize()
        header.from_ = DeviceType.Base
        header.to_ = deviceType

        data = LightManual()

        data.flags = flags
        data.brightness = brightness

        return self.transfer(header, data)

    def sendLightModeColor(self, lightMode, interval, r, g, b):

        if ((not isinstance(lightMode, int)) or
                (not isinstance(interval, int)) or
                (not isinstance(r, int)) or
                (not isinstance(g, int)) or
                (not isinstance(b, int))):
            return None

        header = Header()

        header.dataType = DataType.LightMode
        header.length = LightModeColor.getSize()
        header.from_ = DeviceType.Base

        data = LightModeColor()

        if isinstance(lightMode, LightModeDrone):
            header.to_ = DeviceType.Drone
            data.mode.mode = lightMode.value

        elif isinstance(lightMode, LightModeController):
            header.to_ = DeviceType.Controller
            data.mode.mode = lightMode.value

        elif isinstance(lightMode, int):
            header.to_ = DeviceType.Drone
            data.mode.mode = lightMode

        else:
            return None

        data.mode.interval = interval

        data.color.r = r
        data.color.g = g
        data.color.b = b

        return self.transfer(header, data)

    def sendLightModeColors(self, lightMode, interval, colors):

        if ((not isinstance(interval, int)) or
                (not isinstance(colors, Colors))):
            return None

        header = Header()

        header.dataType = DataType.LightMode
        header.length = LightModeColors.getSize()
        header.from_ = DeviceType.Base

        data = LightModeColors()

        if isinstance(lightMode, LightModeDrone):
            header.to_ = DeviceType.Drone
            data.mode.mode = lightMode.value

        elif isinstance(lightMode, LightModeController):
            header.to_ = DeviceType.Controller
            data.mode.mode = lightMode.value

        elif isinstance(lightMode, int):
            header.to_ = DeviceType.Drone
            data.mode.mode = lightMode

        else:
            return None

        data.mode.interval = interval
        data.colors = colors

        return self.transfer(header, data)

    def sendLightEventColor(self, lightEvent, interval, repeat, r, g, b):

        if ((not isinstance(interval, int)) or
                (not isinstance(repeat, int)) or
                (not isinstance(r, int)) or
                (not isinstance(g, int)) or
                (not isinstance(b, int))):
            return None

        header = Header()

        header.dataType = DataType.LightEvent
        header.length = LightEventColor.getSize()
        header.from_ = DeviceType.Base

        data = LightEventColor()

        if isinstance(lightEvent, LightModeDrone):
            header.to_ = DeviceType.Drone
            data.event.event = lightEvent.value

        elif isinstance(lightEvent, LightModeController):
            header.to_ = DeviceType.Controller
            data.event.event = lightEvent.value

        elif isinstance(lightEvent, int):
            header.to_ = DeviceType.Drone
            data.event.event = lightEvent

        else:
            return None

        data.event.interval = interval
        data.event.repeat = repeat

        data.color.r = r
        data.color.g = g
        data.color.b = b

        return self.transfer(header, data)

    def sendLightEventColors(self, lightEvent, interval, repeat, colors):

        if ((not isinstance(interval, int)) or
                (not isinstance(repeat, int)) or
                (not isinstance(colors, Colors))):
            return None

        header = Header()

        header.dataType = DataType.LightEvent
        header.length = LightEventColors.getSize()
        header.from_ = DeviceType.Base

        data = LightEventColors()

        if isinstance(lightEvent, LightModeDrone):
            header.to_ = DeviceType.Drone
            data.event.event = lightEvent.value

        elif isinstance(lightEvent, LightModeController):
            header.to_ = DeviceType.Controller
            data.event.event = lightEvent.value

        elif isinstance(lightEvent, int):
            header.to_ = DeviceType.Drone
            data.event.event = lightEvent

        else:
            return None

        data.event.interval = interval
        data.event.repeat = repeat

        data.colors = colors

        return self.transfer(header, data)

    def sendLightDefaultColor(self, lightMode, interval, r, g, b):

        if ((not isinstance(interval, int)) or
                (not isinstance(r, int)) or
                (not isinstance(g, int)) or
                (not isinstance(b, int))):
            return None

        header = Header()

        header.dataType = DataType.LightDefault
        header.length = LightModeColor.getSize()
        header.from_ = DeviceType.Base

        data = LightModeColor()

        if isinstance(lightMode, LightModeDrone):
            header.to_ = DeviceType.Drone
            data.mode.mode = lightMode.value

        elif isinstance(lightMode, LightModeController):
            header.to_ = DeviceType.Controller
            data.mode.mode = lightMode.value

        elif isinstance(lightMode, int):
            header.to_ = DeviceType.Drone
            data.mode.mode = lightMode

        else:
            return None

        data.mode.interval = interval

        data.color.r = r
        data.color.g = g
        data.color.b = b

        return self.transfer(header, data)

    # Light End

    # Color Start

    def get_colors(self):
        """
        Access the color data using the default ByRobot
        color prediction
        color 1 is the front sensor
        color 2 is the back sensor
        """
        color1 = self.get_color_data()[9].name
        color2 = self.get_color_data()[10].name
        colors = [color1, color2]
        return colors

    def get_front_color(self):
        return self.get_color_data()[9].name

    def get_back_color(self):
        return self.get_color_data()[10].name


    # Color End

    # Display Start

    def sendDisplayClearAll(self, pixel=DisplayPixel.Black):

        if (not isinstance(pixel, DisplayPixel)):
            return None

        header = Header()

        header.dataType = DataType.DisplayClear
        header.length = DisplayClearAll.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Controller

        data = DisplayClearAll()

        data.pixel = pixel

        return self.transfer(header, data)

    def sendDisplayClear(self, x, y, width, height, pixel=DisplayPixel.Black):

        if (not isinstance(pixel, DisplayPixel)):
            return None

        header = Header()

        header.dataType = DataType.DisplayClear
        header.length = DisplayClear.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Controller

        data = DisplayClear()

        data.x = x
        data.y = y
        data.width = width
        data.height = height
        data.pixel = pixel

        return self.transfer(header, data)

    def sendDisplayInvert(self, x, y, width, height):

        header = Header()

        header.dataType = DataType.DisplayInvert
        header.length = DisplayInvert.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Controller

        data = DisplayInvert()

        data.x = x
        data.y = y
        data.width = width
        data.height = height

        return self.transfer(header, data)

    def sendDisplayDrawPoint(self, x, y, pixel=DisplayPixel.White):

        if (not isinstance(pixel, DisplayPixel)):
            return None

        header = Header()

        header.dataType = DataType.DisplayDrawPoint
        header.length = DisplayDrawPoint.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Controller

        data = DisplayDrawPoint()

        data.x = x
        data.y = y
        data.pixel = pixel

        return self.transfer(header, data)

    def sendDisplayDrawLine(self, x1, y1, x2, y2, pixel=DisplayPixel.White, line=DisplayLine.Solid):

        if ((not isinstance(pixel, DisplayPixel)) or (not isinstance(line, DisplayLine))):
            return None

        header = Header()

        header.dataType = DataType.DisplayDrawLine
        header.length = DisplayDrawLine.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Controller

        data = DisplayDrawLine()

        data.x1 = x1
        data.y1 = y1
        data.x2 = x2
        data.y2 = y2
        data.pixel = pixel
        data.line = line

        return self.transfer(header, data)

    def sendDisplayDrawRect(self, x, y, width, height, pixel=DisplayPixel.White, flagFill=False,
                            line=DisplayLine.Solid):

        if ((not isinstance(pixel, DisplayPixel)) or (not isinstance(flagFill, bool)) or (
                not isinstance(line, DisplayLine))):
            return None

        header = Header()

        header.dataType = DataType.DisplayDrawRect
        header.length = DisplayDrawRect.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Controller

        data = DisplayDrawRect()

        data.x = x
        data.y = y
        data.width = width
        data.height = height
        data.pixel = pixel
        data.flagFill = flagFill
        data.line = line

        return self.transfer(header, data)

    def sendDisplayDrawCircle(self, x, y, radius, pixel=DisplayPixel.White, flagFill=True):

        if ((not isinstance(pixel, DisplayPixel)) or (not isinstance(flagFill, bool))):
            return None

        header = Header()

        header.dataType = DataType.DisplayDrawCircle
        header.length = DisplayDrawCircle.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Controller

        data = DisplayDrawCircle()

        data.x = x
        data.y = y
        data.radius = radius
        data.pixel = pixel
        data.flagFill = flagFill

        return self.transfer(header, data)

    def sendDisplayDrawString(self, x, y, message, font=DisplayFont.LiberationMono5x8, pixel=DisplayPixel.White):

        if ((not isinstance(font, DisplayFont)) or (not isinstance(pixel, DisplayPixel)) or (
                not isinstance(message, str))):
            return None

        header = Header()

        header.dataType = DataType.DisplayDrawString
        header.length = DisplayDrawString.getSize() + len(message)
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Controller

        data = DisplayDrawString()

        data.x = x
        data.y = y
        data.font = font
        data.pixel = pixel
        data.message = message

        return self.transfer(header, data)

    def sendDisplayDrawStringAlign(self, x_start, x_end, y, message, align=DisplayAlign.Center,
                                   font=DisplayFont.LiberationMono5x8, pixel=DisplayPixel.White):

        if ((not isinstance(align, DisplayAlign)) or (not isinstance(font, DisplayFont)) or (
                not isinstance(pixel, DisplayPixel)) or (not isinstance(message, str))):
            return None

        header = Header()

        header.dataType = DataType.DisplayDrawStringAlign
        header.length = DisplayDrawStringAlign.getSize() + len(message)
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Controller

        data = DisplayDrawStringAlign()

        data.x_start = x_start
        data.x_end = x_end
        data.y = y
        data.align = align
        data.font = font
        data.pixel = pixel
        data.message = message

        return self.transfer(header, data)

    # Display End

    # Buzzer Start

    def sendBuzzer(self, mode, value, time):

        if ((not isinstance(mode, BuzzerMode)) or
                (not isinstance(value, int)) or
                (not isinstance(time, int))):
            return None

        header = Header()

        header.dataType = DataType.Buzzer
        header.length = Buzzer.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Controller

        data = Buzzer()

        data.mode = mode
        data.value = value
        data.time = time

        return self.transfer(header, data)

    def sendBuzzerMute(self, time):

        if (not isinstance(time, int)):
            return None

        header = Header()

        header.dataType = DataType.Buzzer
        header.length = Buzzer.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Controller

        data = Buzzer()

        data.mode = BuzzerMode.Mute
        data.value = BuzzerScale.Mute.value
        data.time = time

        return self.transfer(header, data)

    def sendBuzzerMuteReserve(self, time):

        if (not isinstance(time, int)):
            return None

        header = Header()

        header.dataType = DataType.Buzzer
        header.length = Buzzer.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Controller

        data = Buzzer()

        data.mode = BuzzerMode.MuteReserve
        data.value = BuzzerScale.Mute.value
        data.time = time

        return self.transfer(header, data)

    def sendBuzzerScale(self, scale, time):

        if ((not isinstance(scale, BuzzerScale)) or
                (not isinstance(time, int))):
            return None

        header = Header()

        header.dataType = DataType.Buzzer
        header.length = Buzzer.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Controller

        data = Buzzer()

        data.mode = BuzzerMode.Scale
        data.value = scale.value
        data.time = time

        return self.transfer(header, data)

    def sendBuzzerScaleReserve(self, scale, time):

        if ((not isinstance(scale, BuzzerScale)) or
                (not isinstance(time, int))):
            return None

        header = Header()

        header.dataType = DataType.Buzzer
        header.length = Buzzer.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Controller

        data = Buzzer()

        data.mode = BuzzerMode.ScaleReserve
        data.value = scale.value
        data.time = time

        return self.transfer(header, data)

    def sendBuzzerHz(self, hz, time):

        if ((not isinstance(hz, int)) or
                (not isinstance(time, int))):
            return None

        header = Header()

        header.dataType = DataType.Buzzer
        header.length = Buzzer.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Controller

        data = Buzzer()

        data.mode = BuzzerMode.Hz
        data.value = hz
        data.time = time

        return self.transfer(header, data)

    def sendBuzzerHzReserve(self, hz, time):

        if ((not isinstance(hz, int)) or
                (not isinstance(time, int))):
            return None

        header = Header()

        header.dataType = DataType.Buzzer
        header.length = Buzzer.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Controller

        data = Buzzer()

        data.mode = BuzzerMode.HzReserve
        data.value = hz
        data.time = time

        return self.transfer(header, data)

    # Buzzer End

    # Vibrator Start

    def sendVibrator(self, on, off, total):

        if ((not isinstance(on, int)) or
                (not isinstance(off, int)) or
                (not isinstance(total, int))):
            return None

        header = Header()

        header.dataType = DataType.Vibrator
        header.length = Vibrator.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Controller

        data = Vibrator()

        data.mode = VibratorMode.Instantally
        data.on = on
        data.off = off
        data.total = total

        return self.transfer(header, data)

    def sendVibratorReserve(self, on, off, total):

        if ((not isinstance(on, int)) or
                (not isinstance(off, int)) or
                (not isinstance(total, int))):
            return None

        header = Header()

        header.dataType = DataType.Vibrator
        header.length = Vibrator.getSize()
        header.from_ = DeviceType.Base
        header.to_ = DeviceType.Controller

        data = Vibrator()

        data.mode = VibratorMode.Continually
        data.on = on
        data.off = off
        data.total = total

        return self.transfer(header, data)

# Vibrator End


# Update Start


# Update End

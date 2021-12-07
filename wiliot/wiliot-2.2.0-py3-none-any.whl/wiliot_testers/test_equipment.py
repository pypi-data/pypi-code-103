'''
Created on Nov 30, 2021

@author: davidd
'''
from time import time, sleep
from serial import Serial 
from sys import path
from os.path import join, dirname


class Attenuator(object):
    def __init__(self, ATTN_type, comport='AUTO'):

        if 'MCDI' in ATTN_type:
            self._active_TE = Attenuator.MCDI()
        elif 'API' in ATTN_type or 'Weinschel' in ATTN_type:
            self._active_TE = Attenuator.API(comport)
        else:
            pass

    def GetActiveTE(self):
        return self._active_TE
    
    def close_port(self):
        if self._active_TE.is_open():
            self._active_TE.close_port()   

    class MCDI(object):

        def __init__(self):

            import clr  # pythonnet, manually installed with a downloaded wheel and pip
            import ctypes  # module to open dll files
            path.append(join(dirname(__file__), "..\\..\\src\\", 'utils'))
            clr.AddReference('mcl_RUDAT_NET45')
            from mcl_RUDAT_NET45 import USB_RUDAT
            self.Device = USB_RUDAT()
            self.Device.Connect()
            info = self.DeviceInfo()
            print('Found Attenuator: Model {}, {} ,{} , '.format(info[0], info[1], info[2]))

        def DeviceInfo(self):
            cmd = ":MN?"
            model_name = self.Device.Send_SCPI(cmd, "")
            cmd = ":SN?"
            serial = self.Device.Send_SCPI(cmd, "")
            cmd = ":FIRMWARE?"
            fw = self.Device.Send_SCPI(cmd, "")
            return [model_name[1], serial[1], fw[1]]

        def Setattn(self, attn):
            cmd = ":SETATT:" + str(attn)
            [status, Resp] = self.Device.Send_SCPI(cmd, "")
            if status == 0:
                print('Command failed or invalid attenuation set')
            elif status == 1:
                print('Command completed successfully')
            elif status == 2:
                print(
                    'Requested attenuation was higher than the allowed range, the attenuation was set to the device�s maximum allowed value')
            print([status, Resp])

        def Getattn(self):
            cmd = ":ATT?"
            [status, Resp] = self.Device.Send_SCPI(cmd, "")
            print([status, Resp])
            if status == 0:
                print('Command failed or invalid attenuation set')
            elif status == 1:
                print('Command completed successfully')
            return Resp

    class API(object):

        def __init__(self, comport="AUTO"):

            self.baudrate = 9600
            if comport == "AUTO":
                ports_list = Serial().serial_ports()
                for port in ports_list:
                    self.comport = port
                    self.s = Serial(self.comport, self.baudrate, timeout=0, write_timeout=0)
                    sleep(1)
                    # Turn the console off
                    self.s.write("CONSOLE DISABLE\r\n".encode())
                    # Flush the buffers
                    self.s.flush()
                    self.s.flushInput()
                    self.s.flushOutput()

                    resp = self.Query("*IDN?\r\n")
                    if ("Aeroflex" in resp):
                        print('Found ' + resp.strip('\r\n') + ' on port: ' + port)
                        break
                    elif '8311' in resp:
                        print('Found ' + resp.strip('\r\n') + ' on port: ' + port)
                    else:
                        pass
            else:
                self.s = Serial(comport, self.baudrate, timeout=0, write_timeout=0)
                sleep(1)
                self.s.write("CONSOLE DISABLE\r\n".encode())
                # Flush the buffers
                self.s.flush()
                self.s.flushInput()
                self.s.flushOutput()
                resp = self.Query("*IDN?\r\n")
                if ("Aeroflex" in resp):
                    print('Found ' + resp.strip('\r\n') + ' on port: ' + comport)
                elif '8311' in resp:
                    print('Found ' + resp.strip('\r\n') + ' on port: ' + comport)
                else:
                    print('Aeroflex Attenuator not found on selected port, check connection')

        def Write(self, cmd, wait=False):
            """Send the input cmd string via COM Socket"""
            if self.s.isOpen():
                pass
            else:
                self.s.open()
            self.s.flushInput()
            sleep(1)
            try:
                self.s.write(str.encode(cmd))
                sleep(0.5);  # Commands may be lost when writing too fast

            except:
                pass
            self.s.close()

        def Query(self, cmd):
            """Send the input cmd string via COM Socket and return the reply string"""
            if self.s.isOpen():
                pass
            else:
                self.s.open()
                sleep(1)
            self.s.flushInput()
            sleep(1)
            try:
                self.s.write(str.encode(cmd))
                sleep(0.5)
                data = self.s.readlines();
                value = data[0].decode("utf-8")
                # Cut the last character as the device returns a null terminated string
                value = value[:-1]
            except:
                value = ''
            #             print(datetime.datetime.now().time(), "Sent: ", cmd)
            #             print(datetime.datetime.now().time(), "Recv: ", value)
            self.s.close()
            return value;
        
        def close_port(self):
            if self.s is not None and self.s.isOpen():
                self.s.close()
                
        def is_open(self):
            if self.s is not None:
                return self.s.isOpen()
            return True

        def Setattn(self, attn):
            cmd = "ATTN " + str(attn) + '\r\n'
            self.Write(cmd)
            value = self.Getattn()
            return value

        def Getattn(self):
            cmd = "ATTN?\r\n"
            value = self.Query(cmd)
            return value

        def set_active_channel(self, channel):
            cmd = "CHAN " + str(channel) + "\r\n"
            self.Write(cmd)
            value = self.get_active_channel()
            return value

        def get_active_channel(self):
            cmd = "CHAN?\r\n"
            value = self.Query(cmd)
            return value
        
class Tescom:
    """
    Control TESCOM testing chambers
    """
    open_cmd = b'OPEN\r'
    close_cmd = b'CLOSE\r'
    com_port_obj = None
    models_list = ['TC-5064C', 'TA-7011AP', 'TC-5063A', 'TC-5970CP']

    def __init__(self, port=None):
        self.port = port
        try:
            if port is not None:
                self.connect(port)
                
        except Exception as e:
            print(e)
            print("Tescom - Connection failed")

    def connect(self, port):
        """
        :param port: com port to connect
        :return: com port obj
        """
        try:
            com_port_obj = self.com_port_obj = Serial(port=port, baudrate=9600, timeout=1)
            if com_port_obj is not None:
                self.door_cmd = None
                self.com_port_obj.write(b'MODEL?\r')
                sleep(0.5)
                model = str(self.com_port_obj.read(14))
                parts = [p for p in model.split("'")]
                parts = [p for p in parts[1].split(" ")]
                self.model = parts[0]
                if len(self.model) > 0:
                    print("RF chamber connected to port " + str(port))
                    print("Tescom - Chamber model:", self.model)
                else:
                    print("Tescom - Error! No chamber found")
                    return
                if self.model in self.models_list:
                    self.door_cmd = b'DOOR?\r'
                else:
                    self.door_cmd = b'LID?\r'
            else:
                raise Exception
        except Exception as e:
            # print(e)
            print(("Tescom - Could not connect to port " + port))
            return None

    def close_port(self):
        """
        closes com port
        """
        try:
            self.com_port_obj.close()
            print("RF chamber disconnected from port: " + str(self.port))
        except Exception as e:
            print("Could not disconnect")

    def open_chamber(self):
        """
        opens chamber
        :return: "OK" if command was successful
        """
        if self.is_door_open():
            print("Chamber is open")
            return 'OK'
        try:
            print(f"Chamber {self.port} is opening")
            self.com_port_obj.reset_input_buffer()
            self.com_port_obj.reset_output_buffer()
            self.com_port_obj.write(self.open_cmd)
            res = ''
            wait_counter = 0
            while 'OK' not in res:
                if wait_counter >= 15:
                    raise Exception(f"Error in opening chamber {self.port}")
                res = self.com_port_obj.read(14).decode('utf-8').upper().rstrip('\r')
                if len(str(res)) > 0:
                    print(f'Chamber {self.port} status: ' + str(res))
                wait_counter += 1
                sleep(0.5)
            if not self.is_door_open():
                raise Exception(f"{self.port} Door status doesn't match command sent!")
            print(f"Chamber {self.port} is open")
            return 'OK'
        except Exception as e:
            print(e)
            return "FAIL"

    def close_chamber(self):
        """
        closes chamber
        :return: "OK" if command was successful
        """
        if self.is_door_closed():
            print("Chamber closed")
            return 'OK'
        try:
            print(f"CHAMBER {self.port} IS CLOSING, CLEAR HANDS!!!")
            sleep(2)
            self.com_port_obj.write(self.close_cmd)
            res = ''
            wait_counter = 0
            while 'READY' not in res:
                if wait_counter >= 20:
                    raise Exception(f"Error in closing chamber {self.port}")
                res = self.com_port_obj.read(14).decode('utf-8').upper().rstrip('\r')
                if 'ERR' in res or 'READY' in res or 'OK' in res:
                    print(f'Chamber {self.port} status: ' + str(res))
                if 'ERR' in res:
                    return "FAIL"
                wait_counter += 1
                sleep(0.5)
            if not self.is_door_closed():
                raise Exception(f"{self.port} Door status doesn't match command sent!")
            print(f"Chamber {self.port} closed")
            return 'OK'
        except Exception as e:
            print(f"Error in closing chamber {self.port}")
            print(e)
            return "FAIL"
        
    def is_connected(self):
        if self.com_port_obj is None:
            return False
        return self.com_port_obj.isOpen()
    
    def get_state(self):
        self.com_port_obj.reset_input_buffer()
        sleep(0.5)
        self.com_port_obj.write(self.door_cmd)
        sleep(0.5)
        state = self.com_port_obj.read(14).decode('utf-8').upper().rstrip('\r')
        return state
    
    def is_door_open(self):
        state = self.get_state()
        if 'OPEN' in state:
            return True 
        return False
    
    def is_door_closed(self):
        state = self.get_state()
        if 'CLOSE' in state:
            return True
        return False

class BarcodeScanner(object):
    prefix = '~0000@'
    suffix = ';'
    com = ''
    serial = None
    
    
    def __init__(self, com=None, baud=115200, config=True, log_type = 'NO_LOG'):
        self.log_type = log_type
        if com!=None:
            self.openPort(com, baud=baud, config=config)
        else:
            self.serial = ser = Serial()
            
    def read(self):
        # print("analog_trigger_setting");
        self.serial.write(b"\x1b\x31")
        sleep(0.1)
        # t = ser.read(ser.in_waiting)
        t = self.serial.read_all()
        # print(t)
        return t
    
    def readAndFlush(self):
        t = self.read()
        self.serial.flushInput()
        self.serial.flushOutput()
        return t
    
    def readExternalId(self, scanDur=0.5, sleepDur=0.005):
        barcodeRead = ''
        startTime = time()
        while((time()-startTime)<scanDur):
            t = self.readAndFlush()
            barcodeRead = str(t)
            if len(barcodeRead.split(')'))<3:
                barcodeRead = ''
                continue
            try:
                fullData = barcodeRead.split('\\x')[-1]
                gtin = ')'.join(fullData.split(')')[:2]) + ')' 
                tagData = fullData.split(')')[2]
                curId = tagData.split('T')[1].strip("' ")
                reelId = tagData.split('T')[0].strip("' ")
                return curId, reelId, gtin
            except:
                continue
            sleep(sleepDur)
        
        return None, None, None
            
    
    def automaticRead(self):
        # print("Automatic reading settings");
        self.serial.write(b"\x1b\x32")
        sleep(0.1)
        t = self.serial.read_all()
        # print(t)
        return t
    
    def triggerStopSettings(self):
        # print("Trigger_stop_settings");
        # sleep(0.1)
        # t = ser.read(ser.in_waiting)
        sleep(0.1)
        t = self.serial.read_all()
        self.serial.flushInput()
        self.serial.flushOutput()
        sleep(0.1)
        # print(t)
        acks = str(t).split(';')[:-1]
        isSuccess = all([True if ack.endswith('\\x06') else False for ack in acks])
        return isSuccess
    
    def openPort(self, com, baud=115200, config=True):
        if self.serial!=None:
            self.serial.closePort()
        self.serial = ser = Serial(com, baud, timeout=0.5)
        if ser != None and self.log_type!='NO_LOG':
            print(f'Barcode scanner ({com}) connected.')
        elif ser == None:
            print(f'Barcode scanner - Problem connecting {com}')
        self.com = com
        ser.timerout=1 #read time out
        ser.writeTimeout = 0.5 #write time out.
        if config:
            self.configure()
            
    def close_port(self):
        if self.serial.isOpen():
            self.serial.close()
            
    def isOpen(self):
        return self.serial.isOpen()
            
    '''
    illScn - illumination:    0-off, 1-normal, 2-always on
    amlEna - aiming:          0-off, 1-normal, 2-always on
    pwbEna - power on beep    0-off, 1-on
    grbEna - good read beep   0-off, 1-on
    atsEna - auto sleep       0-disable, 1-enable
    atsDur - sleep duration   1-36000 [sec]
    scnMod - scan mode        0-level mode, 2-sense mode, 3-continuous mode, 7-batch mode
    '''
    def configure(self, illScn='2', amlEna='0', grbEna='0', grbVll='2', atsEna='0', atsDur='36000', scnMod='0', pwbEna='1'):
        sleep(0.1)
        params = {'ILLSCN':illScn, 'AMLENA':amlEna, 'GRBENA':grbEna, 'ATSENA':atsEna, 'GRBVLL':grbVll, 'ATSDUR':atsDur, 'SCNMOD':scnMod, 'PWBENA':pwbEna}
        params = [key+value for key,value in params.items()]
        configs = self.prefix + ';'.join(params) + self.suffix
        self.serial.write(str.encode(configs))
        # self.serial.write(b'ILLSCN2;AMLENA2;GRBENA0;ATSENA0,DUR0;SCNMOD0;')
        sleep(0.1)
        isSuccess = self.triggerStopSettings()
        if isSuccess and self.log_type!='NO_LOG':
            print(f'Barcode scanner ({self.com}) configured successfully.')
        elif not isSuccess:
            print(f'Barcode scanner ({self.com}) configuration failed.')
            
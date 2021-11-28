from os.path import isfile
from tkinter import Tk, INSERT, END
import serial.tools.list_ports
import pygubu
import json
import multiprocessing
from wiliot.gateway_api.gateway import *

# default config values:
EP_DEFAULT = 20  # Energizing pattern
EPs_DEFAULT = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28,
               50, 51, 52)  # All Energizing pattern
TP_O_DEFAULT = 5  # timing profile on
TP_P_DEFAULT = 15  # timing profile period
PI_DEFAULT = 0  # pace interval
RC_DEFAULT = 37
RCs_DEFAULT = (37, 38, 39)
VIEW_TYPES = ('current samples', 'first samples')
DATA_TYPES = ('raw', 'processed')
CONFIG_SUM = "EP:{EP}, TP_ON:{TP_ON}, TP_P:{TP_P}, RC:{RC}, PI:{PI}, F:{F}"
baud_rates = ["921600"]


class GatewayUI(object):
    gwCommandsPath = '.gwCommands.json'
    gwUserCommandsPath = '.gwUserCommands.json'
    gwAllCommands = []
    gwCommands = []
    gwUserCommands = []
    filter_state = False
    portActive = False

    def __init__(self, main_app_folder='', array_out=None, tk_frame=None):
        print('GW UI mode is activated')
        self.busy_processing = False
        self.close_requested = False
        # 1: Create a builder
        self.builder = builder = pygubu.Builder()

        # 2: Load an ui file
        uifile = os.path.join(os.path.join(os.path.abspath(os.path.dirname(__file__))), 'utils', 'gw_test_debugger.ui')
        builder.add_from_file(uifile)

        if tk_frame:
            self.ttk = tk_frame  # tkinter.Frame , pack(fill="both", expand=True)
        else:
            self.ttk = Tk()
        self.ttk.title("Wiliot Gateway Test Application")

        # 3: Create the widget using a self.ttk as parent
        self.mainwindow = builder.get_object('mainwindow', self.ttk)

        self.ttk = self.ttk

        # set the scroll bar of the main textbox
        textbox = self.builder.get_object('recv_box')
        scrollbar = self.builder.get_object('scrollbar')
        textbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=textbox.yview)
        self.builder.get_object('scrollbar').set(self.builder.get_object('recv_box').index(INSERT),
                                                 self.builder.get_object('recv_box').index(END))
        self.builder.get_object('recv_box').grid()

        self.builder.connect_callbacks(self)

        # upload pre-defined commands
        self.gwCommandsPath = os.path.join(main_app_folder, self.gwCommandsPath)
        if isfile(self.gwCommandsPath):
            with open(self.gwCommandsPath, 'r') as f:
                self.gwCommands = json.load(f)

        self.gwUserCommandsPath = os.path.join(main_app_folder, self.gwUserCommandsPath)
        if isfile(self.gwUserCommandsPath):
            with open(self.gwUserCommandsPath, 'r') as f:
                self.gwUserCommands = json.load(f)

        self.gwAllCommands = self.gwCommands + self.gwUserCommands

        # define array to export data for other applications
        if array_out is None:
            self.data_out = multiprocessing.Queue()
        else:
            self.data_out = array_out

        self.ttk.lift()
        self.ttk.attributes("-topmost", True)
        self.ttk.attributes("-topmost", False)

        self.ObjGW = WiliotGateway()
        self.config_param = {}

        # update ui
        self.ui_update('init')
        self.ui_update('available_ports')

        self.ttk.protocol("WM_DELETE_WINDOW", self.close_window)

        self.ttk.after_idle(self.periodic_call)
        self.ttk.mainloop()

    def close_window(self):
        self.close_requested = True
        print("User requested close at:", time.time(), "Was busy processing:", self.busy_processing)

    def periodic_call(self):
        if not self.close_requested:
            self.busy_processing = True
            self.busy_processing = False
            self.ttk.after(500, self.periodic_call)

        else:
            print("Destroying GUI at:", time.time())
            try:
                self.ObjGW.exit_gw_api()
                self.ttk.destroy()
            except Exception as e:
                print(e)
                exit(0)

    def on_connect(self):
        if not self.portActive:
            try:
                port = self.builder.get_object('port_box').get().rsplit(' ', 1)[0]
                baud = self.builder.get_object('baud_rate_box').get().rsplit(' ', 1)[0]
                if port == '' or baud == '':
                    return

                if self.ObjGW.open_port(port, baud):  # open and check if succeed
                    self.builder.get_object('recv_box').insert(END, "> Port successfully opened\n")
                    self.builder.get_object('recv_box').see(END)
                    self.portActive = True
                    self.builder.get_object('connect_button').configure(text='Disconnect')
                    # print version:
                    self.builder.get_object('recv_box').insert(END, self.ObjGW.hw_version + '=' +
                                                               self.ObjGW.sw_version + "\n")
                    self.builder.get_object('recv_box').see(END)
                    # config gw to receive packets (and not only manage bridges):
                    self.ObjGW.write('!enable_brg_mgmt 0')
                    # update UI:
                    self.ui_update('connect')
                    # start listening:
                    self.ObjGW.run_packets_listener(do_process=True, tag_packets_only=False)
                    data_handler_listener = threading.Thread(target=self.recv_data_handler, args=())
                    data_handler_listener.start()

                else:
                    self.builder.get_object('recv_box').insert(END, "> Can't open Port - "
                                                                    "check connection parameters and try again\n")
                    self.builder.get_object('recv_box').see(END)
                    self.portActive = False
            except Exception as e:
                self.builder.get_object('recv_box').insert(END, "> Encounter a problem during connection\n")
                self.builder.get_object('recv_box').see(END)
                print(e)

        else:  # Port is open, close it...
            try:
                self.builder.get_object('recv_box').insert(END, "> Disconnecting from Port\n")
                self.builder.get_object('recv_box').see(END)
                self.ObjGW.exit_gw_api()
                self.builder.get_object('connect_button').configure(text="Connect")
                self.portActive = False
                self.ui_update('connect')
            except Exception as e:
                print(e)

    def on_search_ports(self):
        self.ObjGW.available_ports = [s.device for s in serial.tools.list_ports.comports()]
        if len(self.ObjGW.available_ports) == 0:
            self.ObjGW.available_ports = [s.name for s in serial.tools.list_ports.comports()]
        # update ui:
        self.ui_update('available_ports')

    def recv_data_handler(self):
        print("DataHandlerProcess Start")
        consecutive_exception_counter = 0
        while True:
            time.sleep(0)
            try:
                if self.close_requested or not self.portActive:
                    print("DataHandlerProcess Stop")
                    return

                # check if there is data to read
                if self.ObjGW.is_data_available():
                    # check which data type to read:
                    action_type = ''
                    if self.builder.get_object('view_type').get() == 'current samples':
                        action_type = ActionType.CURRENT_SAMPLES
                    elif self.builder.get_object('view_type').get() == 'first samples':
                        action_type = ActionType.FIRST_SAMPLES
                    # get data
                    data_type = DataType.RAW
                    if self.builder.get_object('data_type').get() == 'raw':
                        data_type = DataType.RAW
                    elif self.builder.get_object('data_type').get() == 'processed':
                        data_type = DataType.PROCESSED

                    data_in = self.ObjGW.get_data(action_type=action_type, num_of_packets=1, data_type=data_type)
                    if not data_in:
                        continue
                    if isinstance(data_in, list):
                        print("we extracted more than one element at a time.\nonly the first packet is printed")
                        data_in = data_in[0]
                    # print
                    data_str = []
                    for key, value in data_in.items():
                        data_str.append("{} : {}".format(key, value))
                    all_data_str = ', '.join(data_str)
                    self.builder.get_object('recv_box').insert(END, all_data_str)
                    self.builder.get_object('recv_box').insert(END, '\n')
                    self.builder.get_object('recv_box').see(END)

                    consecutive_exception_counter = 0
            except Exception as e:
                print(e)
                print("DataHandlerProcess Exception")
                consecutive_exception_counter = consecutive_exception_counter + 1
                if consecutive_exception_counter > 10:
                    print("Abort DataHandlerProcess")
                    return

    def on_update_gw_version(self):
        self.builder.get_object('recv_box').insert(END, "> Updating GW version, please wait...\n")
        self.builder.get_object('recv_box').see(END)
        time.sleep(1)
        version_path_entry = self.builder.get_object('version_path').get()
        if version_path_entry:
            version_path_entry = version_path_entry.strip("\u202a")  # strip left-to-right unicode if exists
            if not os.path.isfile(version_path_entry):
                self.builder.get_object('recv_box').insert(END, "> cannot find the entered gw version file:\n" +
                                                           version_path_entry + "\n")
                self.builder.get_object('recv_box').see(END)
                return

        self.ObjGW.update_version(versions_path=version_path_entry)
        # listen again:
        self.ObjGW.run_packets_listener(do_process=True, tag_packets_only=False)
        self.builder.get_object('recv_box').insert(END, "> Update GW version was completed \n")
        self.builder.get_object('recv_box').see(END)

    def on_reset(self):
        self.ObjGW.reset_gw()

    def on_write(self):
        cmd_value = self.builder.get_object('write_box').get()
        self.ObjGW.write(cmd_value)

        if cmd_value.strip() not in list(self.builder.get_object('write_box')['values']):
            temp = list(self.builder.get_object('write_box')['values'])

            # keep only latest instances
            if temp.__len__() == 20:
                temp.pop(0)
            if len(self.gwUserCommands) >= 20:
                self.gwUserCommands.pop(0)
            self.gwUserCommands.append(cmd_value)
            temp.append(cmd_value)
            self.builder.get_object('write_box')['values'] = tuple(temp)
            with open(self.gwUserCommandsPath, 'w+') as f:
                json.dump(self.gwUserCommands, f)

        self.ui_update(state='config')

    def on_config(self):
        filter_val = self.filter_state
        pacer_val = int(self.builder.get_object('pace_inter').get())
        energ_ptrn_val = int(self.builder.get_object('energizing_pattern').get())
        time_profile_val = [int(self.builder.get_object('timing_profile_on').get()),
                            int(self.builder.get_object('timing_profile_period').get())]
        received_channel_val = int(self.builder.get_object('received_channel').get())
        self.builder.get_object('recv_box').insert(END, "> Setting GW configuration...\n")
        self.builder.get_object('recv_box').see(END)
        config_param_set = self.ObjGW.config_gw(filter_val=filter_val, pacer_val=pacer_val,
                                                energy_pattern_val=energ_ptrn_val, time_profile_val=time_profile_val,
                                                received_channel=received_channel_val,
                                                modulation_val=True)
        # update config parameters:
        for key, value in config_param_set.__dict__.items():
            if key == 'filter' or key == 'modulation':
                self.config_param[key] = str(value)[0]
            else:
                self.config_param[key] = str(value)

        self.ui_update(state='config')
        self.builder.get_object('recv_box').insert(END, "> Configuration is set\n")
        self.builder.get_object('recv_box').see(END)

    def on_set_filter(self):
        self.filter_state = not self.filter_state
        self.builder.get_object('recv_box').insert(END, "> Setting filter...\n")
        self.builder.get_object('recv_box').see(END)
        config_param_set = self.ObjGW.config_gw(filter_val=self.filter_state)
        self.config_param["filter"] = str(config_param_set.filter)[0]

        self.ui_update(state='config')

    def on_clear(self):
        self.builder.get_object('recv_box').delete('1.0', END)
        self.builder.get_object('recv_box').see(END)

    def ui_update(self, state):
        # updating UI according to the new state
        if state == 'init':
            self.builder.get_object('write_box')['values'] = tuple(self.gwAllCommands)
            # default config values:
            self.builder.get_object('energizing_pattern')['values'] = tuple(EPs_DEFAULT)
            self.builder.get_object('energizing_pattern').set(EP_DEFAULT)
            self.builder.get_object('timing_profile_on').set(TP_O_DEFAULT)
            self.builder.get_object('timing_profile_period').set(TP_P_DEFAULT)
            self.builder.get_object('pace_inter').set(PI_DEFAULT)
            self.builder.get_object('received_channel')['values'] = tuple(RCs_DEFAULT)
            self.builder.get_object('received_channel').set(RC_DEFAULT)

            self.config_param = {"energy_pattern": str(EP_DEFAULT),
                                 "received_channel": str(RC_DEFAULT),
                                 "time_profile_on": str(TP_O_DEFAULT),
                                 "time_profile_period": str(TP_P_DEFAULT),
                                 "pacer_val": str(PI_DEFAULT),
                                 "filter": "N"}

            self.builder.get_object('config_sum').insert(END, CONFIG_SUM.format(
                RC="", EP="", TP_ON="", TP_P="", PI="", F=""))
            self.builder.get_object('config_sum').see(END)

            self.builder.get_object('view_type')['values'] = tuple(VIEW_TYPES)
            self.builder.get_object('view_type').set('first samples')
            self.builder.get_object('data_type')['values'] = tuple(DATA_TYPES)
            self.builder.get_object('data_type').set('raw')

            ver_num, _ = self.ObjGW.get_latest_version_number()
            if ver_num is not None:
                self.builder.get_object('version_num').insert(END, ver_num)

        elif state == 'available_ports':
            if self.ObjGW.available_ports:
                self.builder.get_object('recv_box').insert(END, f'> Finished searching for ports, available ports: '
                                                                f'{", ".join(self.ObjGW.available_ports)}\n')
                self.builder.get_object('recv_box').see(END)
                self.builder.get_object('port_box')['values'] = tuple(self.ObjGW.available_ports)
            else:
                self.builder.get_object('recv_box').insert(END, 'no serial ports were found. '
                                                                'please check your connections and refresh\n')
                self.builder.get_object('recv_box').see(END)
            self.builder.get_object('baud_rate_box')['values'] = tuple(baud_rates)
            self.builder.get_object('port_box')['state'] = 'enabled'
            self.builder.get_object('baud_rate_box')['state'] = 'enabled'
            self.builder.get_object('baud_rate_box').set(baud_rates[0])

        elif state == 'connect':
            enable_disable_str = 'disabled'
            if self.portActive:
                enable_disable_str = 'enabled'

            self.builder.get_object('config_button')['state'] = enable_disable_str
            self.builder.get_object('energizing_pattern')['state'] = enable_disable_str
            self.builder.get_object('timing_profile_on')['state'] = enable_disable_str
            self.builder.get_object('timing_profile_period')['state'] = enable_disable_str
            self.builder.get_object('pace_inter')['state'] = enable_disable_str
            self.builder.get_object('set_filter')['state'] = enable_disable_str
            self.builder.get_object('write_button')['state'] = enable_disable_str
            self.builder.get_object('write_box')['state'] = enable_disable_str
            self.builder.get_object('reset_button')['state'] = enable_disable_str
            self.builder.get_object('view_type')['state'] = enable_disable_str
            self.builder.get_object('received_channel')['state'] = enable_disable_str
            self.builder.get_object('data_type')['state'] = enable_disable_str
            self.builder.get_object('update_button')['state'] = enable_disable_str
            self.builder.get_object('version_path')['state'] = enable_disable_str

        elif state == 'config':
            self.builder.get_object('config_sum').delete(1.0, END)
            self.builder.get_object('config_sum').insert(END,
                                                         CONFIG_SUM.format(RC=self.config_param["received_channel"],
                                                                           EP=self.config_param["energy_pattern"],
                                                                           TP_ON=self.config_param["time_profile_on"],
                                                                           TP_P=self.config_param[
                                                                               "time_profile_period"],
                                                                           PI=self.config_param["pacer_val"],
                                                                           F=self.config_param["filter"]))
            self.builder.get_object('config_sum').see(END)


if __name__ == '__main__':
    # Run the UI
    app_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    GWApp = GatewayUI(main_app_folder=app_folder)

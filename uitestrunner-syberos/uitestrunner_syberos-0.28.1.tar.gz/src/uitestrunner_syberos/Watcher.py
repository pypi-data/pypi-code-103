# Copyright (C) <2021>  YUANXIN INFORMATION TECHNOLOGY GROUP CO.LTD and Jinzhe Wang
# This file is part of uitestrunner_syberos
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import time
import psutil


class WatchWorker:
    
    watch_data = {}
    __watcher_list = []
    
    def __init__(self, d, conn, main_pid):
        self.device = d
        self.conn = conn
        self.main_pid = main_pid

    def __get_list(self):
        if self.conn.poll():
            data = dict(self.conn.recv())
            if 'watcher_list' in data.keys():
                self.__watcher_list = data['watcher_list']

    def run(self):
        main_process = psutil.Process(self.main_pid)
        while True:
            time.sleep(1)
            main_process.suspend()
            try:
                self.__get_list()
                self.device.refresh_layout()
                for watcher in self.__watcher_list:
                    flag = 0
                    for xpath in watcher['xpath_list']:
                        if self.device.find_item_by_xpath(xpath['sop_id'], xpath['xpath']).exist():
                            flag += 1
                    if flag == len(watcher['xpath_list']):
                        for xpath in watcher['xpath_list']:
                            if xpath['index'] == watcher['index']:
                                if watcher['active'] == 'click':
                                    self.device.find_item_by_xpath(xpath['sop_id'], xpath['xpath']).click()
                                elif watcher['active'] == 'back':
                                    self.device.back()
                                elif watcher['active'] == 'home':
                                    self.device.home()
                                elif watcher['active'] == 'launch':
                                    self.device.launch(watcher['active_sop_id'], watcher['active_ui_app_id'])
            except Exception as e:
                print(e)
                main_process.resume()
                continue
            main_process.resume()


class Watcher:

    __watcher_data = {}

    def __init__(self, data: dict, d):
        self.__watcher_data = data
        self.device = d

    def when(self, sop_id, xpath_key):
        if 'xpath_list' not in self.__watcher_data.keys():
            self.__watcher_data['xpath_list'] = []
        index = len(self.__watcher_data['xpath_list'])
        self.__watcher_data['xpath_list'].append({'index': index,
                                                  'xpath': self.device.get_xpath(sop_id, xpath_key),
                                                  'sop_id': sop_id})
        self.__watcher_data['index'] = index
        return _WatchContext(self.__watcher_data, self.device)


class _WatchContext:
    
    __watcher_data = {}
    
    def __init__(self, data: dict, d):
        self.__watcher_data = data
        self.device = d

    def when(self, sop_id, xpath_key):
        if 'xpath_list' not in self.__watcher_data.keys():
            self.__watcher_data['xpath_list'] = []
        index = len(self.__watcher_data['xpath_list'])
        self.__watcher_data['xpath_list'].append({'index': index,
                                                  'xpath': self.device.get_xpath(sop_id, xpath_key),
                                                  'sop_id': sop_id})
        self.__watcher_data['index'] = index
        return self

    def click(self):
        self.__watcher_data['active'] = 'click'
        self.__push()

    def pause(self, key: str):
        self.__watcher_data['active'] = key
        self.__push()

    def launch(self, sop_id: str, ui_app_id: str):
        self.__watcher_data['active'] = 'launch'
        self.__watcher_data['active_sop_id'] = sop_id
        self.__watcher_data['active_ui_app_id'] = ui_app_id
        self.__push()

    def __push(self):
        self.device.watcher_list.append(self.__watcher_data)
        self.device.push_watcher_data()



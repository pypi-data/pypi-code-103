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
import urllib.parse
from time import sleep
from lxml import etree
import time
from urllib3 import encode_multipart_formdata


class Events:
    device = None
    app = None
    item = None

    def __init__(self, d=None, a=None, i=None):
        self.device = d
        self.app = a
        self.item = i

    @staticmethod
    def __reply_status_check(reply):
        if reply.status == 200:
            return True
        return False

    def get_blank_timeout(self):
        return int(self.device.con.get(path="getBlankTimeout").read())

    def set_blank_timeout(self, timeout):
        return self.__reply_status_check(self.device.con.get(path="setBlankTimeout", args="sec=" + str(timeout)))

    def get_dim_timeout(self):
        return int(self.device.con.get(path="getDimTimeout").read())

    def set_dim_timeout(self, timeout):
        return self.__reply_status_check(self.device.con.get(path="setDimTimeout", args="sec=" + str(timeout)))

    def set_display_on(self):
        return self.__reply_status_check(self.device.con.get(path="setDisplayState", args="state=0"))

    def set_display_off(self):
        return self.__reply_status_check(self.device.con.get(path="setDisplayState", args="state=1"))

    def set_display_dim(self):
        return self.__reply_status_check(self.device.con.get(path="setDisplayState", args="state=0")) and \
               self.__reply_status_check(self.device.con.get(path="setDisplayState", args="state=2"))

    def get_display_state(self):
        reply = int(str(self.device.con.get(path="getDisplayState").read(), 'utf-8'))
        if reply == 0:
            return "on"
        elif reply == 1:
            return "off"
        elif reply == 2:
            return "dim"
        return "unknown"

    def lock(self):
        return self.__reply_status_check(self.device.con.get(path="setLockState", args="state=0"))

    def unlock(self):
        dis_state = int(str(self.device.con.get(path="getDisplayState").read(), 'utf-8'))
        if dis_state == 0 or dis_state == 2:
            return self.__reply_status_check(self.device.con.get(path="setLockState", args="state=1"))
        elif dis_state == 1:
            if self.set_display_on():
                sleep(1)
                return self.__reply_status_check(self.device.con.get(path="setLockState", args="state=1"))
        return False

    def get_lock_state(self):
        reply = int(str(self.device.con.get(path="getLockState").read(), 'utf-8'))
        if reply == 0:
            return "locked"
        elif reply == 1:
            return "unlocked"
        return "unknown"

    def submit_string(self, text):
        return self.__reply_status_check(self.device.con.get(path="sendCommitString", args="str=" + urllib.parse.quote(text)))

    def click(self, x, y):
        return self.__reply_status_check(self.device.con.get(path="sendTouchEvent", args="points=" + str(x) + "|" + str(y)))

    def multi_click(self, points):
        args = ""
        for point in points:
            args += str(point[0]) + "|" + str(point[1])
            if points.index(point) != len(points) - 1:
                args += ","
        return self.__reply_status_check(self.device.con.get(path="sendTouchEvent", args="points=" + args))

    def swipe(self, x1, y1, x2, y2):
        return self.__reply_status_check(self.device.con.get(path="sendSlideEvent", args="sliders=" + str(x1) + "|" + str(y1) + "->" + str(x2) + "|" + str(y2)))

    def multi_swipe(self, points1, points2):
        args = ""
        for point1 in points1:
            args += str(point1[0]) + "|" + str(point1[1]) + "->" + str(points2[points1.index(point1)][0]) + "|" + str(points2[points1.index(point1)][1])
            if points1.index(point1) != len(points1) - 1:
                args += ","
        return self.__reply_status_check(self.device.con.get(path="sendSlideEvent", args="sliders=" + args))

    def back(self):
        return self.__reply_status_check(self.device.con.get(path="sendBackKeyEvent"))

    def home(self, timeout=None):
        if not timeout:
            timeout = self.device.default_timeout
        if self.__reply_status_check(self.device.con.get(path="sendHomeKeyEvent")):
            for m_iter in range(0, timeout):
                if m_iter > 0:
                    sleep(1)
                self.device.refresh_layout()
                selector = etree.XML(self.device.xmlStr.encode('utf-8'))
                if selector.get("sopId") == "home-screen(FAKE_VALUE)":
                    return True
                else:
                    self.device.con.get(path="sendHomeKeyEvent")
        return False

    def menu(self):
        return self.__reply_status_check(self.device.con.get(path="sendMenuKeyEvent"))

    def volume_up(self, delay=0):
        return self.__reply_status_check(self.device.con.get(path="sendVolumeUpKeyEvent", args="delay=" + str(delay)))

    def volume_down(self, delay=0):
        return self.__reply_status_check(self.device.con.get(path="sendVolumeDownKeyEvent", args="delay=" + str(delay)))

    def set_rotation_allowed(self, allowed=True):
        if allowed:
            return self.__reply_status_check(self.device.con.get(path="setRotationAllowed", args="allowed=1"))
        else:
            return self.__reply_status_check(self.device.con.get(path="setRotationAllowed", args="allowed=0"))

    def get_rotation_allowed(self):
        reply = int(str(self.device.con.get(path="getRotationAllowed").read(), 'utf-8'))
        if reply == 1:
            return True
        return False

    def set_rotation(self, rotation: int):
        return self.__reply_status_check(self.device.con.get(path="setCurrentOrientation", args="rotation=" + str(rotation)))

    def get_rotation(self):
        return int(str(self.device.con.get(path="getCurrentOrientation").read(), 'utf-8'))

    def upload_file(self, file_path, remote_path):
        file_name = file_path.split("/")[len(file_path.split("/")) - 1]
        if file_name == "":
            raise Exception('error: the file path format is incorrect, and the transfer folder is not supported')
        if remote_path.split("/")[len(remote_path.split("/")) - 1] == "":
            remote_path += file_name
        header = {
            "content-type": "application/json",
            "FileName": remote_path
        }
        f = open(file_path, 'rb')
        data = {'file': (file_name, f.read())}
        f.close()
        encode_data = encode_multipart_formdata(data)
        data = encode_data[0]
        header['Content-Type'] = encode_data[1]
        return bool(int(str(self.device.con.post(path="upLoadFile", headers=header, data=data).read(), 'utf-8')))

    def file_exist(self, file_path):
        return bool(int(str(self.device.con.get(path="checkFileExist", args="filename=" + file_path).read(), 'utf-8')))

    def file_remove(self, file_path):
        return bool(int(str(self.device.con.get(path="fileRemove", args="filename=" + file_path).read(), 'utf-8')))

    def file_move(self, source_path, target_path):
        return bool(int(str(self.device.con.get(path="fileMove", args="source=" + source_path + "&target=" + target_path).read(), 'utf-8')))

    def file_copy(self, source_path, target_path):
        return bool(int(str(self.device.con.get(path="fileCopy", args="source=" + source_path + "&target=" + target_path).read(), 'utf-8')))

    def dir_exist(self, dir_path):
        return self.file_exist(dir_path)

    def mkdir(self, dir_path):
        return bool(int(str(self.device.con.get(path="mkdir", args="dirname=" + dir_path).read(), 'utf-8')))

    def is_installed(self, sopid):
        return bool(int(str(self.device.con.get(path="isAppInstalled", args="sopid=" + sopid).read(), 'utf-8')))

    def is_uninstallable(self, sopid):
        return bool(int(str(self.device.con.get(path="isAppUninstallable", args="sopid=" + sopid).read(), 'utf-8')))

    def install(self, file_path):
        if self.upload_file(file_path, "/tmp/"):
            file_name = file_path.split("/")[len(file_path.split("/")) - 1]
            self.device.con.get(path="install", args="filepath=/tmp/" + file_name)
            return True
        return False

    def uninstall(self, sopid):
        return bool(int(str(self.device.con.get(path="uninstall", args="sopid=" + sopid).read(), 'utf-8')))

    def system_time(self):
        return int(str(self.device.con.get(path="getDatetime").read(), 'utf-8'))

    def latest_toast(self):
        return str(self.device.con.get(path="getLatestToast").read(), 'utf-8')

    def clear_app_data(self, sopid):
        return self.__reply_status_check(self.device.con.get(path="clearAppData", args="sopid=" + sopid))

    def get_panel_state(self):
        return bool(int(str(self.device.con.get(path="getPanelState").read(), 'utf-8')))

    def set_panel_open(self):
        if not self.get_panel_state():
            return self.__reply_status_check(self.device.con.get(path="setPanelState"))

    def set_panel_close(self):
        if self.get_panel_state():
            return self.__reply_status_check(self.device.con.get(path="setPanelState"))

    def launch(self, sopid, uiappid, timeout=None):
        self.device.refresh_layout()
        self.device.con.get(path="launchApp", args="sopid=" + sopid + "&" + "uiappid=" + uiappid)
        if timeout is None:
            timeout = self.device.default_timeout
        die_time = int(time.time()) + timeout
        while int(time.time()) < die_time:
            self.device.refresh_layout()
            selector = etree.XML(self.device.xmlStr.encode('utf-8'))
            if selector.get("sopId") == sopid:
                return True
            self.device.con.get(path="launchApp", args="sopid=" + sopid + "&" + "uiappid=" + uiappid)
            sleep(1)
        return False

    def close(self, sopid):
        return self.__reply_status_check(self.device.con.get(path="quitApp", args="sopid=" + sopid))

    def is_topmost(self, sopid):
        self.device.refresh_layout()
        selector = etree.XML(self.device.xmlStr.encode('utf-8'))
        if selector.get("sopId") == sopid:
            return True
        return False

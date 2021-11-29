#!/usr/bin/env python3
# -*    - coding: utf-8 -*-

"""
It is intended to facilitate the management of Bluetooth devices.
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

try:
    # noinspection PyUnresolvedReferences
    import bluetooth
except Exception as e:
    print(e)
from ..Shell import print_error


class Bluetooth:
    def __init__(self):
        self.__session = None
        self.connection_status = False
        self.device = None
        self.devices = None
        self.port = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def get_devices(self, filter_names=None):
        self.devices = ['None']
        try:
            for mac, name in bluetooth.discover_devices(lookup_names=True, flush_cache=True):
                if filter_names and name in filter_names:
                    self.devices.append(mac)
        except Exception as error:
            print_error(error, locals())
        return self.devices

    def connect(self):
        try:
            if self.__session is None and self.port is not None:
                self.__session = bluetooth.Bluetooth(bluetooth.RFCOMM)
                self.__session.connect((self.port, 1))
                print(f'------------->{self.device} -- #{self.port}# Device Connection Successful')
                self.connection_status = True
        except Exception as error:
            print_error(error, locals())
            self.disconnect()

    def disconnect(self):
        try:
            if self.__session is not None:
                self.__session.close()
                print(f'------------->{self.device} -- #{self.port}# Device Disconnect Successful')
        except Exception as error:
            print_error(error, locals())
        self.__session = None
        self.connection_status = False

    def send(self, command, command_name):
        try:
            self.__session.send(f'<{command}>'.encode())
            print(f'{self.port} >> {self.device} ---> Send :::> {command_name} --->{command}')
        except Exception as error:
            print_error(error, locals())

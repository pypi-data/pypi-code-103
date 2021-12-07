#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Developed for data retrieval over target with Telnet Protocol.
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

import telnetlib
from ..Decorators import try_except
from ..Shell import print_error


class Telnet:
    def __init__(self):
        self.host = None
        self.port = None
        self.timeout = None
        self.__session = None

    def connect(self, host, port, timeout):
        try:
            self.__session = telnetlib.Telnet(timeout=timeout)
            self.host = host
            self.port = port
            self.timeout = timeout
            self.__session.open(host, port, timeout)
            print(f'---> Telnet Connected successfully Host:{host}/Port:{port}/Timeout:{timeout}')
        except Exception as error:
            print(f"#########> Telnet connection problem:::>{error}")
            self.disconnect()

    @try_except
    def disconnect(self):
        if self.__session:
            self.__session.close()
        self.__init__()
        print(':::::::::::> Telnet connection was disconnected successfully')

    def send_and_read(self, command, read_until):
        print(f':::::::::::> Telnet Write Command:{command} --- Read Until String:{read_until}')
        data = None
        if self.__session:
            try:
                self.__session.write(f'{command}\n'.encode())
                data = self.__session.read_until(read_until.encode(), timeout=self.timeout)
                data = data + self.__session.read_some()
                data = data.decode(encoding='UTF-8', errors='ignore')
                data = data.replace('\x05', '').split('\r\n')
                data = data[0] if len(data) == 1 else data
                if isinstance(data, str):
                    data = data.split('\n')
                print(f':::::::::::> Telnet Reading Completed...')
            except Exception as error:
                print_error(error, locals())
        else:
            print(f'Data could not be read because there is no telnet connection.')
            print(f'Return data:{data}')
        return data

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Here, the whole package is gathered with the design pattern logic.
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

from .Apps.DataFrame import DataFrame
from .Apps.Excel import Excel
from .Apps.FileRw import FileRw
from .Apps.Image import Photo
from .Apps.Matlab import Matlab
from .Apps.Selenium import Selenium
from .Apps.Svn import RemoteClient
from .Apps.Telegram import Telegram
from .Databases.PostgreSQL import PostgreSQL
from .Databases.SQLite import SQLite
from .DateTime import DateTime
from .Devices.Audio import Audio
from .Devices.Bluetooth import Bluetooth
from .Devices.Webcam import Webcam
from .Gui.Tkinter import Tkinter
from .OS import OperatingSystem
from .Other import Other
from .Protocols.Ftp import Ftp
from .Protocols.Smtp import Smtp
from .Protocols.Telnet import Telnet
from .Shell import Cmd


class Apps:
    def __init__(self):
        self.data_frame = DataFrame()
        self.excel = Excel()
        self.file = FileRw()
        self.image = Photo()
        self.matlab = Matlab()
        self.selenium = Selenium()
        self.svn = RemoteClient(None)
        self.telegram = Telegram()


class Config:
    pass


class Databases:
    def __init__(self):
        self.postgresql = PostgreSQL()
        self.sqlite = SQLite()


class Devices:
    def __init__(self):
        self.audio = Audio()
        self.bluetooth = Bluetooth()
        self.webcam = Webcam()


class Functions:
    def __init__(self):
        self.cmd = Cmd()
        self.date_time = DateTime()
        self.os = OperatingSystem()
        self.other = Other()


class Gui:
    def __init__(self):
        self.tk = Tkinter()


class Protocols:
    def __init__(self):
        self.ftp = Ftp()
        self.smtp = Smtp()
        self.telnet = Telnet()


class Platform:
    def __init__(self):
        self.apps = Apps()
        self.config = Config()
        self.db = Databases()
        self.devices = Devices()
        self.functions = Functions()
        self.gui = Gui()
        self.protocols = Protocols()

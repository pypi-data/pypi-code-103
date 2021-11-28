#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Provides FTP server/Client management.
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

import os
from ftplib import FTP, all_errors
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from ..Decorators import try_except, calculate_time_processing
from ..OS import delete_files_or_folders
from ..ParallelProcessing import ThreadWithReturnValue


class Server:
    def __init__(self):
        self.__session = None
        self.__worker = None

    @try_except
    def __start(self, ip, port, directory, handler):
        print(f'IP:{ip} ---> Port:{port} ---> Directory:{directory}')
        self.__session = FTPServer((ip, port), handler)
        self.__session.serve_forever()
        print(f'{ip} FTP Server Started...')

    @try_except
    def connect(
            self, ip, directory, port=21, username='ftp', password='ftp', perm='elradfmw',
            msg_login="Login successful.", msg_quit="Goodbye.", add_anonymous_user=True
    ):
        if self.__worker:
            self.disconnect()
        authorizer = DummyAuthorizer()
        authorizer.add_user(
            username, password, "/", perm=perm, msg_login=msg_login, msg_quit=msg_quit
        )
        if add_anonymous_user:
            authorizer.add_anonymous(directory, perm="elradfmwM")
        handler = FTPHandler
        handler.authorizer = authorizer
        handler.banner = "pyftpdlib based ftpd ready."
        self.__worker = ThreadWithReturnValue(
            target=self.__start,
            name='FtpServer',
            args=(ip, port, directory, handler),
            daemon=False
        )
        self.__worker.start()

    @try_except
    def disconnect(self):
        if self.__session is not None:
            self.__session.close_all()
        if self.__worker is not None:
            self.__worker.join(1)
        self.__session = None
        self.__worker = None
        print('FTP server was stopped successfully')


class Client:
    def __init__(self):
        self.__session = None

    @try_except
    def connect(self, host='', user='', passwd='', acct='', source_address=None):
        self.__session = FTP(
            host=host, user=user, passwd=passwd, acct=acct, source_address=source_address
        )
        message = self.__session.login('', '')
        print(f'-------------> FTP {host} ---> {message}')
        return message[0] == '2', message

    @try_except
    def disconnect(self):
        if self.__session:
            print(self.__session.quit())
        self.__session = None
        print(f'-------------> FTP shut down successfully.')

    @try_except
    def go_to_root_directory(self):
        for _ in range(len(self.__session.pwd().split('/'))):
            self.__session.cwd('..')
        print(f'Current directory:{self.__session.pwd()}')

    @try_except
    def dir_cleaner(self):
        for n in self.__session.nlst():
            try:
                if n not in ('.', '..'):
                    try:
                        print(f'{self.__session.delete(n)} ---> {n}')
                    except all_errors:
                        self.__session.cwd(n)
                        self.dir_cleaner()
                        self.__session.cwd('..')
                        print(f'{self.__session.rmd(n)} ---> {n}')
            except all_errors:
                print(f'{self.__session.rmd(n)} ---> {n}')

    @try_except
    def dir_ch(self, dir_name):
        if isinstance(dir_name, list):
            self.go_to_root_directory()
        else:
            dir_name = [dir_name]
        for name in dir_name:
            try:
                self.__session.mkd(name)
            except all_errors:
                pass
            print(self.__session.cwd(name))

    def delete_file(self, file_name):
        try:
            print(f'{self.__session.delete(file_name)} ---> {file_name}')
        except all_errors:
            pass

    def delete_directory(self, directory):
        try:
            print(f'{self.__session.rmd(directory)} ---> {directory}')
        except all_errors:
            pass

    @try_except
    @calculate_time_processing
    def file_upload(self, ftp_address, file_path):
        if os.path.exists(file_path):
            print(f'-------------> FTP files are loading: {file_path}')
            self.dir_ch(str(ftp_address).split('/'))
            self.delete_file(os.path.basename(file_path))
            with open(file_path, "rb") as file:
                message = self.__session.storbinary(f'STOR {os.path.basename(file_path)}', file)
            print(self.__session.dir())
        else:
            message = f'FTP File not found to transfer:::> {ftp_address}'
        print(f'-------------> {message}')
        return message[0] == '2', message

    @try_except
    @calculate_time_processing
    def file_download(self, ftp_address, file_path):
        print(f'-------------> FTP files downloading: {file_path}')
        self.dir_ch(str(os.path.dirname(ftp_address)).split('/'))
        delete_files_or_folders(file_path)
        with open(file_path, "wb") as file:
            message = self.__session.retrbinary(
                f"RETR {os.path.basename(ftp_address)}", file.write
            )
        print(f'-------------> {message}')
        return message[0] == '2', message


class Ftp:
    def __init__(self):
        self.client = Client()
        self.server = Server()
        self.use_local = False
        self.ip = None
        self.port = 21
        self.directory = None

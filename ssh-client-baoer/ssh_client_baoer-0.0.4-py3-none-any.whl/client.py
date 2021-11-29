import os
import socket
from typing import Text

import paramiko

from .unix_path import join as unix_join


class SSHClient(object):
    """
    SSH client, you can use it to execute shell command and upload or download file with SFTP.
    """

    def __init__(self, host, user, passwd, working_dir=os.path.abspath(os.path.curdir), port=22) -> None:
        super().__init__()
        self.__host = host
        self.__port = port
        self.__user = user
        self.__passwd = passwd
        self.__transport = None
        self.__ssh_client = None
        self.__sftp_client = None
        self.__working_dir = working_dir
        self.__TIMEOUT = 180.0
        self.__RECEIVE_SIZE = 1000

    def connect(self) -> None:
        """
        Create SSH session.
        """
        self.__transport = paramiko.Transport(self.__host, self.__port)
        self.__transport.connect(username=self.__user, password=self.__passwd)
        self.__sftp_client = paramiko.SFTPClient.from_transport(self.__transport)
        self.__ssh_client = paramiko.SSHClient()
        self.__ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.__ssh_client.connect(self.__host, self.__port, self.__user, self.__passwd)

    def close(self) -> None:
        """
        Close SSH session.
        """
        self.__transport.close()
        self.__ssh_client.close()

    def exec(self, cmd: Text, invoke_mod=False, timeout=None) -> None:
        """
        Execute a command on remote.
        """

        if invoke_mod:
            invoke = self.__ssh_client.invoke_shell()
            invoke.settimeout(self.__TIMEOUT if timeout is None else timeout)
            invoke.sendall(cmd + '\n')

            stdout_buffer = b""
            try:
                while True:
                    stdout = invoke.recv(self.__RECEIVE_SIZE)
                    stdout_buffer += stdout
            except socket.timeout:
                print("Stdout timeout ...")
            finally:
                print(str(stdout_buffer, encoding="utf-8"))

            stderr_buffer = b""
            try:
                while True:
                    stderr = invoke.recv_stderr(self.__RECEIVE_SIZE)
                    stderr_buffer += stderr
            except socket.timeout:
                print("Stderr timeout ...")
            finally:
                print(str(stderr_buffer, encoding="utf-8"))
            return

        _, stdout, stderr = self.__ssh_client.exec_command(cmd + '\n',
                                                           timeout=self.__TIMEOUT if timeout is None else timeout)

        for line in stdout:
            print('... ' + line.strip('\n'))

        for line in stderr:
            print('... ' + line.strip('\n'))

    def upload(self, local_path: Text, remote_path: Text) -> None:
        """
        Upload file to remote.
        :param local_path: local file path.
        :param remote_path: remote file path.
        """
        self.__sftp_client.put(local_path, remote_path)
        print('Upload %s to %s ... success.' % (local_path, remote_path))

    def upload_to(self, local_path: Text, remote_dir: Text) -> None:
        """
        Upload file to remote directory.
        :param local_path: local file path.
        :param remote_dir: remote directory.
        """
        file_name = os.path.split(local_path)[1]
        self.upload(local_path, unix_join(remote_dir, file_name))

    def upload_working_to(self, file_name, remote_dir) -> None:
        """
        Upload file in working directory to remote directory.
        :param file_name: file name.
        :param remote_dir: remote directory.
        """
        self.upload(os.path.join(self.__working_dir, file_name), unix_join(remote_dir, file_name))

    def upload_files(self, **kwargs):
        for file, target_path in kwargs.items():
            self.upload_working_to(file, target_path)

    def download(self, remote_path: Text, local_path: Text):
        """
        Download file.
        :param remote_path: remote file path.
        :param local_path: local file path.
        """
        self.__sftp_client.get(remote_path, local_path)
        print('Download %s to %s ... success.' % (remote_path, local_path))

    def download_to_working(self, remote_path) -> None:
        """
        Download file to working directory.
        :param remote_path: remote file path.
        """
        file_name = os.path.split(remote_path)[1]
        self.download(remote_path, os.path.join(self.__working_dir, file_name))

    def download_files(self, *args):
        for file in args:
            self.download_to_working(file)

import logging
import os
from typing import Text

from fabric import Connection
from invoke.exceptions import CommandTimedOut

logger = logging.getLogger("ssh_client")


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
        self.__connection = None
        self.__working_dir = working_dir

    def connect(self) -> None:
        """
        Create SSH session.
        """
        self.__connection = Connection(host=self.__host, user=self.__user, connect_kwargs={"password": self.__passwd})

    def close(self) -> None:
        """
        Close SSH session.
        """
        self.__connection.close()

    def exec(self, cmd: Text, pty=False, timeout=None, ignore_timeout=False, ignore_exit=False) -> None:
        """
        Execute a command on remote.
        """
        logger.info('Command: %s.', cmd)
        try:
            result = self.__connection.run(cmd, pty=pty, timeout=timeout, warn=ignore_exit)
            logger.info('Command: %s, exit code: %s.', cmd, result.exited)
        except CommandTimedOut as e:
            if ignore_timeout:
                logger.warning('Execute Command Timeout: %s.', cmd)
                return
            raise e

    def upload(self, local_path: Text, remote_path: Text) -> None:
        """
        Upload file to remote directory.
        :param local_path: local file path.
        :param remote_path: remote directory or file.
        """
        self.__connection.put(local_path, remote_path)
        logger.info('Upload %s to %s successfully.', local_path, remote_path)

    def upload_working(self, file_name, remote_path) -> None:
        """
        Upload file in working directory to remote directory.
        :param file_name: file name.
        :param remote_path: remote directory or file.
        """
        self.__connection.put(os.path.join(self.__working_dir, file_name), remote_path)

    def upload_files(self, **kwargs):
        for file, target_path in kwargs.items():
            self.upload_working(os.path.join(self.__working_dir, file), target_path)

    def download(self, remote_path: Text, local_path: Text):
        """
        Download file.
        :param remote_path: remote file path.
        :param local_path: local directory or file.
        """
        self.__connection.get(remote_path, local_path)
        logger.info('Download %s to %s successfully.', remote_path, local_path)

    def download_working(self, remote_path) -> None:
        """
        Download file to working directory.
        :param remote_path: remote file path.
        """
        self.download(remote_path, self.__working_dir)

    def download_files(self, *args):
        for file in args:
            self.download_working(file)

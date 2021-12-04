# coding=utf-8
import logging
import os
import stat
import subprocess
from typing import List


__author__ = 'ThucNC'
_logger = logging.getLogger(__name__)


class ShellHelper:
    @staticmethod
    def detect_executable(command):
        """
        Try to find an `command` executable. It first looks in
        ./command/, then the local directory, then in a relative path
        from the file that contains the Sandbox module, then in the
        system paths.

        return (string): the path to a valid (hopefully) command.

        """
        paths = [os.path.join('', command, command),
                 os.path.join('', command)]
        if '__file__' in globals():
            paths += [os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                '..', '..', command, command))]
        paths += [command]
        print(paths)
        for path in paths:
            # Consider only non-directory, executable files with SUID flag on.
            if os.path.exists(path) \
                    and not os.path.isdir(path) \
                    and os.access(path, os.X_OK):
                st = os.stat(path)
                if st.st_mode & stat.S_ISUID != 0:
                    return path

        # As default, return self.exec_name alone, that means that
        # system path is used.
        return paths[-1]

    @staticmethod
    def execute(commands: List[str], strip_output=True, raise_exception=False, timeout=60, input=None):
        process = subprocess.run(commands, stdout=subprocess.PIPE,
                                 universal_newlines=True, stderr=subprocess.PIPE,
                                 timeout=timeout, input=input)
        # print(process)
        if process.returncode != 0:
            msg = f"Failed to run command {commands} with error: {process.returncode}, stderr: \n {process.stderr} "
            if raise_exception:
                raise Exception(msg)
            else:
                _logger.error(msg)

        res = process.stdout
        if strip_output:
            res = res.strip()
        return res


if __name__ == "__main__":
    print(ShellHelper.detect_executable("python"))

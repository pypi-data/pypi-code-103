import os
import yaml
import copy
from pathlib import Path
from shutil import copyfile
from abc import ABC, abstractmethod


class ManagedClass(ABC):

    def __init__(self, execpath):
        self._installfolder = Path(execpath).parent
        self.homevar = "{}/var/{}".format(str(Path.home()), self.getClassName())

        if not os.path.exists(self.homevar):
            os.makedirs(self.homevar)

    @classmethod
    @abstractmethod
    def getClassName(cls):
        pass

    def getHomevarPath(self):
        return "{}/var/{}".format(str(Path.home()), self.getClassName())

    def is_raspberry_pi(self, raise_on_errors=False):
        """Checks if Raspberry PI.
           :return:
        """
        import io
        try:
            with io.open('/proc/cpuinfo', 'r') as cpuinfo:
                found = False
                for line in cpuinfo:
                    if line.startswith('Hardware'):
                        found = True
                        label, value = line.strip().split(':', 1)
                        value = value.strip()
                        if value not in (
                            'BCM2708',
                            'BCM2709',
                            'BCM2711',
                            'BCM2835',
                            'BCM2836'
                        ):
                            if raise_on_errors:
                                raise ValueError(
                                    'This system does not appear to be a '
                                    'Raspberry Pi.'
                                )
                            else:
                                return False
                if not found:
                    if raise_on_errors:
                        raise ValueError(
                            'Unable to determine if this system is a Raspberry Pi.'
                        )
                    else:
                        return False
        except IOError:
            if raise_on_errors:
                raise ValueError('Unable to open `/proc/cpuinfo`.')
            else:
                return False

        return True

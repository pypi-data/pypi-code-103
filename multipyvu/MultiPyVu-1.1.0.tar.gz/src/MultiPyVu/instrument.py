# -*- coding: utf-8 -*-
"""
instrument.py is used to hold information about MultiVu.  It has
the various flavors, and can determine which version of MultiVu is installed
on a machine.

Created on Tue May 18 13:14:28 2021

@author: djackson
"""

import sys
import subprocess
import time
import logging
from enum import Enum, auto

from .project_vars import SERVER_NAME

if sys.platform == 'win32':
    try:
        import pythoncom
        import win32com.client
    except ImportError:
        print("Must import the pywin32 module.  Use:  ")
        print("\tconda install -c conda-forge pywin32")
        print("   or")
        print("\tpip install pywin32")
        sys.exit(0)


class InstrumentList(Enum):
    DYNACOOL = auto()
    PPMS = auto()
    VERSALAB = auto()
    MPMS3 = auto()
    OPTICOOL = auto()
    na = auto()


class Instrument():
    def __init__(self,
                 flavor: str = '',
                 scaffolding_mode=False,
                 run_with_threading=False,
                 verbose=False
                 ):
        '''
        This class is used to detect which flavor of MultiVu is installed
        on the computer.  It is also used to return the name of the .exe
        and the class ID, which can be used by win32com.client.

        Parameters
        ----------
        flavor : string, optional
            This is the common name of the MultiVu flavor being used.  If
            it is left blank, then the class finds the installed version
            of MultiVu to know which flavor to use.  The default is ''.
        scaffolding_mode : bool, optional
            This flag puts the class in scaffolding mode, which simulates
            MultiVu.  The default is False.
        run_with_threading : bool, optional
            This flag is used to configure win32com.client to be used in
            a separate thread.  The default is False.
        verbose : bool, optional
            When set to True, the flavor of MultiVu is displayed
            on the command line. The default is False.
        '''
        self.logger = logging.getLogger(SERVER_NAME)
        self.scaffolding_mode = scaffolding_mode
        self.run_with_threading = run_with_threading
        self.verbose = verbose

        self.name = ''
        if flavor == '':
            if self.scaffolding_mode:
                err_msg = 'Must choose a MultiVu flavor to run in '
                err_msg += 'scaffolding mode.'
                for f in InstrumentList:
                    err_msg += f'\n\t{f.name}' if f != f.na else ''
                raise MultiVuExeException(err_msg)
        else:
            # If specified, check that it's a allowed flavor; if not,
            # print an error
            found = False
            for instrument in InstrumentList:
                if instrument.name.upper() == flavor.upper():
                    self.name = flavor.upper()
                    found = True
                    break
            if not found:
                err_msg = f'The specified MultiVu flavor, {flavor}, is not '
                err_msg += 'recognized. Please use one of the following:'
                for f in InstrumentList:
                    err_msg += f'\n\t{f}'
                raise MultiVuExeException(err_msg)

        self.exe_name = ''
        self.class_id = ''
        self.mv_id = None
        self.multi_vu = None
        if not self.scaffolding_mode:
            self.exe_name = self._get_exe(self.name)
            self.class_id = self._get_class_id(self.name)
            self._connect_to_MultiVu(self.name,
                                     self.class_id,
                                     run_with_threading
                                     )

    def _get_exe(self, inst: str) -> str:
        '''
        Returns the name of the MultiVu exe.

        Parameters
        ----------
        inst : str
            The name of the MultiVu flavor.

        Returns
        -------
        TYPE
            A string of the specific MultiVu flavor .exe

        '''
        if inst.upper() == InstrumentList.PPMS.name:
            name = inst.capitalize() + 'Mvu'
        elif inst.upper() == InstrumentList.MPMS3.name:
            name = 'SquidVsm'
        elif inst.upper() == InstrumentList.VERSALAB.name:
            name = 'VersaLab'
        elif inst.upper() == InstrumentList.OPTICOOL.name:
            name = 'OptiCool'
        else:
            name = inst.capitalize()
        name += '.exe'
        return name

    def _get_class_id(self, inst: str) -> str:
        '''
        Parameters
        ----------
        inst : str
            The name of the MultiVu flavor.

        Returns
        -------
        string
            The MultiVu class ID.  Used for things like opening MultiVu.

        '''
        class_id = f'QD.MULTIVU.{inst}.1'
        return class_id

    def _connect_to_MultiVu(self,
                            instrument_name: str,
                            class_id: str,
                            using_threading=False):

        if sys.platform != 'win32':
            err_msg = 'The server only works on a Windows machine. However, the server\n'
            err_msg += 'can be tested using the -s flag,along with specifying \n'
            err_msg += 'the MultiVu flavor.'
            raise MultiVuExeException(err_msg)

        detected_name = self.detect_multivu()
        if detected_name != instrument_name:
            if instrument_name == '':
                msg = f'Found {detected_name} running.'
            else:
                msg = f'User specified {instrument_name}, but detected '
                msg += f'{detected_name} running.  Will use '
                msg += f'{detected_name}.'
            self.logger.info(msg)
            self.name = detected_name
            self.exe_name = self._get_exe(self.name)
            self.class_id = self._get_class_id(self.name)
        if using_threading:
            self.initialize_multivu_win32com()
        else:
            self.multivu_win32com_single_thread()

    def detect_multivu(self) -> str:
        '''
        This looks in the file system for an installed version of
        MultiVu.  Once it find it, the function returns the name.

        Raises
        ------
        MultiVuExeException
            This is thrown if MultiVu is not running, or if multiple
            instances of MultiVu are running.

        Returns
        -------
        string
            Returns the common name of the QD instrument.

        '''
        # Build a list of enum, instrumentType
        instrument_names = list(InstrumentList)
        # Remove the last item (called na)
        instrument_names.pop()

        # Use WMIC to get the list of running programs with 'multivu'
        # in their path
        cmd = 'WMIC PROCESS WHERE "COMMANDLINE like \'%multivu%\'" GET '
        cmd += 'Caption,Commandline,Processid'
        with subprocess.Popen(cmd,
                              shell=True,
                              stdout=subprocess.PIPE
                              ) as proc:
            # Attempt to match the expected MV executable names with
            # the programs in the list and instantiate the instrument
            # and add to MultiVu_list.

            # TODO - This code uses a list of known MultiVu exe's and
            # compares that to every line in the list of running processes.
            # It might be faster to get a list of running processes, and
            # compare the names with what is in the instrument_names list.
            # In my case, there are typically only a few programs running.
            MultiVu_list = []
            for line in proc.stdout:
                if (line == b'\r\r\n' or line == b'\r\n'):
                    break
                # Ignore the header
                if (line.decode().startswith('Caption')):
                    continue
                for instr in instrument_names:
                    instr_name = self._get_exe(instr.name.capitalize())
                    if line.decode().startswith(instr_name):
                        MultiVu_list.append(instr.name)
                        # exe found, so break and continue to look for
                        # other running MultiVu flavors
                        break

        # Declare errors if to few or too many are found; for one found,
        # declare which version is identified
        if len(MultiVu_list) == 0:
            err_msg = '''
No running instance of MultiVu was detected. Please
start MultiVu and retry, or use the -s flag to enable
the scaffolding.'''
            raise MultiVuExeException(err_msg)

        elif len(MultiVu_list) > 1:
            err_msg = 'There are multiple running instances of '
            err_msg += f'MultiVu {MultiVu_list} detected.  '
            err_msg += 'Please close all but one and retry, '
            err_msg += 'or specify the flavor to connect to.  See the '
            err_msg += 'help (-h)'
            raise MultiVuExeException(err_msg)

        elif len(MultiVu_list) == 1:
            self.name = MultiVu_list[0]
            msg = MultiVu_list[0] + " MultiVu detected."
            if self.verbose:
                self.logger.info(msg)
            else:
                self.logger.debug(msg)
            return self.name

    def get_multivu_win32com_instance(self):
        '''
        This method is used to get an instance of the win32com.client
        and is necessary when using threading.

        This method updates self.multi_vu

        Raises
        ------
        MultiVuExeException
            This error is thrown if it is unable to connect to MultiVu.

        Returns
        -------
        None.

        '''
        if self.run_with_threading:
            max_tries = 3
            for attempt in range(max_tries):
                try:
                    # This will try to connect Python with MultiVu
                    pythoncom.CoInitialize()
                    # Get an instance from the ID
                    self.multi_vu = win32com.client.Dispatch(
                        pythoncom.CoGetInterfaceAndReleaseStream(
                            self.mv_id,
                            pythoncom.IID_IDispatch
                            )
                        )
                    break
                except pythoncom.com_error as e:
                    if attempt >= max_tries-1:
                        err_msg = f'Quitting script after {attempt + 1} '
                        err_msg += 'failed attempts to connect to MultiVu.'
                        raise MultiVuExeException(err_msg) from e
            time.sleep(0.3)

    def initialize_multivu_win32com(self):
        '''
        This creates an instance of the MultiVu ID which is
        used for enabling win32com to work with threading.

        This method updates self.multi_vu and self.mv_id

        Raises
        ------
        MultiVuExeException
            No detected MultiVu running, and initialization failed.

        '''
        max_tries = 3
        for attempt in range(max_tries):
            try:
                # This will try to connect Python with MultiVu
                pythoncom.CoInitialize()
                # Get an instance
                self.multi_vu = win32com.client.Dispatch(self.class_id)
                # Create id
                self.mv_id = pythoncom.CoMarshalInterThreadInterfaceInStream(
                    pythoncom.IID_IDispatch,
                    self.multi_vu
                    )
                break
            except pythoncom.com_error as e:
                pythoncom_error = vars(e)['strerror']
                if pythoncom_error == 'Invalid class string':
                    err_msg = f'PythonCOM error:  {pythoncom_error}:'
                    err_msg += 'Error instantiating wind32com.client.Dispatch '
                    err_msg += f'using class_id = {self.class_id}'
                    err_msg += '\nTry reinstalling MultiVu.'
                if attempt >= max_tries-1:
                    err_msg = f'Quitting script after {attempt + 1} '
                    err_msg += 'failed attempts to detect a running copy '
                    err_msg += 'of MultiVu.'
                raise MultiVuExeException(err_msg) from e
            time.sleep(0.3)

    def multivu_win32com_single_thread(self):
        max_tries = 3
        for attempt in range(max_tries):
            try:
                self.multi_vu = win32com.client.Dispatch(self.class_id)
                break
            except pythoncom.com_error as e:
                pythoncom_error = vars(e)['strerror']
                if pythoncom_error == 'Invalid class string':
                    err_msg = f'PythonCOM error:  {pythoncom_error}:'
                    err_msg += 'Error instantiating wind32com.client.Dispatch '
                    err_msg += f'using class_id = {self.class_id}'
                    err_msg += '\nTry reinstalling MultiVu.'
                if attempt >= max_tries-1:
                    err_msg += f'\nQuitting script after {attempt + 1} '
                    err_msg += 'failed attempts to detect a running copy '
                    err_msg += 'of MultiVu.'
                    raise MultiVuExeException(err_msg) from e
            time.sleep(0.3)


class MultiVuExeException(Exception):
    """MultiVu Exception Error"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message

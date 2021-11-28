#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
It is aimed to facilitate the necessary installations for python with the tkinter interface on
Linux and Windows systems.

Used as follows;

EXECUTABLE = install(
        executable=sys.executable,
        proxy='proxy_server:8080',
        linux_packages='curl gcc openssl libssl-dev portaudio19-dev python3-pyaudio libpq-dev',
        linux_multi_line_command=None,
        virtual_environment_path=os.path.join(os.getcwd(), 'env3'),
        python_packages_gohlke='pyaudio pygresql',
        python_packages='corut',
        create_app_shortcut={
            'App1': {
                'ShortCutPath': os.path.join(os.getcwd(), 'App1'),
                'AppPath': os.path.join(os.getcwd(), 'App.py'),
                'WorkingDirectory': os.getcwd(),
                'AppIconPath': os.path.join(os.getcwd(), 'ico.ico'),
                'Parameters': None
            },
            'App2': {
                'ShortCutPath': os.path.join(os.getcwd(), 'App2'),
                'AppPath': os.path.join(os.getcwd(), 'App.py'),
                'WorkingDirectory': os.getcwd(),
                'AppIconPath': os.path.join(os.getcwd(), 'ico.ico'),
                'Parameters': '--report'
            }
        }
    )
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

import logging
import os
import re
import shutil
import sys
from io import BytesIO
from pathlib import Path
from platform import machine
from subprocess import PIPE, Popen, STDOUT
from tempfile import gettempdir
from threading import Thread
try:
    from tkinter import Tk, Frame, Text, Scrollbar, simpledialog
except Exception as _e:
    print(_e, '\n\n')
    print('For Linux Please run the following command from console...\n')
    print('sudo apt-get install python3-tk -y\n\n')
from urllib import request

PASSWORD = None
FILE_LOG = os.path.join(gettempdir(), 'CorutApplicationInstallation.log')
logging.basicConfig(
    filename=FILE_LOG,
    filemode="w",
    format='[%(asctime)s.%(msecs)03d]\t%(message)s',
    datefmt='%Y/%m/%d - %H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger()


class _DialogFrame(Tk):
    def __init__(self):
        super().__init__()
        self.__add_frame()
        self.__ask_question(
            'Enter Password',
            'Enter the sudo user password.'.ljust(70, ' ')
        )
        self.__reader_flag = True
        self.__reader = Thread(target=self.__file_reader, name='LogReader', daemon=True)
        self.__reader.start()

    def __add_frame(self):
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.wm_title('Cörüt Installer...')
        txt_frm = Frame(self, width=800, height=600)
        txt_frm.pack(fill='both', expand=True)
        txt_frm.grid_propagate(False)
        txt_frm.grid_rowconfigure(0, weight=1)
        txt_frm.grid_columnconfigure(0, weight=1)
        self.txt = Text(txt_frm, borderwidth=3, relief='sunken')
        self.txt.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
        scroll_bar = Scrollbar(txt_frm, command=self.txt.yview)
        scroll_bar.grid(row=0, column=1, sticky='nsew')
        self.txt.config(
            yscrollcommand=scroll_bar.set,
            font=('aerial', 10),
            undo=True,
            wrap='word'
        )

    def __ask_question(self, title, prompt):
        global PASSWORD
        if sys.platform.startswith('linux'):
            self.withdraw()
            PASSWORD = simpledialog.askstring(title=title, prompt=prompt)
            self.call('encoding', 'system', 'utf-8')
            self.update()
            self.deiconify()

    def __file_reader(self):
        file = open(FILE_LOG, 'r')
        while self.__reader_flag:
            line = str(file.readline()).encode('UTF-8', errors="ignore")
            if line:
                self.txt.insert('end', line)
                self.txt.see("end")
        file.close()
        logger.info(msg='File Reader Stopped')

    def close(self):
        self.__reader_flag = False
        self.destroy()
        self.quit()
        logger.info(msg='Program Closed.')

    def run(self):
        self.mainloop()


class _GohlkeDownloader:
    def __init__(self, proxy=None):
        try:
            from lxml import html
            import ssl
            # noinspection PyUnresolvedReferences,PyProtectedMember
            ssl._create_default_https_context = ssl._create_unverified_context
            self.index = None
            self.packages = {}
            self.last_retrieve = None
            req = request.Request(
                'https://www.lfd.uci.edu/~gohlke/pythonlibs', headers={'User-Agent': 'custom'}
            )
            if proxy:
                req.set_proxy(proxy, 'http')
                req.set_proxy(proxy, 'https')
            response = request.urlopen(req)
            self.index = response.read()
            root = html.parse(BytesIO(self.index))
            self.packages = {}
            for list_item in root.xpath('//ul[@class="pylibs"]/li[a[@id]]'):
                identifier = str(list_item.xpath('a/@id')[0])
                if identifier == 'misc':
                    break
                self.packages[identifier] = {
                    anchor.text: self.__get_info(str(anchor.xpath('@onclick')[0])) for anchor in [
                        li for li in list_item.xpath('ul/li/a') if Path(li.text).suffix == '.whl'
                    ]
                }
        except Exception as error:
            logger.error(msg=error)

    def __getitem__(self, item):
        return self.packages[item]

    @staticmethod
    def __get_info(js_link):
        def dl1(ml, mi):
            lnk = 'https://download.lfd.uci.edu/pythonlibs/'
            for j in range(len(mi)):
                lnk += chr(ml[ord(mi[j]) - 47])
            return lnk

        def dl(ml, mi):
            mi = mi.replace('&lt;', '<')
            mi = mi.replace('&#62;', '>')
            mi = mi.replace('&#38;', '&')
            return dl1(ml, mi)

        match = re.search(r'dl\(\[(.*)], "(.*?)"', js_link)
        if match:
            link = dl(list(map(int, match.group(1).split(','))), match.group(2))
            parts = Path(link).stem.split('-')
            has_build_skip = 1 if parts[2][0].isdigit() else 0
            return {
                'link': link,
                'version': parts[1],
                'python': (lambda x: f'{x[2]}.{x[3:]}')(parts[2 + has_build_skip]),
                'platform': parts[4 + has_build_skip]
            }
        else:
            return None

    def download(self, target, wanted_package):
        downloaded_file = None
        if wanted_package not in self.packages:
            logger.info(msg=f'The searched {wanted_package} package was not found')
        else:
            versions = self.packages[wanted_package]
            for _, values in versions.items():
                if values['python'] != f'{sys.version_info.major}.{sys.version_info.minor}':
                    continue
                if values['platform'] != ('win_amd64' if machine() == 'AMD64' else 'win32'):
                    continue
                downloaded_file = Path(target) / Path(values['link']).name
                if not downloaded_file.is_file():
                    opener = request.build_opener()
                    # noinspection SpellCheckingInspection
                    opener.addheaders = [('User-agent', 'Custom')]
                    request.install_opener(opener)
                    self.last_retrieve = values['link']
                    logger.info(msg=f'File download started from link: ---> {self.last_retrieve}')
                    request.urlretrieve(self.last_retrieve, downloaded_file)
                    logger.info(msg=f'{downloaded_file} file downloaded successfully.')
        return downloaded_file


class _Installer:
    def __init__(
            self,
            executable,
            proxy=None,
            linux_packages=None,
            linux_multi_line_command=None,
            virtual_environment_path=None,
            python_packages_gohlke=None,
            python_packages=None,
            create_app_shortcut=None
    ):
        self.executable = executable
        self.proxy = proxy
        self.__proxy = f' --proxy http://{proxy} ' if proxy else ' '
        self.__packages_linux = linux_packages
        self.__linux_multi_line_command = linux_multi_line_command
        self.__path_venv = virtual_environment_path
        self.__packages_python_gohlke = python_packages_gohlke
        self.__packages_python = python_packages
        self.__app_shortcut = create_app_shortcut
        try:
            process = Thread(target=self.__run_process, name='Installer', daemon=True)
            process.start()
        except (KeyboardInterrupt, SystemExit) as error:
            logger.error(msg=error)

    @staticmethod
    def __run_command(command, password=None):
        logger.info(msg=f'------------------> Command:{command}')
        try:
            with Popen(
                    command,
                    stdin=PIPE, stdout=PIPE, stderr=STDOUT, shell=True,
                    encoding='utf8', universal_newlines=True
            ) as process:
                if password:
                    process.stdin.write(f'{password}\n')
                    process.stdin.flush()
                for line in process.stdout:
                    logger.info(msg=line)
        except Exception as error:
            logger.error(msg=f'Subprocess Error:{error}')
        logger.info(msg='#' * 99)

    @staticmethod
    def __check_command(cmd):
        if cmd is None:
            return []
        elif type(cmd) == str:
            return cmd.split()
        elif type(cmd) == list:
            return cmd
        else:
            logger.info(msg='#' * 99)
            logger.info(msg=f'{cmd} command entered is incorrect')
            logger.info(msg='#' * 99)
            return cmd

    def __run_process(self):
        if sys.platform.startswith('linux'):
            self.__install_linux_packages('python3-dev python3-pip python3-wheel python3-venv')
            self.__install_linux_packages(self.__packages_linux)
            if self.__linux_multi_line_command:
                self.__install_linux_packages(str(self.__linux_multi_line_command).splitlines())
        try:
            import pip
        except ImportError as error:
            logger.error(msg=error)
            self.__run_command(f"{self.executable} -m ensurepip --default-pip")
        self.__install_python_packages('pip lxml certifi')
        self.__install_env(self.__path_venv)
        self.__install_python_packages('pip setuptools wheel importlib_metadata lxml certifi')
        if sys.platform.startswith('win'):
            self.__install_python_packages_gohlke(self.__packages_python_gohlke)
        self.__install_python_packages(self.__packages_python)
        self.__create_app_shortcut()
        logger.info(
            '\n\n\n\nThe update was successful. Close the window and run the application again.\n'
            'You can check the installation details from the log file.\n'
            f'File:{FILE_LOG}'
            '\n\n\n\nUpdate completed...\n\n'
        )
        return self.executable

    def __create_app_shortcut(self):
        try:
            for name, values in self.__app_shortcut.items():
                path_shortcut, app_path, directory, icon, parameters = values.values()
                parameters = parameters if parameters else ''
                if sys.platform.startswith('linux'):
                    text = (
                        "#!/usr/bin/env xdg-open\n"
                        "[Desktop Entry]\n"
                        "Version=1.0\n"
                        "Type=Application\n"
                        f"Name={name}\n"
                        "Comment=\n"
                        f"Exec={self.executable} {app_path} {parameters}\n"
                        f"Icon={icon}\n"
                        f"Path={directory}\n" if directory else ''
                        "Terminal=false\n"
                        "StartupNotify=false\n"
                        f"Keywords={name}\n"
                    )
                    path_shortcut += '.desktop'
                else:
                    if directory:
                        directory_dir = f'{os.path.splitdrive(directory)[0]}\n'
                        directory_dir += f'cd {directory}\n'
                    else:
                        directory_dir = ''
                    text = (
                        directory_dir +
                        f'start {self.executable}w.exe {app_path} {parameters}\n'
                    )
                    path_shortcut += '.bat'
                with open(path_shortcut, 'w') as f:
                    f.writelines(text)
                logger.info(msg=f'Create Application Shortcut Success:{path_shortcut}')
                if sys.platform.startswith('linux'):
                    self.__run_command(f'chmod 770 {path_shortcut}')
                    self.__run_command(
                        f'cp -r {path_shortcut} {str(Path.home())}/.local/share/applications'
                    )
        except Exception as error:
            logger.error(msg=f'Create Application Shortcut Error:{error}')

    @staticmethod
    def __delete_files_or_folders(paths):
        try:
            paths = paths if isinstance(paths, list) else [paths]
            for path in paths:
                try:
                    if os.path.exists(path):
                        shutil.rmtree(path, ignore_errors=True)
                    if os.path.exists(path):
                        os.remove(path)
                except PermissionError as error:
                    logger.error(msg=error)
                logger.info(msg=f':::::> DELETE SUCCESS: {path}')
        except Exception as error:
            logger.info(msg=f'\n\n:::::::::::::::> DELETE ERROR!: {error}\nPaths:{paths}\n\n')

    def __install_env(self, path):
        if path:
            x, y = os.path.split(self.executable)
            logger.info(msg=f'{y} ---> Executable Path:{x}')
            if sys.platform.startswith('linux'):
                executable_base = os.sep.join([sys.base_prefix, 'bin', y])
            else:
                executable_base = os.sep.join([sys.base_prefix, 'python'])
            self.__run_command(f'{executable_base} -m pip install -U{self.__proxy}virtualenv')
            if not os.path.exists(path):
                self.__run_command(f'{executable_base} -m venv {path}')
            logger.info(msg=f'Virtual Environment installation completed successfully.Path:{path}')
            if sys.platform.startswith('linux'):
                self.executable = os.sep.join([path, 'bin', y])
            else:
                self.executable = os.sep.join([path, 'Scripts', 'python'])
            logger.info(msg=f'New environment will continue as {self.executable}')

    def __install_linux_packages(self, packages):
        for package in self.__check_command(packages):
            self.__run_command(f'sudo -S apt-get install {package} -y', PASSWORD)

    def __install_python_packages(self, packages):
        for package in self.__check_command(packages):
            self.__run_command(f'{self.executable} -m pip install -U{self.__proxy}{package}')

    def __install_python_packages_gohlke(self, packages):
        for package in self.__check_command(packages):
            path = _GohlkeDownloader(self.proxy).download(gettempdir(), package)
            if path:
                self.__run_command(
                    f'{self.executable} -m pip install {path}{self.__proxy}--force-reinstall'
                )
                self.__delete_files_or_folders(path)
            logger.info(msg='#' * 99)


def install(
        executable,
        proxy=None,
        linux_packages=None,
        linux_multi_line_command=None,
        virtual_environment_path=None,
        python_packages_gohlke=None,
        python_packages=None,
        create_app_shortcut=None
):
    logger.info(f'Start Application Installation...')
    try:
        app = _DialogFrame()
        installer = _Installer(
            executable,
            proxy,
            linux_packages,
            linux_multi_line_command,
            virtual_environment_path,
            python_packages_gohlke,
            python_packages,
            create_app_shortcut
        )
        app.run()
        executable = installer.executable
    except Exception as error:
        logger.error(msg=error)
    logging.shutdown()
    return executable

#
#  Copyright (c) 2018-2019 Renesas Inc.
#  Copyright (c) 2018-2019 EPAM Systems Inc.
#

import logging
import os
import shutil
from distutils.dir_util import copy_tree
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
from pathlib import Path
from tempfile import TemporaryDirectory

from colorama import Fore, Style
from lxml.etree import tostring

from aos_signer.service_config.service_configuration import ServiceConfiguration
from .errors import SignerError
from .file_details import FileDetails
from ..service_config.config_xml_generator import ConfigXMLGenerator

logger = logging.getLogger(__name__)


class Signer:
    _SERVICE_FOLDER = "service"
    _DEFAULT_STATE_NAME = "default_state.dat"
    _THREADS = cpu_count()
    _SERVICE_FILE_ARCHIVE_NAME = 'service'

    def __init__(self, src_folder, package_folder, config: ServiceConfiguration):
        self._config = config
        self._src = src_folder
        self._package_folder = package_folder

    def process(self):
        with TemporaryDirectory() as tmp_folder:
            self._copy_application(folder=tmp_folder)
            self._copy_yaml_conf(folder=tmp_folder)
            self._copy_state(folder=tmp_folder)
            self._generate_config(folder=tmp_folder)
            file_name = self._compose_archive(folder=tmp_folder)
            print(f"{Fore.GREEN}Service archive created: {file_name}{Style.RESET_ALL}")

    def _copy_state(self, folder):
        state_info = self. _config.configuration.state
        print("Copying default state...       ", end='')
        # print(state_info)
        if not state_info:
            print(f"{Fore.YELLOW}SKIP{Style.RESET_ALL}")
            return
        if not state_info.get('required', False):
            print(f"{Fore.YELLOW}SKIP{Style.RESET_ALL}")
            return
        state_filename = state_info.get('filename', 'state.dat')
        if state_filename:
            try:
                shutil.copy(
                    os.path.join('meta', state_filename),
                    os.path.join(folder, self._DEFAULT_STATE_NAME)
                )
                print(f"{Fore.GREEN}DONE{Style.RESET_ALL}")
            except FileNotFoundError:
                print(f"{Fore.RED}ERROR{Style.RESET_ALL}")
                raise SignerError(f"State file '{state_filename}' defined in the configuration does not exist.")

    def _copy_application(self, folder):
        print("Copying application...         ", end='')
        temp_service_folder = Path(folder) / self._SERVICE_FOLDER
        temp_service_folder.mkdir(parents=True, exist_ok=True)
        copy_tree(self._src, str(temp_service_folder), preserve_symlinks=True)
        print(f"{Fore.GREEN}DONE{Style.RESET_ALL}")

    def _copy_yaml_conf(self, folder):
        print("Copying configuration...       ", end='')
        shutil.copyfile(self._config.config_path, os.path.join(folder, 'config.yaml'))
        print(f"{Fore.GREEN}DONE{Style.RESET_ALL}")

    def _generate_config(self, folder):
        print("Generating config.xml...       ", end='')
        file_details = self._calculate_file_hashes(folder=folder)
        xml_config_generator = ConfigXMLGenerator(self._config)
        xml_config = tostring(xml_config_generator.generate(file_details=file_details))
        with open(Path(folder) / 'config.xml', "wb") as fp:
            fp.write(xml_config)
        print(f"{Fore.GREEN}DONE{Style.RESET_ALL}")

    def _calculate_file_hashes(self, folder):
        pool = ThreadPool(self._THREADS)
        file_details = []
        src_len = len([item for item in folder.split(os.path.sep) if item])

        regular_files_only = True

        for root, dirs, files in os.walk(folder):
            splitted_root = [item for item in root.split(os.path.sep) if item][src_len:]
            if splitted_root:
                root = os.path.join(*splitted_root)
            else:
                root = ""

            # Check for links in directories
            for dir_name in dirs:
                full_dir_name = os.path.join(folder, root, dir_name)
                if os.path.islink(full_dir_name):
                    if self._config.build.symlinks == 'delete':
                        logger.info("Removing non-regular directory '{}'".format(os.path.join(root, dir_name)))
                        os.remove(full_dir_name)
                    elif self._config.build.symlinks == 'raise':
                        logger.error("This is not a regular directory '{}'.".format(os.path.join(root, dir_name)))
                        regular_files_only = False

            # Process files
            for file_name in files:
                full_file_name = os.path.join(folder, root, file_name)

                if os.path.islink(full_file_name):
                    if self._config.build.symlinks == 'delete':
                        logger.info("Removing non-regular file '{}'".format(os.path.join(root, file_name)))
                        os.remove(full_file_name)
                    elif self._config.build.symlinks == 'raise':
                        logger.error("This is not a regular file '{}'.".format(os.path.join(root, file_name)))
                        regular_files_only = False
                    continue

                file_details.append(FileDetails(
                    root=folder,
                    file=os.path.join(root, file_name)
                ))

        if not regular_files_only:
            raise SignerError("Source code folder contains non regular file(s).")

        pool.map(FileDetails.calculate, file_details)

        return file_details

    def _compose_archive(self, folder):
        print("Creating archive...            ", end='')
        arch = shutil.make_archive(os.path.join(self._package_folder, self._SERVICE_FILE_ARCHIVE_NAME), "gztar", folder)
        print(f"{Fore.GREEN}DONE{Style.RESET_ALL}")
        return arch

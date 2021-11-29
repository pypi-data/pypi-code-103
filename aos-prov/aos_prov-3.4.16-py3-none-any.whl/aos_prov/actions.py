#
#  Copyright (c) 2018-2021 Renesas Inc.
#  Copyright (c) 2018-2021 EPAM Systems Inc.
#
import os
import platform
import subprocess
import time
import zipfile
from pathlib import PurePath, Path

from aos_prov.command_provision import run_provision

from aos_prov.utils.user_credentials import UserCredentials

from aos_prov.communication.cloud.cloud_api import CloudAPI
from aos_prov.command_download import download_vbox_sdk, DOWNLOADS_PATH


def create_new_unit(vm_name, do_provision=False):
    uc = UserCredentials(cert_file_path=None,
                         key_file_path=None,
                         pkcs12=str(PurePath(Path.home() / '.aos' / 'security' / 'aos-user-oem.p12')))
    cloud_api = CloudAPI(uc)
    cloud_api.check_cloud_access()
    if platform.system() == 'Linux':
        from aos_prov.command_vm_libvirt import create_libvirt_vm
        unit_uuid, vm_port = create_libvirt_vm(vm_name, None)
    elif platform.system() == 'Darwin':
        from aos_prov.command_vm_libvirt import create_libvirt_vm
        unit_uuid, vm_port = create_libvirt_vm(vm_name, None)
    elif platform.system() == 'Windows':
        from aos_prov.command_vm import new_vm, start_vm
        vm_port = new_vm(vm_name, None)
        start_vm(vm_name)
    if do_provision:
        time.sleep(10)
        run_provision(f'127.0.0.1:{vm_port}', cloud_api, reconnect_times=20)


def install_vbox_sdk():
    file = download_vbox_sdk()

    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(DOWNLOADS_PATH)

    envs = os.environ.copy()
    if platform.system() == 'Windows':
        command = 'python vboxapisetup.py install --user'
    elif platform.system() == 'Linux':
        command = 'VBOX_INSTALL_PATH=$(which virtualbox) python3 vboxapisetup.py install --user --prefix='
    elif platform.system() == 'Darwin':
        command = 'VBOX_INSTALL_PATH=/Applications/VirtualBox.app/Contents/MacOS python3 vboxapisetup.py install --user --prefix='
    else:
        command = 'VBOX_INSTALL_PATH=$(which virtualbox) python3 vboxapisetup.py install --user --prefix='
    return_code = subprocess.run(command, shell=True, env=envs, cwd=str(Path(DOWNLOADS_PATH / 'sdk' / 'installer')))
    if return_code.returncode == 0:
        return
    else:
        print('Error installing VirtualBox SDK')

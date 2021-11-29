#
#  Copyright (c) 2018-2019 Renesas Inc.
#  Copyright (c) 2018-2019 EPAM Systems Inc.
#

import os
from colorama import Fore, Style
from aos_signer.signer.errors import NoAccessError

_meta_folder_name = 'meta'
_src_folder_name = 'src'
_config_file_name = 'config.yaml'


def run_bootstrap():
    _create_folder_if_not_exist(_meta_folder_name)
    _create_folder_if_not_exist(_src_folder_name)
    _init_conf_file()
    print(Fore.GREEN + "DONE" + Style.RESET_ALL + '\n')
    _print_epilog()


def _create_folder_if_not_exist(folder_name):
    try:
        if os.path.isdir(folder_name):
            print("Directory {}[{}]{} exists... {}Skipping{}".format(
                Fore.CYAN, folder_name, Style.RESET_ALL, Fore.YELLOW, Style.RESET_ALL)
            )
        else:
            os.mkdir(folder_name)
            print("Directory {}[{}]{} created.".format(Fore.CYAN, folder_name, Style.RESET_ALL))
    except PermissionError:
        raise NoAccessError


def _init_conf_file():
    conf_file_path = os.path.join(_meta_folder_name, _config_file_name)
    if os.path.isfile(conf_file_path):
        print("Configuration file {cyan}[{filename}]{reset} exists... {yellow}Skipping{reset}".format(
            cyan=Fore.CYAN, filename=_config_file_name, reset=Style.RESET_ALL, yellow=Fore.YELLOW)
        )
    else:
        with open(conf_file_path, 'x') as cfp:
            cfp.write(_config_bootstrap)
        print(f"Config file  {Fore.CYAN}{_meta_folder_name}/{_config_file_name}{Fore.RESET + Style.DIM} created")


def _print_epilog():
    print('---------------------------')
    print(Style.DIM + 'Further steps:')
    print(f'Copy your service files with desired folders to {Fore.CYAN}[src]{Fore.RESET + Style.DIM} folder.')
    print("Update " + Fore.CYAN + "meta/config.yaml" + Fore.RESET + " with desired values.")
    print("Run '" + Style.BRIGHT + Fore.BLUE + "aos-signer sign" + Style.RESET_ALL + Style.DIM +
          "' to sign service and '" + Style.BRIGHT + Fore.BLUE + "aos-signer upload" + Style.RESET_ALL + Style.DIM +
          "' to upload signed service to the cloud.")


_config_bootstrap = """
# Commented sections are optional. Uncomment them if you want to include them in config

#publisher: # General publisher info section
#    author: # Author info
#    company: # Company info

# How to build and sign package
build:
    os: linux
    arch: x86
    sign_pkcs12: aos-user-sp.p12
    symlinks: copy
    # context: string, optional

# Information about publishing process (URI, cert, etc)
publish:
    url: aoscloud.io
    service_uid: #Service UID can be found on the Cloud service details page 
    tls_pkcs12: aos-user-sp.p12

# Service configuration
configuration:
    state:
        filename: state.dat
        required: False

    # Startup command
    cmd: #service start command
    # Service working dir
    workingDir: #service working directory

#    devices:
#        - name : string (camera0, mic0, audio0, etc)
#          mode  : rwm

#    resources:
#        - system-dbus
#        - bluetooth
        
#    hostname: my-container
    
#    exposedPorts:
#        - 8089-8090/tcp
#        - 1515/udp
#        - 9000

#    allowedConnections:
#        - 9931560c-be75-4f60-9abf-08297d905332/8087-8088/tcp
#        - 9931560c-be75-4f60-9abf-08297d905332/1515/udp

#    Quotas assigned to service
#      quotas:
#        cpu: 50
#        mem: 2KB
#        state: 64KB
#        storage: 64KB
#        upload_speed: 32Kb
#        download_speed: 32Kb
#        upload: 1GB
#        download: 1GB
#        temp: 32KB
#   
#  Resource alerts
#    alerts:
#        ram:
#            minTime: string
#            minThreshold: 10,
#            maxThreshold: 150
#        cpu:
#            minTime: string
#            minThreshold: 40,
#            maxThreshold: 45
#        storage:
#            minTime: string
#            minThreshold: 10,
#            maxThreshold: 150
#        upload:
#            minTime: string
#            minThreshold: 10,
#            maxThreshold: 150
#        download:
#            minTime: string
#            minThreshold: 10,
#            maxThreshold: 150
#
#    Permissions for functional servers
#    permissions:
         # functional server
#        vis:
             # functionality name: access mode
#            Attribute.Body.Vehicle.VIN: "r"
#            Signal.Doors.* : "rw"
#    env:
#       - MY_ENV_VAR1=this env var will be set for the service'
#       - MY_ENV_VAR2=this_to
#    layers:
#       - 'layer_uid'
#
"""

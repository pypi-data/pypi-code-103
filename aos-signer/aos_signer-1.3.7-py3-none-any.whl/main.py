#
#  Copyright (c) 2018-2019 Renesas Inc.
#  Copyright (c) 2018-2019 EPAM Systems Inc.
#

import argparse
import sys

from colorama import Fore, Style

from aos_signer import __version__
from aos_signer.signer.bootstrapper import run_bootstrap
from aos_signer.signer.errors import SignerConfigError, SignerError
from aos_signer.signer.signer import Signer, logger
from aos_signer.signer.uploader import run_upload
from aos_signer.service_config.service_configuration import ServiceConfiguration

_COMMAND_INIT = 'init'
_COMMAND_SIGN = 'sign'
_COMMAND_UPLOAD = 'upload'
_COMMAND_VALIDATE = 'validate'
_COMMAND_GO = 'go'


def run_init_signer():
    print("{}Starting INIT process...{}".format(Fore.GREEN, Style.RESET_ALL))
    run_bootstrap()
    sys.exit(0)

def run_validate(config: ServiceConfiguration):
    print("{}Starting CONFIG VALIDATION process...{}".format(Fore.LIGHTBLACK_EX, Style.RESET_ALL))
    ServiceConfiguration('meta/config.yaml')
    print("{}Config is valid{}".format(Fore.GREEN, Style.RESET_ALL))


def run_upload_service(config: ServiceConfiguration, sys_exit=True):
    print("{}Starting SERVICE UPLOAD process...{}".format(Fore.LIGHTBLACK_EX, Style.RESET_ALL))
    try:
        run_upload(config)
        if sys_exit:
            sys.exit(0)
    except OSError:
        print(Fore.RED + str(sys.exc_info()[1]))
        sys.exit(1)


def run_sign(config: ServiceConfiguration, sys_exit=True):
    print("{}Starting SERVICE SIGNING process...{}".format(Fore.LIGHTBLACK_EX, Style.RESET_ALL))
    try:
        logger.info("Validating config . . .")
        s = Signer(src_folder='src', package_folder='.', config=config)
        s.process()

        if sys_exit:
            sys.exit(0)
    except OSError:
        print(Fore.RED + str(sys.exc_info()[1]) + Style.RESET_ALL)


def run_go(config: ServiceConfiguration):
    run_sign(config, sys_exit=False)
    run_upload(config)


def main():
    from colorama import init
    init()
    parser = argparse.ArgumentParser(
        prog='Aos Signer Tool',
        description='This tool will help you to prepare, sign and upload service to Aos Cloud'
    )
    parser.add_argument('-V', '--version', action='store_true', help='Print aos-signer version number and exit')
    parser.set_defaults(which=None)

    sub_parser = parser.add_subparsers(title='Commands')

    init = sub_parser.add_parser(
        _COMMAND_INIT,
        help='Generate required folders and configuration file. If you don\'t know where to start type aos-signer init'
    )
    init.set_defaults(which=_COMMAND_INIT)

    validate = sub_parser.add_parser(
        _COMMAND_VALIDATE,
        help='Validate config file.'
    )
    validate.set_defaults(which=_COMMAND_VALIDATE)

    sign = sub_parser.add_parser(
        _COMMAND_SIGN,
        help='Sign Service. Read config and create signed archive ready to be uploaded.'
    )
    sign.set_defaults(which=_COMMAND_SIGN)

    upload = sub_parser.add_parser(
        _COMMAND_UPLOAD,
        help='Upload Service to the Cloud.'
             'Address, security credentials and service UID is taken from config.yaml in meta folder.'
    )
    upload.set_defaults(which=_COMMAND_UPLOAD)

    go = sub_parser.add_parser(
        _COMMAND_GO,
        help='Sign and upload Service to the Cloud.'
             'Address, security credentials and service UID are taken from config.yaml in meta folder.'
    )
    go.set_defaults(which=_COMMAND_GO)

    args = parser.parse_args()
    try:
        if args.version:
            print(__version__)
            sys.exit(0)

        if args.which is None:
            config = ServiceConfiguration('meta/config.yaml')
            run_sign(config)

        if args.which == _COMMAND_INIT:
            run_init_signer()

        config = ServiceConfiguration('meta/config.yaml')
        if args.which == _COMMAND_VALIDATE:
            print("{}Config is valid{}".format(Fore.GREEN, Style.RESET_ALL))

        if args.which == _COMMAND_SIGN:
            run_sign(config)

        if args.which == _COMMAND_UPLOAD:
            run_upload_service(config)

        if args.which == _COMMAND_GO:
            run_go(config)

    except SignerError as se:
        print(Fore.RED + 'Process failed with error: ')
        print(str(se) + Style.RESET_ALL)
        sys.exit(1)
    except Exception as sce:
        print(Fore.RED + 'Process failed with error: ')
        print(str(sce) + Style.RESET_ALL)
        logger.exception(sce)
        sys.exit(1)


if __name__ == '__main__':
    main()

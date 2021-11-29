#!/usr/bin/env python3

import argparse
import os
import rollbar
import sys


SCRIPT_LOCATION = os.path.dirname(os.path.realpath(__file__))
ROOT_PATH = os.path.normpath(os.path.join(SCRIPT_LOCATION, '..'))
CONFIG_LOCATION = os.path.join(SCRIPT_LOCATION, 'logfit_config.yaml')
sys.path.append(ROOT_PATH)

from logfit import __version__
from logfit.client import LogFit
from logfit.config import Config, ROLLBAR_TOKEN, ROLLBAR_ENV


def main():
    """ Set up rollbar error reporting """
    rollbar.init(ROLLBAR_TOKEN, ROLLBAR_ENV)
    try:
        parse_args(sys.argv[1:])
    except KeyboardInterrupt:
        pass
    except Exception:
        rollbar.report_exc_info()
        raise


def parse_args(sys_args):
    """ Parse sys.argv cli commands """
    parser = argparse.ArgumentParser(
        description='Read and upload log files to log.fit'
    )
    parser.add_argument(
        'command',
        choices=['start', 'run', 'foreground', 'stop', 'restart', 'status'],
    )
    parser.add_argument(
        '-v', '--version', action='version', version=__version__,
    )
    parser.add_argument(
        '-c', '--config', help='Path to config file', default=CONFIG_LOCATION,
    )
    args = parser.parse_args(sys_args)
    run_logfit(args.command, args.config)


def run_logfit(command, config_file):
    """ Generate configs and run logfit """
    config = Config()
    config.read_config_file(config_file)
    logfit_client = LogFit(
        pidfile="/tmp/logfit.pid",
        config=config,
    )
    if command == 'start':
        logfit_client.start()
    elif command in ['run', 'foreground']:
        logfit_client.run()
    elif command == 'stop':
        logfit_client.stop()
    elif command == 'restart':
        logfit_client.restart()
    elif command == 'status':
        logfit_client.is_running()


if __name__ == "__main__":
    main()

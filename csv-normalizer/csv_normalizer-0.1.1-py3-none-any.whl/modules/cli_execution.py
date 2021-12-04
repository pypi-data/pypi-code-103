# This Python file uses the following encoding: utf-8
import configparser
import os
import pprint
import argparse
from . import configs
from . import csv_normalizer

def parse_args(args):
    """
    Parse command line configuration with argparse.ArgumentParser
    :return: parse.parse_args(args)
    added_arguments:
        '-c', '--config_ini', dest='config_ini'
        '--version', dest='version', default=None, const=True
        '--write_config', dest='write_config', default=None, action='store_true'
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-c', '--config_ini', dest='config_ini',
                        const=os.path.join(os.sep, 'etc', 'csv_normalizer', 'csv_normalizer.ini'),
                        default=None,
                        nargs='?', help='csv_normalizer ini configuration file')

    parser.add_argument('--version', dest='version', nargs='?', default=None, const=True,
                        help='Print version and exit')
    
    parser.add_argument('--no_rename', dest='no_rename_old', nargs='?', default=None, const=True,
                        help='Do not rename to .old the original file')

    parser.add_argument('--write_config', dest='write_config', default=None, action='store_true',
                        help="Write configuration with default values, useful to get a config file to modify")

    if not args:
        raise SystemExit(parser.print_help())

    return parser.parse_args(args)

def cli_execution(argparse_options):
    """
    Manage command line options for cli usage
    :param options:
    :return:
    Will run the process and print to stdout the dict summary
    """

    # Configs that can be overwritten by command line options
    config_options = configs.get_all_config(argparse_options.config_ini)
    config_options_dict = configs.get_common_config_dict(argparse_options.config_ini)

    if argparse_options.write_config:
        if not argparse_options.config_ini:
            raise SystemExit('--write_config requires -c config_file.ini')

        with open(argparse_options.config_ini, 'w', encoding='utf-8') as f:
            config_options.write(f, space_around_delimiters=True)
            raise SystemExit(f'Configuration written to {argparse_options.config_ini}')
    
    # Initiate csv_normalizer objet to work with it.
    csv_normalizer_obj = csv_normalizer.Csv_Normalizer(config_dict=config_options_dict, 
                                            no_rename_old=argparse_options.no_rename_old)
    # Execute the process
    summary_execution_dict = csv_normalizer_obj.run()
    # Just print summary result dict in pprint
    pprint.pprint(
        dict(summary_execution_dict)
        )

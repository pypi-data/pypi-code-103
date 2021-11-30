import argparse
import logging
import os
import sys

from swagger2case import __version__
from swagger2case.core import SwaggerParser


def main():
    parser = argparse.ArgumentParser(
        description="Convert swagger testcases to yaml testcases for HttpRunner.")
    parser.add_argument("-V", "--version", dest='version', action='store_true',
        help="show version")
    parser.add_argument('--log-level', default='INFO',
        help="Specify logging level, default is INFO.")

    parser.add_argument('swagger_testset_file', nargs='?',
        help="Specify swagger testset file.")

    parser.add_argument('--output_file_type', nargs='?',
        help="Optional. Specify output file type.")

    parser.add_argument('--output_dir', nargs='?',
        help="Optional. Specify output directory.")

    args = parser.parse_args()

    if args.version:
        print("{}".format(__version__))
        exit(0)

    log_level = getattr(logging, args.log_level.upper())
    logging.basicConfig(level=log_level)

    swagger_testset_file = args.swagger_testset_file
    output_file_type = args.output_file_type
    output_dir = args.output_dir

    if not swagger_testset_file or not swagger_testset_file.endswith(".json"):
        logging.error("swagger_testset_file file not specified.")
        sys.exit(1)
    
    if not output_file_type:
        output_file_type = "yaml"
    else:
        output_file_type = output_file_type.lower()
    if output_file_type not in ["json", "yml", "yaml"]:
        logging.error("output file only support json/yml/yaml.")
        sys.exit(1)
    
    if not output_dir:
        output_dir = '.'

    swagger_parser = SwaggerParser(swagger_testset_file)
    parse_result, name = swagger_parser.parse_data()
    swagger_parser.save(parse_result, output_dir, output_file_type=output_file_type, name=name)

    return 0








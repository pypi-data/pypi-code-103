#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""YSTAFDB CLI

Usage:
  ystafdb-cli -i <input/dirpath> -o <output/dirpath> -f <format>

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
import argparse
from docopt import docopt
from ystafdb import generate_ystafdb
import sys


def main():
    parser = argparse.ArgumentParser(description='Extract rdf from ystafdb')
    parser.add_argument('-i', '--input',
                        dest='indir',
                        required=False,
                        default='ystafdb/data/',
                        help='path to ystafdb csv files')

    parser.add_argument('-o', '--output',
                        dest='outdir',
                        required=False,
                        default='output/',
                        help='Output directory')

    parser.add_argument('-f', '--format',
                        dest='format',
                        choices=['nt','ttl','xml'],
                        default='ttl',
                        help='The output format')

    args = parser.parse_args()

    try:
        generate_ystafdb(args)
    except KeyboardInterrupt:
        print("Terminating CLI")
        sys.exit(1)


if __name__ == "__main__":
    main()

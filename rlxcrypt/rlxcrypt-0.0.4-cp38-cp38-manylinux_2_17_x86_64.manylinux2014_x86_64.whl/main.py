import argparse
import logging
import sys

from rlxcrypt import __version__
print ("rlxcrypt version", __version__)
from .loader import generate_keys, file_encrypt

__author__ = "rramosp"
__copyright__ = "rramosp"
__license__ = "MIT"

def parse_args(args):
    parser = argparse.ArgumentParser(prog='rlxcrypt')

    subparsers = parser.add_subparsers(help='sub-command help', dest='command')

    # create the parser for the "generate" command
    parser_a = subparsers.add_parser('generate_keys', help='generates public and private key pair')
    parser_a.add_argument("--prefix", type=str, default="", help="prefix for file names")

    # create the parser for the "encrypt" command
    parser_b = subparsers.add_parser('encrypt', help='encrypt a python file')
    parser_b.add_argument("input_file", type=str, help="python file to script (must end in '.py')")
    parser_b.add_argument("--overwrite", default=False, action="store_true",  help="overwrite output file")

    args = parser.parse_args(args)

    if args.command=='encrypt' and not args.input_file.endswith(".py"):
        raise ValueError(f"input_file must be a '.py' file, got '{args.input_file}'")

    return args

def main(args):

    args = parse_args(args)

    if args.command == 'generate_keys':
        generate_keys(args.prefix+"public_key.pem", args.prefix+"private_key.pem")        

    elif args.command == "encrypt":
        file_encrypt(args.input_file, args.input_file+"e")


def run():
    main(sys.argv[1:])

if __name__ == "__main__":
    run()

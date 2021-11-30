'''Main module.'''
import argparse
import logging
from sys import stdout
from typing import TextIO
from os import linesep
from top_names.name_list import NameList

#DEFAULT_OUTFILE = os.path.join(os.path.split(os.path.abspath(__file__))[0],"output.txt")

def main(*, output: TextIO = stdout):
    """
    Create scrapers for the top names of the last thirteen decades and \
        output them to the given output.
    :param output: TextIO stream to write to. Default is stdout.
    :param time_between_requests: Time in millis between requests.\
         Defaults to 200 to be nice.
    :raises RuntimeError: Can raise RuntimeError from scalper if a\
         200 Response is not given by the website.
    """
    name_list = NameList()
    for name in name_list:
        output.write(name)
        output.write(linesep)
    output.flush()

def cli_entry_point():
    '''Command line entry point.'''
    parser = argparse.ArgumentParser(\
        description="Scrape a list of the top baby names from the last thirteen decades.")
    parser.add_argument(\
        '--output', '-o', help="Output file.", type=argparse.FileType('w'), default=stdout)
    parser.add_argument(\
        '--debug', '-d', help="Enables debug logging.", action="store_true")
    args = parser.parse_args()
    outfile = args.output
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    try:
        main(output=outfile)
    finally:
        outfile.close()

if __name__ == "__main__":
    cli_entry_point()

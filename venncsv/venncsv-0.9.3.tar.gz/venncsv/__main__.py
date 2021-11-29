#!/usr/bin/python3

# imports

from .__init__ import __doc__ as description, __version__ as version
from argparse import ArgumentParser as Parser, RawDescriptionHelpFormatter as Formatter
from warnings import simplefilter
from sys import argv
from libfunx import get_source, get_target, ask
from os import popen
from os.path import split as pathsplit

# globals

class args: pass # container for arguments

# main

def venncsv(argv):
    """'$ venncsv x.csv y.csv' then writes x_and_y.csv, x_or_y.csv, x_xor_y.csv, x_minus_y.csv and y_minus_y.csv"""

    parser = Parser(prog='venncsv', formatter_class=Formatter, description=description) # get arguments
    parser.add_argument('-V', '--version',   action='version', version='venncsv ' + version)
    parser.add_argument('-v', '--verbose',   action='store_true', help='show what happens')
    parser.add_argument('-y', '--yes',       action='store_true', help='overwrite existing output files (default: ask)')
    parser.add_argument('-n', '--no',        action='store_true', help='don\'t overwrite existing output files (default: ask)')
    parser.add_argument("-o", "--open",      action="store_true", help='at end open input and output files for check and print (default: ask)')
    parser.add_argument("-q", "--quit",      action="store_true", help='at end don\'t open input and output files for check and print (default: ask)')
    parser.add_argument('-A', '--x-and-y',   action='store_true', help='write x_and_y.csv   = x.csv & y.csv')
    parser.add_argument('-O', '--x-or-y',    action='store_true', help='write x_or_y.csv    = x.csv | y.csv')
    parser.add_argument('-X', '--x-xor-y',   action='store_true', help='write x_xor_y.csv   = x.csv ^ y.csv')
    parser.add_argument('-M', '--x-minus-y', action='store_true', help='write x_minus_y.csv = x.csv - y.csv')
    parser.add_argument('-W', '--y-minus-x', action='store_true', help='write y_minus_x.csv = y.csv - x.csv')
    parser.add_argument('x_csv', help='1st input file')
    parser.add_argument('y_csv', help='2nd input file')
    parser.parse_args(argv[1:], args)
    if not (args.x_and_y or args.x_or_y or args.x_xor_y or args.x_minus_y or args.y_minus_x):
        args.x_and_y, args.x_or_y, args.x_xor_y, args.x_minus_y, args.y_minus_x = 5 * [True]
    files = []
    
    def read_csv(input):
        input = get_source(input, '.csv')
        files.append(input)
        head = None
        rows = set()
        for line in open(input):
            line = line.rstrip()
            if head is None:
                head = line
            elif line:
                rows.add(line)
        if head is None:
            exit(f'Header not found in input file {input!r}')
        if not head:
            exit(f'Empty header in input file {input!r}')
        if args.verbose:
            print(f'{len(rows)} rows <-- {input!r}')
        return head, rows

    head1, rows1 = read_csv(args.x_csv)
    head2, rows2 = read_csv(args.y_csv)
    if head1 != head2:
        exit('Input file headers don\'t match')
    
    def write_csv(x_csv, op, y_csv, rows):
        x_csv = pathsplit(x_csv)[-1]
        y_csv = pathsplit(y_csv)[-1]
        output = get_target(f'{x_csv[:-4]}_{op}_{y_csv}', '.csv', yes=args.yes, no=args.no)
        files.append(output)
        with open(output, 'w') as out:
            print(head1, file=out)
            for row in sorted(rows):
                print(row, file=out)
        if args.verbose:
            print(f'{len(rows)} rows --> {output!r}')

    if args.x_and_y:   write_csv(args.x_csv, 'and',   args.y_csv, rows1 & rows2)
    if args.x_or_y:    write_csv(args.x_csv, 'or',    args.y_csv, rows1 | rows2)
    if args.x_xor_y:   write_csv(args.x_csv, 'xor',   args.y_csv, rows1 ^ rows2)
    if args.x_minus_y: write_csv(args.x_csv, 'minus', args.y_csv, rows1 - rows2)
    if args.y_minus_x: write_csv(args.y_csv, 'minus', args.x_csv, rows2 - rows1)

    if args.open or not args.quit and ask(f'Open 2 input files and {len(files)-2} output '
        f'file{"s"*(len(files)>3)} for check and print or Quit? (o=open, q=quit) --> ', 'oq') == 'o':
        popen(' & '.join(f'xdg-open {file!r}' for file in files))

def main():
    try:
        simplefilter('ignore')
        venncsv(argv)
    except KeyboardInterrupt:
        print()

if __name__ == '__main__':
    main()


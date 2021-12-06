import argparse, sys
from os.path import exists

def parse():
    parser = argparse.ArgumentParser(description="""
        Single test case checker for competitive programming.
        Defaults to diff checker, but token and epsilon checkers are available.
    """)

    parser.add_argument('input', help='input file')
    parser.add_argument('user_output', help='user output file')
    parser.add_argument('judge_output', help='judge output file')

    parser.add_argument('-v', '--verbose',
            help='include detailed diagnostics', action='store_true')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-t', '--tok',
            help='use token checker', action='store_true')
    group.add_argument('-e', '--eps', type=float,
            help='use epsilon checker')

    args = parser.parse_args()
    _validate(args)

    return args

def _validate(args):
    try:
        inp, user_out, judge_out = args.input, args.user_output, args.judge_output
    except ValueError:
        print('Internal error parsing input')
        return False

    missingFiles = []
    if not exists(inp):
        missingFiles.append('input')
    if not exists(user_out):
        missingFiles.append('user_output')
    if not exists(judge_out):
        missingFiles.append('judge_output')

    if missingFiles:
        print('Error parsing input files')
        print('The following files are missing or invalid:')
        for f in missingFiles:
           print('\t' + f)

        sys.exit(1)

import argparse
from pathlib import Path
from codescan.scan import full_scan, git_scan
from codescan.print import print_table_format, error, warning, success


def get_parser():
    parser = argparse.ArgumentParser(
        description='Scan Codes for Security Leaks',
        epilog="Enjoy the Program!",
        allow_abbrev=False
    )

    parser.add_argument('-f', '--full', action='store_true',
                        help="Full Scan. Default to git changes of current directory if not specified")

    parser.add_argument('-d', '--dir', action='store', type=str,
                        help="Scan Directory. Default to current directory")

    parser.add_argument('-i', '--ignore', action='store', type=str,
                        help="Ignore File. Specify the file contains the list of files excluded in the codescan")

    return parser


def get_command_arguments():
    parser = get_parser()
    args = parser.parse_args()

    if args.full and args.ignore is None:
        parser.error('-i, --ignore is required when using -f, --full')

    if args.full:
        if args.dir:
            return 'FULL', Path(args.dir), args.ignore
        else:
            return 'FULL', Path(""), args.ignore
    else:
        return 'GIT', Path(""), ".gitignore"


if __name__ == "__main__":

    args = get_command_arguments()

    if args[0] == "FULL":
        results = full_scan(args[1], args[2])
        if len(results) == 0:
            success("Yey! No Leaks Found!")
        else:
            error("Opps! Leaks Found")
            print_table_format(results)

    if args[0] == 'GIT':
        results = git_scan()
        if len(results) == 0:
            success("Yey! No Leaks Found!")
        else:
            error("Opps! Leaks Found")
            print_table_format(results)

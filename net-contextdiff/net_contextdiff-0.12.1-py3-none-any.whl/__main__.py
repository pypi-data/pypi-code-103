# net_contextdiff.__main__


# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>
#
# This script compares Cisco IOS configuration files and outputs a
# configuration file which will convert the former into the latter.



from net_contextdiff import __version__

import argparse
import re
import sys

from deepops import deepmerge
import yaml

from .ios import CiscoIOSConfig, CiscoIOSDiffConfig



# --- constants ---



# PLATFORMS = dict
#
# This dictionary specifies the available platforms available to compare
# configurations in.  The dictionary is keyed on the user-specified platform
# name and specifies two values in a tuple, giving the object classes to be
# used for that platform: the first is the parser an the second is the
# difference comparator.

PLATFORMS = {
    "ios": (CiscoIOSConfig, CiscoIOSDiffConfig)
}



# --- functions ---



def diffconfig(diff, devicename, from_filename, to_filename, output_filename,
               no_output, dump_rules, debug_parser, debug_convert):

    """This function compares the 'from' and 'to' configurations for
    the specified device and writes a difference configuration file
    (one that transforms the configuration of a running device from the
    'from' to the 'to' state).

    The filenames for the configuration files, as well as the output
    are taken from the arguments parsed above and stored in global
    variables used directly by this function.

    The function returns True iff the parsing and comparison succeeded.
    Most problems result in the function aborting with an exception,
    but some minor warnings may be ignored and the program continue
    with devices.

    Keyword arguments:

    diff -- the DiffConfig object to do the convert the configuration

    devicename -- the name of the device being converted, or None if
    it's not known

    from_filename -- filename of the source configuration

    to_filename -- filename of the target configuration

    output_filename -- name of the file to write the conversion
    configuration to or None for standard output

    no_output -- a boolean set to True iff no output file is to be
    written

    dump_rules, debug_parser, debug_convert -- the equivalent
    variables to command line arguments
    """


    # reset the rules list for this conversion - this is the same
    # list each time, except the devicename changes and may cause
    # some of the rules to change

    diff.init_rules_active()
    diff.add_rules_active(rule_specs, devicename)

    if dump_rules >= 2:
        num = 0
        for spec, tree in diff.get_rules():
            print(">> rule num: %d spec: %s" % (num, spec))
            print(yaml.dump(tree, default_flow_style=False)
                        if tree else "<none>\n", sep="\n")

            num += 1


    # read in the 'from' and 'to' configurations

    from_cfg = config_parser_class(filename=from_filename, debug=debug_parser)

    to_cfg = (config_parser_class(filename=to_filename, debug=debug_parser)
                  if to_filename else None)


    # find the differences

    diffs, diffs_tree = diff.convert(from_cfg, to_cfg)


    # if output is suppressed, just stop with success here

    if no_output:
        return diffs_tree


    # write the differences to a file or standard output

    if output_filename:
        if debug_convert:
            print("debug: writing to output file:", output_filename)

        with open(output_filename, "w") as output_file:
            if diffs:
                print(diffs, file=output_file)

    else:
        if debug_convert:
            print("debug: writing to standard output")

        if diffs:
            print(diffs)


    return diffs_tree



# --- command line arguments ---



# create the parser and add in the available command line options

parser = argparse.ArgumentParser(
    # override the program name as running this as a __main__ inside a module
    # directory will use '__main__' by default - this name isn't necessarily
    # correct, but it looks better than that
    prog="net-contextdiff",

    # we want the epilog help output to be printed as it and not reformatted or
    # line wrapped
    formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument(
    "-r", "--rules-tree-filename",
    metavar="FILENAME",
    help="read rules data from a YAML file (assumed to be an "
         "'excludes' list by default - see -s option)")

parser.add_argument(
    "-s", "--rule-spec",
    metavar="PATH",
    action="append",
    default=[],
    help="add a rule to the rules list; rules are in the form '!path' "
         "and processed in order: '!' excludes the specified items and "
         "omitting it includes ONLY the specified items; the 'path' is "
         "a dictionary path, with keys separated by colons; the path "
         "is into the file read with -r; default can be viewed with "
         "-R option)")

parser.add_argument(
    "-e", "--explain",
    action="store_true",
    help="explain which converter paths match a configuration change")

parser.add_argument(
    "-q", "--quiet",
    action="store_true",
    help="when generating configuration for multiple devices, don't "
         "print the name of each device, as it's generated")

parser.add_argument(
    "-O", "--no-output",
    action="store_true",
    help="do not write changes output file - used to test parsing, "
         "exclude and conversion process")

parser.add_argument(
    "-R", "--dump-rules",
    action="count",
    default=0,
    help="dump the tree of items to be included and excluded from the "
         "comparisons, based on the rules (multiple levels increase "
         "verbosity up to a maximum of 2)")

parser.add_argument(
    "-C", "--dump-config",
    action="store_true",
    help="dump the configuration dictionary after parsing")

parser.add_argument(
    "-D", "--dump-diff",
    action="store_true",
    help="dump the difference (removes and updates) between the from "
         "and to configurations")

parser.add_argument(
    "-T", "--dump-diff-tree",
    action="store_true",
    help="dump the differences across all compared files as a YAML "
         "tree - this is useful for using in an exclude file")

parser.add_argument(
    "-P", "--debug-parser",
    action="count",
    default=0,
    help="enable debugging of contextual parsing (multiple levels "
         "increase verbosity up to a maxmimum of 2)")

parser.add_argument(
    "-V", "--debug-convert",
    action="count",
    default=0,
    help="enable debugging of the difference converstion action "
         "processing (multiple levels increase verbosity up to a "
         "maximum of 2)")

parser.add_argument(
    "platform",
    choices=PLATFORMS,
    help="platform used for configuration files")

parser.add_argument(
    "from_filename",
    metavar="from",
    help="initial ('from') configuration file; '%%' can be used to "
         "substitute in the name of the device into the filename")

parser.add_argument(
    "to_filename",
    nargs="?",
    default=None,
    metavar="to",
    help="destination ('to') configuration file; '%%' can be used to "
         "substitute in the name of the device into the filename; if "
         "omitted just parse the file and assume 'debug' mode")

parser.add_argument(
    "output_filename",
    nargs="?",
    metavar="output",
    help="write differences configuration to named file instead of "
         "stdout; '%%' can be used to substitute in the name of the "
         "device into the filename")

parser.add_argument(
    "devicenames",
    metavar="devicename",
    nargs="*",
    help="name(s) of the device(s) to calculate differences in the "
         "configuration for")

parser.add_argument(
    "-v", "--version",
    action="version",
    version=("%(prog)s " + __version__))


# parse the supplied command line against these options, storing the results

args = parser.parse_args()

config_parser_class, config_diff_class = PLATFORMS[args.platform]

rules_tree_filename = args.rules_tree_filename
rule_specs = args.rule_spec
explain = args.explain
quiet = args.quiet
no_output = args.no_output
dump_rules = args.dump_rules
dump_config = args.dump_config
dump_diff = args.dump_diff
dump_diff_tree = args.dump_diff_tree
debug_parser = args.debug_parser
debug_convert = args.debug_convert
from_filename = args.from_filename
to_filename = args.to_filename
output_filename = args.output_filename
devicenames = args.devicenames


# if the rule specifications were not specified, assume this set by
# default (we can't add_argument(default=...) option because the
# 'action="append"' option just adds user-specified items to it)

if not rule_specs:
    rule_specs = [
        "!rules:exclude:ALL",
        "!rules:exclude:%",
        "rules:include:ALL",
        "rules:include:%",
    ]


# check a couple of nonsensical configurations aren't being use related
# to multiple devices

if not len(devicenames):
    if from_filename.find("%") != -1:
        print("error: no device names specified, so operating on a single "
              "file, yet 'from' filename has '%' character",
              file=sys.stderr)

        exit(1)


    if to_filename and (to_filename.find("%") != -1):
        print("error: no device names specified, so operating on a single "
              "file, yet 'to' filename has '%' character",
              file=sys.stderr)

        exit(1)


    if output_filename and (output_filename.find("%") != -1):
        print("error: no device names specified, so operating on a single "
              "file, yet 'output' filename has '%' character",
              file=sys.stderr)

        exit(1)


elif len(devicenames) > 1:
    if from_filename.find("%") == -1:
        print("warning: multiple device names specified but 'from' filename "
              "does not contain '%' - same file will be read",
              file=sys.stderr)

    if to_filename and (to_filename.find("%") == -1):
        print("warning: multiple device names specified but 'to' filename "
              "does not contain '%' - same file will be read",
              file=sys.stderr)


    if not output_filename:
        print("warning: multiple device names specified but outputting to "
              "standard output - all configurations will be concatenated",
              file=sys.stderr)

    elif output_filename.find("%") == -1:
        print("error: multiple device names specified but 'output' filename "
              "does not contain '%' - same file would be overwritten",
              file=sys.stderr)

        exit(1)



# --- setup ---



# create the diff object once at the start

diff = config_diff_class(explain, dump_config, dump_diff, debug_convert)


# if a rules tree file was specified, read that in

if rules_tree_filename:
    diff.add_rules_tree_file(rules_tree_filename)


# dump the rule tree, if debugging enabled for it (this will include any
# rules included by default, in the class)

if dump_rules >= 1:
    print(">> rule tree:")
    print(yaml.dump(diff.get_rules_tree(), default_flow_style=False))
    print(">> rule specs:")
    for spec in rule_specs:
        print("->", spec)

    print()



# --- compare ---



# if we have a list of device names (even just one), we iterate through
# them, else we just process the one file we've been given

if devicenames:
    # initialise the tree of aggregated differences across al the
    # compared configuration files

    all_diffs_tree = {}


    for devicename in devicenames:
        if not quiet:
            print(devicename)


        # do the actual conversion

        diffs_tree = diffconfig(
                      diff, devicename,
                      from_filename.replace("%", devicename),
                      to_filename.replace("%", devicename),
                      output_filename.replace("%", devicename),
                      no_output, dump_rules, debug_parser,
                      debug_convert)


        # add the differences in this conversion to the aggregate tree

        deepmerge(all_diffs_tree, diffs_tree)


else:
    all_diffs_tree = diffconfig(
        diff, None, from_filename, to_filename, output_filename, no_output,
        dump_rules, debug_parser, debug_convert)


# if the option to enable dumping of the differences tree is enabled, do
# that

if dump_diff_tree:
    print("=> differences tree:")
    print(yaml.dump(all_diffs_tree, default_flow_style=False))


exit(0)

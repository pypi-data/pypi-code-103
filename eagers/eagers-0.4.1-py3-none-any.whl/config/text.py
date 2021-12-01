"""Configuration variables for various types of text.
"""


# NAMES
# General
# Prefix for runtime HDF5 files.
RUNTIME_HDF5_FILE_PREFIX = "runtime_"

# CSV result file
# Separator between project name and table name.
CSV_RESULT_SEP = "--"

# Acceptable True/False strings.  Use str.lower() to compare.
ACCEPTABLE_TRUE_STR = ("true", "1", "y")
ACCEPTABLE_FALSE_STR = ("false", "0", "n")
def parse_bool_str(s):
    lower = s.lower()
    if lower in ACCEPTABLE_TRUE_STR:
        return True
    elif lower in ACCEPTABLE_FALSE_STR:
        return False
    else:
        raise ValueError(f"Unrecognized boolean value {s!r}")

import copy
import datetime
import logging
import os
import sys

import ciso8601
import numpy as np
import pandas as pd
import pytz


logger = logging.getLogger('tsdataformat')


class Tsdata(object):
    """
    Tsdata is a class to manage Tsdata metadata and validate data lines.
    """
    header_size = 7  # lines in header
    na = "NA" # no data string
    sep = "\t" # field separator character

    def __init__(self):
        self.metadata = {
            "FileType": "",
            "Project": "",
            "FileDescription": "",
            "Comments": [],
            "Types": [],
            "Units": [],
            "Headers": []
        }
        self.lasttime = datetime.datetime.min.replace(tzinfo=pytz.utc)

    def set_metadata_from_text(self, metadata):
        """
        Sets metadata by parsing header lines as a single string.

        Raises a ValueError exception on metadata errors.
        """
        self.metadata = self._parse_header(metadata)
        self.column_count = len(self.metadata["Headers"])
        self.validate_metadata()
    
    def set_columns(self, new_headers):
        """Reorder and subset existing columns in metadata."""
        if not self.metadata:
            raise ValueError("no existing metadata found")
        if len(new_headers) < 2:
            raise ValueError("there must be at least 2 columns")
        if len(set(new_headers)) != len(new_headers):
            raise ValueError("duplicate column detected")
        if new_headers[0] != "time":
            raise ValueError("the first column must be time")
        
        oldmeta = copy.deepcopy(self.metadata)
        self.metadata["Comments"] = []
        self.metadata["Types"] = []
        self.metadata["Units"] = []
        self.metadata["Headers"] = []
        for _, nh in enumerate(new_headers):
            try:
                i = oldmeta["Headers"].index(nh)
            except ValueError:
                raise ValueError("{} is not a valid column".format(nh))
            self.metadata["Comments"].append(oldmeta["Comments"][i])
            self.metadata["Types"].append(oldmeta["Types"][i])
            self.metadata["Units"].append(oldmeta["Units"][i])
            self.metadata["Headers"].append(oldmeta["Headers"][i])

    @property
    def header(self):
        """Header text with no final newline."""
        if not self.metadata:
            return ""
        return os.linesep.join([
            self.metadata["FileType"],
            self.metadata["Project"],
            self.metadata["FileDescription"],
            self.sep.join(self.metadata["Comments"]),
            self.sep.join(self.metadata["Types"]),
            self.sep.join(self.metadata["Units"]),
            self.sep.join(self.metadata["Headers"])
        ])

    def _parse_header(self, metadata):
        """
        Parses header text and return a  dictionary.
        
        Raises ValueError for any errors encountered.
        """
        lines = metadata.rstrip().splitlines()
        if len(lines) != self.header_size:
            raise ValueError("expected {} header lines, found {}".format(self.header_size, len(lines)))
        # Prevent a common problem and remove any trailing whitespace
        lines = [line.rstrip() for line in lines]
        d = {
            "FileType": lines[0],
            "Project": lines[1],
            "FileDescription": lines[2],
            "Comments": [s.strip() for s in lines[3].split(self.sep)],
            "Types": [s.strip() for s in lines[4].split(self.sep)],
            "Units": [s.strip() for s in lines[5].split(self.sep)],
            "Headers": [s.strip() for s in lines[6].split(self.sep)]
        }
        return d


    def validate_metadata(self):
        keys_present = set(self.metadata.keys())
        keys_required = set([
            "FileType", "Project", "FileDescription", "Comments", "Types",
            "Units", "Headers"
        ])
        diff = keys_required.difference(keys_present)
        if len(diff) > 0:
            raise ValueError("metadata missing required entries: {}".format(", ".join(diff)))

        if self.metadata["FileType"] == "":
            raise ValueError("empty FileType line")

        if self.metadata["Project"] == "":
            raise ValueError("empty Project line")

        colcount = 0 # keep track of number of columns we've seen
        # Column comments may be blank so allow 0 columns
        if len(self.metadata["Comments"]) != 0:
            colcount = len(self.metadata["Comments"])
            for i, v in enumerate(self.metadata["Comments"]):
                if v == "":
                    raise ValueError("empty Comment in column {}".format(i+1))

        if len(self.metadata["Types"]) == 0:
            raise ValueError("empty Types line")
        if colcount > 0 and len(self.metadata["Types"]) != colcount:
            raise ValueError("inconsistent Types column count")
        type_diff = set(self.metadata["Types"]).difference(set(_typelu.keys()))
        if len(type_diff) > 0:
            raise ValueError("invalid types: {}".format(", ".join(type_diff)))
        colcount = len(self.metadata["Types"])

        if len(self.metadata["Units"]) == 0:
            raise ValueError("empty Units line")
        if len(self.metadata["Units"]) != colcount:
            raise ValueError("inconsistent Units column count")
        for i, v in enumerate(self.metadata["Units"]):
                if v == "":
                    raise ValueError("empty Unit in column {}".format(i+1))

        if len(self.metadata["Headers"]) == 0:
            raise ValueError("empty Headers line")
        if len(self.metadata["Headers"]) != colcount:
            raise ValueError("inconsistent Headers column count")
        if self.metadata["Headers"][0] != "time":
            raise ValueError("first Headers column should be 'time'")
        for i, v in enumerate(self.metadata["Headers"]):
                if v == "":
                    raise ValueError("empty Header in column {}".format(i+1))

        if colcount < 2: # must have at least a time column and one data column
            raise ValueError("no data columns after time")

    def validate_line(self, line):
        """
        Validates one line of Tsdata file based on loaded metadata and checks
        that this line is in ascending order relative to the previous line seen.

        Returns a list of the original fields as strings.

        Raises ValueError if an error is detected.
        """
        if not self.metadata:
            raise ValueError("metadata must be set before calling validate_line")

        fields = [f.strip() for f in line.rstrip().split(self.sep)]

        valid = []
        if len(fields) != len(self.metadata["Types"]):
            raise ValueError("expected {} fields, found {}".format(self.column_count, len(fields)))
        for i, t in enumerate(self.metadata["Types"]):
            valid.append(_typelu[t](fields[i]))
        # Don't check for time order for now, may reinstate later
        # if self.lasttime > valid[0]:
        #     self.lasttime = valid[0]
        #     raise ValueError("timestamp {} not in ascending order".format(fields[0]))
        self.lasttime = valid[0]

        return fields


def tsdata_to_csv(in_file, out_file):
    """
    Writes Tsdata file in in_file to out_file.

    in_file and out_file should be file-like objects. Metadata will be
    loaded from in_file, overwriting any metadata already in this object.

    Raises a ValueError exception for validation errors.
    """
    ts = Tsdata()
    ts.set_metadata_from_text(read_header(in_file))
    out_file.write(','.join(ts.metadata["Headers"]) + os.linesep)
    linenum = ts.header_size + 1
    for line in in_file:
        try:
            outputs = ts.validate_line(line)
        except ValueError as e:
            msg = "line {}: {}".format(linenum, e)
            logger.warning(msg)
        else:
            out_file.write(",".join(outputs) + os.linesep)
        linenum += 1


def read_header(in_file):
    """
    Reads header lines from a file-like object.
    
    Returns a single string with header lines joined by os.linesep.
    """
    lines = []
    for _ in range(Tsdata.header_size):
        lines.append(in_file.readline().rstrip())
    return os.linesep.join(lines)


def read_tsdata(in_file, convert=None):
    """
    Reads a Tsdata file as a Pandas DataFrame sorted ascending by time.

    If convert is "all" or "time", time fields will attempt to be converted to
    datetime objects. Any values not able to be parsed will be represented as
    NaT.
    
    If convert is "all" then in addition to this, other columns will be
    converted to their types specified in the file header. The one exception is
    boolean columns will be treated as having type category. Any values failing
    conversion will be set to pd.NaN.

    Raises ValueError if errors are encountered in metadata header.
    """
    if convert and convert not in ["all", "time"]:
        raise ValueError("convert must be None, False, '', 'all', or 'time'")

    ts = Tsdata()
    ts.set_metadata_from_text(read_header(in_file))

    # Read CSV as dataframe but treat everything as an object for now
    df = pd.read_csv(
        in_file,
        sep=Tsdata.sep,
        header=None,
        names=ts.metadata["Headers"],
        dtype=object,
        keep_default_na=False
    )
    if convert == "all" or convert == "time":
        df["time"] = pd.to_datetime(df["time"].str.strip(), errors="coerce", utc=True,
                                    infer_datetime_format=True)

    if convert == "all":
        # Convert columns to their correct types, coercing any values which
        # can't be converted to the correct null value. Note that this
        # is more permissive than the strict Tsdata format as more than just
        # "NA" will be considered NULL. Because of numpy/pandas lack of missing
        # data support for booleans and to simplify potential
        # grouping/resampling, booleans will be treated as categorical string
        # data.
        for (col, type_) in zip(ts.metadata["Headers"], ts.metadata["Types"]):
            if type_ == "boolean":
                cat = pd.api.types.CategoricalDtype(categories=["TRUE", "FALSE", "NA"])
                df[col] = df[col].str.strip().astype(cat)
            elif type_ == "float":
                df[col] = pd.to_numeric(df[col].str.strip(), errors="coerce").astype("float64")
            elif type_ == "integer":
                df[col] = pd.to_numeric(df[col].str.strip(), errors="coerce").astype("Int64")
            elif type_ == "category":
                df[col] = df[col].str.strip().astype("category")

    return df


def resample_tsdata(in_file, out_file, freq, dropna=False, exclude_categories=None):
    """
    Resamples Tsdata by time, categories, and booleans.

    in_file and out_file should be file-like objects. Numeric data in each group
    is summarized by the mean. freq should represent a period of time, e.g.
    3min. See the pandas URL for offset-aliases below for possible values and
    meanings. dropna controls whether to remove rows where all numeric values
    are NA after grouping.

    https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
    https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#resampling
    """
    if exclude_categories is None:
        exclude_categories = []

    ts = Tsdata()
    ts.set_metadata_from_text(read_header(in_file))
    in_file.seek(0)
    df = read_tsdata(in_file, convert="all")
    df = df.set_index("time")

    # Note columns to group by in addition to time (category/boolean)
    togroup = []
    for (h, t) in zip(ts.metadata["Headers"], ts.metadata["Types"]):
        if (t == "category" or t == "boolean") and (h not in exclude_categories):
            togroup.append(h)
    
    # Prepare output columns in original order, everything but text columns
    outcolumns = []
    for (h, t) in zip(ts.metadata["Headers"], ts.metadata["Types"]):
        if t != "text" and (h not in exclude_categories):
            outcolumns.append(h)

    # Group by time and maybe categories/booleans with a new frequency, fill
    # gaps with NaN.
    grouped = df.groupby([pd.Grouper(freq=freq)] + togroup)
    # Summarize
    grouped = grouped.mean()
    # Remove rows that were created as empty gaps during binning. This may also
    # remove any bins where original numeric values were all NA.
    if dropna:
        grouped = grouped.dropna(how="all")

    df = df.sort_index()

    # Output
    df = grouped.reset_index()
    df["time"] = df["time"].apply(lambda dt: dt.isoformat())
    ts.set_columns(outcolumns)
    out_file.write(ts.header + os.linesep)
    df[outcolumns].to_csv(out_file, sep=Tsdata.sep, na_rep="NA", header=False,
                          index=False)


def clean_tsdata(in_file, out_file, csv=False):
    """
    Cleans Tsdata in in_file writing to out_file.

    in_file and out_file should be file-like objects. This function discards
    lines with bad timestamps, converts bad values to the default Null string
    "NA", fills blanks with "NA" where necessary, and sorts ascending by time.

    Outputs CSV file if csv is True.
    """
    ts = Tsdata()
    ts.set_metadata_from_text(read_header(in_file))
    in_file.seek(0)
    df = read_tsdata(in_file)
    in_file.seek(0)
    df2 = read_tsdata(in_file, convert="all")


    # Sanity check that these dataframes are same length and can use the same
    # index.
    assert len(df) == len(df2)

    # Sort by ascending time and remove bad times.
    df2 = df2.sort_values(by=["time"])
    df = df.loc[df2.index] # sort df by new df2 order
    assert len(df) == len(df2) # sanity check again
    good_times = pd.notna(df2["time"])
    df = df[good_times]
    df2 = df2[good_times]

    # Find NaNs in df2, replace same cells in df with "NA".
    df = df.mask(df2.isna(), "NA")

    # Strip leading and trailing whitespace for all string cells, which should
    # be all of them here.
    df = df.applymap(lambda x: x.strip() if type(x) == str else x)
    if not csv:
        out_file.write(ts.header + os.linesep)
        df.to_csv(out_file, sep=Tsdata.sep, header=False, index=False)
    else:
        df.to_csv(out_file, sep=",", header=True, index=False)


def _float_check(v):
    if v == Tsdata.na:
        return v
    _ = float(v)
    return v


def _int_check(v):
    if v == Tsdata.na:
        return v
    _ = int(v)
    return v


def _text_check(v):
    return v


def _time_check(v):
    # Return datetime.datetime here to avoid parsing twice in places
    return ciso8601.parse_rfc3339(v)


def _bool_check(v):
    if v == "TRUE" or v == "FALSE" or v == Tsdata.na:
        return v
    raise ValueError("bad boolean value {}".format(v))


_typelu = {
    "float": _float_check,
    "integer": _int_check,
    "text": _text_check,
    "time": _time_check,
    "category": _text_check,
    "boolean": _bool_check
}

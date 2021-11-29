"""Reads typical meteorlogical year (TMY) weather files.

EPW file data field descriptions:
https://bigladdersoftware.com/epx/docs/8-3/auxiliary-programs/energyplus-weather-file-epw-data-dictionary.html#data-field-descriptions
Especially important to note are the descriptions for hour and minute
data fields.
"""

import csv
import datetime as dt
import pathlib

import numpy as np

from building_plus.config.weather_file import (
    EPW_HEADERS, EPW_INTEREST, EPW_TIMESTAMP, CSV_INTEREST, CSV_TIMESTAMP,
    WTS_ATTR_MAP,
)


NON_LEAP_YEAR = 2017
HR_SECONDS = 3600
MIN_SECONDS = 60


def read_weather_file(file, designation):
    """Read weather file to a dictionary.

    Headers that are read are specified in config.

    Positional arguments:
    file - (str, path-like) Path to weather file.
    designation - (str) Weather data designation. Can be 'tmy' or
        'continuous'.
    """
    # Ensure input is Path object.
    file = pathlib.Path(file)
    # File type-specific parameters.
    if file.suffix == '.epw':
        start_row = 8
        headers = EPW_HEADERS
        headers_of_interest = EPW_INTEREST
    elif file.suffix == '.csv':
        start_row = 2
        headers = get_csv_headers(file)
        headers_of_interest = CSV_INTEREST
    # Initialize result dictionary.
    weather = {WTS_ATTR_MAP[k]: [] for k in headers_of_interest}
    weather['timestamp'] = []
    weather['designation'] = designation
    # Read file.
    with open(file, newline='') as csv_file:
        reader = csv.DictReader(csv_file, fieldnames=headers)
        # Skip preamble rows.
        [next(reader) for i in range(start_row)]
        # Now for the data!
        for row in reader:
            weather['timestamp'].append(read_timestamp(row, file.suffix))
            for h in headers_of_interest:
                value = convert_units(h, row[h])
                weather[WTS_ATTR_MAP[h]].append(value)
    return weather


def get_csv_headers(file):
    """Return the headers of a CSV weather file.

    Positional arguments:
    file - (pathlib.Path) CSV weather file.
    """
    with open(file, newline='') as wf:
        reader = csv.reader(wf)
        # Headers are found on the second line.
        next(reader)
        headers = next(reader)
    return headers


def convert_units(name, value):
    """Convert units of given value as necessary.

    Positional arguments:
    name - (str) Name of value to convert.
    value - (str, int, float) Value to be converted.
    """
    if '(mbar)' in name:
        # Convert mbar to Pa.
        return float(value) * 100
    else:
        value = float(value)
        return value


def read_timestamp(row, file_suffix):
    """Read timestamp information based on the given file suffix.

    Positional arguments:
    row - (dict) Row from DictReader.
    file_suffix - (str) File suffix.
    """
    if file_suffix == '.epw':
        y, m, d, hr, mn = map(int, [
            row['Year'], row['Month'], row['Day'], row['Hour'], row['Minute']])
        # EPW files: Hour 1 is 00:01 - 01:00, so that:
        #   hour 01, minute 01 -> 00:01
        #   hour 01, minute 60 -> 01:00
        # See link to EnergyPlus documentation at top of file.
        # Decrement hour by one for Python datetime compatibility.
        hr -= 1
    elif file_suffix == '.csv':
        m, d, y = map(int, row['Date (MM/DD/YYYY)'].split('/'))
        # Get first two elements of list returned by split, for cases
        # where the second value (or further) is included.
        hr, mn = map(int, row['Time (HH:MM)'].split(':')[:2])
    else:
        raise ValueError('{!r} is not a recognized suffix.'
            .format(file_suffix))
    # Account for possible overflow.
    # 00:60 overflows to 01:00.
    # 24:00 overflows to 00:00 on the following day.
    # Jan. 31st, 24:00 overflows to Feb. 1st, 00:00.
    seconds = hr * HR_SECONDS + mn * MIN_SECONDS
    return dt.datetime(NON_LEAP_YEAR, m, d) + dt.timedelta(seconds=seconds)

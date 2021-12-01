"""Defines TimeSeriesDataSet class, which establishes common behavior
for time series data sets, and its subclasses.

Classes:
TimeSeriesDataSet
NodeDataTimeSeries
WeatherTimeSeries
OtherTimeSeries
"""

import calendar
from contextlib import contextmanager
import datetime as dt
from functools import wraps

import numpy as np
from numpy.lib import recfunctions as rfn
import tables as tb

from eagers.class_definition.data_constructed import DataConstructed
from eagers.config.dataset import DATASET_TYPES
from eagers.config.path_spec import HDF5_SUFFIX, USER_DIR_HDF5_DATASETS
from eagers.basic.file_handling import ensure_suffix
from eagers.basic.hdf5 import h5file_context, DatetimeFloatConverter as DFC


class TimeSeriesDataSet(DataConstructed):
    """Holds time series data set file information for on-demand access
    to its data. The two most useful methods are read() and
    read_timestamp_range().
    """

    def __init__(self, filename, dset_type):
        """TimeSeriesDataSet objects should not be instantiated
        directly.
        """
        assert filename is not None, "filename cannot be None."
        assert dset_type in DATASET_TYPES, \
            f"{dset_type!r} not an acceptable data set type."
        self.filename = filename
        self.dset_type = dset_type

    def __repr__(self):
        return f"<{type(self).__name__}(filename={self.filename!r})>"

    @property
    def filepath(self):
        return (USER_DIR_HDF5_DATASETS
            / self.dset_type
            / ensure_suffix(self.filename, HDF5_SUFFIX))

    @property
    def tablenames(self):
        with self.file_context() as h5f:
            root = h5f.root
            return list(c for c in root._v_children
                if isinstance(getattr(root, c), tb.table.Table))

    def colnames(self, tablename):
        """Reads the column names from the specified HDF5 table."""
        with self.table_context(tablename) as table:
            return table.colnames

    @classmethod
    def from_file(cls, name, *args, **kwargs):
        """Provides an implementation for DataConstructed.from_file().
        """
        return cls(name, *args, **kwargs)

    @contextmanager
    def file_context(self):
        """Exposes an HDF5 file while open."""
        with h5file_context(self.filepath, mode='r') as h5f:
            yield h5f

    @contextmanager
    def table_context(self, name):
        """Exposes an HDF5 table while open."""
        with self.file_context() as h5f:
            table = getattr(h5f.root, name)
            yield table

    @wraps(tb.Table.read)
    def read(self, tablename, *args, **kwargs):
        """Reference PyTables.Table.read() for documentation. The only
        difference is that this function also accepts a tablename
        argument before any others.
        """
        with self.table_context(tablename) as table:
            return table.read(*args, **kwargs)

    @classmethod
    def _read_timestamp_range_from_table(
        cls,
        table,
        start=None,
        stop=None,
        *,
        field=None,
        inclusive=True,
        return_indices=False,
    ):
        """Basic version of read_timestamp_range where a Table object is
        provided. This exists for internal use, to avoid having to close
        and re-open the file in some cases.
        """
        col = 'timestamp'
        # Check input integrity.
        assert start <= stop, "Datetime range must be in chronological order."
        # Create query.
        upper_inequality = '<=' if inclusive else '<'
        query_condition = (
            f"({col} >= {start}) "
            f"& ({col} {upper_inequality} {stop})"
        )
        # Since no variables from the current namespace are used, set
        # condvars to [].
        if return_indices:
            # 2 return values.
            indices = table.get_where_list(query_condition, condvars=[])
            return (
                table.read(indices[0], indices[-1] + 1, field=field),
                indices,
            )
        else:
            # 1 return value.
            return table.read_where(query_condition, condvars=[], field=field)

    @classmethod
    def _handle_start_stop_args(cls, table, start, stop, typecast=None):
        """Returns given start and stop dates, ensuring they are not
        None.

        Positional arguments:
        table - (PyTables.Table) Table to read from.
        start - (datetime, float, or None) Start date.
        stop - (datetime, float, or None) Stop date.

        Keyword arguments:
        typecast - (str) (Default: None) Type to cast to.
        """
        # Handle unspecified bounds.
        if start is None:
            start = table.read(0, 1, field="timestamp")[0]
        if stop is None:
            stop = table.read(-1, field="timestamp")[0]
        # Handle type casting.
        if typecast == "datetime":
            if not isinstance(start, dt.datetime):
                start = DFC.f2d_sgl2sgl(start)
            if not isinstance(stop, dt.datetime):
                stop = DFC.f2d_sgl2sgl(stop)
        elif typecast == "float":
            if not isinstance(start, float):
                start = DFC.d2f_sgl2sgl(start)
            if not isinstance(stop, float):
                stop = DFC.d2f_sgl2sgl(stop)
        return start, stop

    def read_timestamp_range(
        self,
        tablename,
        start=None,
        stop=None,
        *,
        field=None,
        inclusive=True,
        return_indices=False,
    ) -> np.recarray:
        """Return NumPy record array of the rows corresponding to the
        specified timestamp bounds (inclusive). If the given bounds
        don't exactly match time stamps in the file, the closest values
        within the given bounds are returned.

        Positional arguments:
        tablename - (str) The name of the Table to read from.

        Keyword arguments:
        start - (datetime or float) (Default: None) Lower bound of
            timestamp range. If None, read from the beginning of the
            data set.
        stop - (datetime or float) (Default: None) Upper bound of
            timestamp range. If None, read to the end of the data set.
            If this value is beyond the end of the data set, this method
            will read to the end.
        field - (str) (Default: None) Column name of data to be
            returned.
        inclusive - (bool) (Default: True) Whether upper bound
            inequality is inclusive (<= as opposed to <).
        return_indices - (bool) (Default: False) If set to True, the
            indices of the returned rows will also be returned. When
            used in conjunction with read(), this can be useful for
            getting points on either side of timestamp ranges.
        """
        with self.table_context(tablename) as table:
            start, stop = self._handle_start_stop_args(
                table, start, stop, typecast="float"
            )
            return self._read_timestamp_range_from_table(
                table,
                start,
                stop,
                field=field,
                inclusive=inclusive,
                return_indices=return_indices,
            )

    def read_timestamp_range_extend_missing(
        self,
        tablename,
        start=None,
        stop=None,
        *,
        field=None,
    ):
        """Same as read_timestamp_range(), but extends data to fill missing points if
        needed. This is not applicable to TMY weather data. Here, there are no
        `inclusive` (it's always True) or `return_indices` options.
        """
        with self.table_context(tablename) as table:
            start, stop = self._handle_start_stop_args(
                table, start, stop, typecast="float"
            )
            data = self._read_timestamp_range_from_table(
                table,
                start,
                stop,
                field=field,
            )
            timestamp = data["timestamp"]
            if timestamp.size:
                first_timestamp = timestamp[0]
                last_timestamp = timestamp[-1]
            else:
                first_timestamp = table.read(0, 1, field="timestamp")[0]
                last_timestamp = table.read(-1, field="timestamp")[0]
            need_ante_extension = first_timestamp > start
            need_post_extension = last_timestamp < stop
            extension_requirement = need_ante_extension + need_post_extension
            frequency = None
            if extension_requirement:
                assert (
                    extension_requirement < 2
                ), "Can't handle both ante- and post-extension."
                if len(timestamp) > 1:
                    frequency = np.mean(np.diff(timestamp))
                else:
                    frequency = np.diff(table.read(0, 2, field="timestamp"))[0]
        if frequency is not None:
            if need_ante_extension:
                extension_time = first_timestamp - start
            else:
                extension_time = stop - last_timestamp
            assert extension_time >= frequency, (
                f"Need: extension_time >= frequency. Actual: {extension_time} < "
                f"{frequency}"
            )
            secs_in_day = 3600 * 24
            if need_ante_extension:
                new_start = start + secs_in_day
                new_stop = first_timestamp + secs_in_day - frequency
            else:
                new_start = last_timestamp - secs_in_day + frequency
                new_stop = stop - secs_in_day
            extension = self.read_timestamp_range(tablename, new_start, new_stop)
            if need_ante_extension:
                extension["timestamp"] -= secs_in_day
                arrays = [extension, data]
            else:
                extension["timestamp"] += secs_in_day
                arrays = [data, extension]
            data = rfn.stack_arrays(arrays, usemask=False, asrecarray=True)
        return data


class NodeDataTimeSeries(TimeSeriesDataSet):
    def __init__(self, filename):
        super().__init__(filename, 'nodedata')

    def start_dates(self, as_datetime=False):
        """Returns an array of the available start dates for this data
        set.

        Keyword arguments:
        as_datetime - (bool) (Default: False) Whether to return a list
            of datetime objects instead of an array of floats.
        """
        with self.file_context() as h5f:
            floats = getattr(h5f.root, 'available_start_dates').read()
            return DFC.f2d_arr2lst(floats) if as_datetime else floats


class WeatherTimeSeries(TimeSeriesDataSet):
    # tmy: Typical Meteorological Year. Timestamps only for one non-leap
    # year.
    # continuous: Continuous data. Timestamps possibly spanning multiple
    # years.
    _designations = ('tmy', 'continuous')

    def __init__(self, filename):
        super().__init__(filename, 'weather')
        # Check designations.
        self._des = {}
        for tablename in self.tablenames:
            with self.table_context(tablename) as table:
                des = table.attrs.designation
            if des not in self._designations:
                raise ValueError(
                    f"{des!r} in {filename!r} not a recognized designation.\n"
                    f"Acceptable designations: {', '.join(self._designations)}"
                )
            self._des[tablename] = des

    @wraps(TimeSeriesDataSet.read_timestamp_range)
    def read_timestamp_range(
        self, tablename, start=None, stop=None, *args, **kwargs
    ):
        designation = self._des[tablename]
        if designation == 'continuous':
            # Use the default method.
            return super().read_timestamp_range(
                tablename, start, stop, *args, **kwargs
            )
        elif designation == 'tmy':
            with self.table_context(tablename) as table:
                start, stop = self._handle_start_stop_args(
                    table, start, stop, typecast="datetime"
                )
                return self._tmy_read_timestamp_range(
                    table, start, stop, *args, **kwargs
                )

    def table_designation(self, tablename):
        """The weather file designation of the table with the given
        name.
        """
        try:
            return self._des[tablename]
        except KeyError:
            raise ValueError(
                f"Couldn't find a designation for table {tablename!r}"
            )

    def _tmy_read_timestamp_range(
        self,
        table,
        start,
        stop,
        *args,
        return_indices=False,
        **kwargs,
    ):
        """Core logic for read_timestamp_range specific to TMY-type
        weather files and where a table is provided. This exists for
        internal use, to avoid having to close and re-open the file in
        some cases.

        TMY weather files assume a non-leap year. When the requested
        range includes February 29th, the missing data must be made up
        for. In this case, Feb. 28 data is used in place of Feb. 29.

        Positional and keyword arguments are the same as for
        read_timestamp_range, except for this additional keyword
        argument:
        impose_year - (bool) (Default: True) Indicates whether the
            requested range should be returned with the years of the
            requested datetimes imposed on the data read from the TMY
            file. Otherwise, the timestamps for the returned data will
            all have the year of the TMY file. E.g. if the range from
            2011-4-23 to 2012-7-4 is requested from a file with the TMY
            year 2017 and impose_year is False, the data returned will
            have timestamps from 2017-4-23 to 2017-12-31, then 2017-1-1
            to 2017-7-4.
        """
        # Check for Feb 29 within requested range.  If found, will need
        # to break at occurrences of both Feb 29 and new year.  After
        # initializing an array, append sections of the range between
        # breaks until end of requested range.
        tmy_yr = DFC.f2d_sgl2sgl(table.read(0, 1, field='timestamp')[0]).year
        range_sections, years = self._tmy_year_sections(start, stop, tmy_yr)
        arrays = []
        indices = []
        for i, year in enumerate(years[:-1]):
            start, stop = range_sections[i]
            # Use inclusive=False.  All tuples except the last one
            # indicate non-inclusive sections.
            self._tmy_read_year_section(
                table,
                start,
                stop,
                year,
                arrays,
                indices,
                *args,
                inclusive=False,
                return_indices=return_indices,
                **kwargs,
            )
        for i, year in enumerate(years[-1:]):
            start, stop = range_sections[-1]
            # Final tuple is inclusive; use inclusive=True.
            self._tmy_read_year_section(
                table,
                start,
                stop,
                year,
                arrays,
                indices,
                *args,
                inclusive=True,
                return_indices=return_indices,
                **kwargs,
            )
        data = rfn.stack_arrays(arrays, usemask=False, asrecarray=True)
        if return_indices:
            return data, np.hstack(indices)
        else:
            return data

    @staticmethod
    def _tmy_year_sections(start, stop, tmy_year):
        """Return a list of two-tuples representing start and end times
        for sections of the given range to be read from the TMY data
        file and a list of the requested years corresponding 1-to-1 with
        each section. Section breaks occur at new years and the start
        and end of leap days. Because breaks occur at new years, each
        section will correspond to only one year. Since TMY data files
        contain data for non-leap years, Feb. 28 is used in place of
        Feb. 29.
        
        End times are non-inclusive to avoid needing to know the
        smallest time increment. E.g. whether the entire day of February
        28th, 2017 (a non-leap year) is denoted as
        (2017/2/28 00:00, 2017/2/28 23:00) or
        (2017/2/28 00:00, 2017/2/28 23:59) depends on whether the
        smallest time increment is 1 hour or 1 minute. Using the non-
        inclusive notation (2017/2/28 00:00, 2017/3/1 00:00) to denote
        the section of time starting at the beginning of 2/28 and ending
        just before the beginning of 3/1 eliminates ambiguity.
        Positional arguments:
        start - (datetime) Start of range.
        stop - (datetime) End of range.
        tmy_year - (int) Year of the TMY data set.
        """
        # Define boolean functions for determining specific dates.
        def is_feb29(x):
            try:
                return x.date() == dt.date(x.year, 2, 29)
            except ValueError:
                # Not a leap year; can't make a date for 2/29.
                return False

        def is_new_year(x):
            return x == dt.datetime(x.year, 1, 1)

        # Find section breaks.  These occur at the start of a new year,
        # the start and end of Feb 29, and the start and stop dates.
        # The requested years are tracked at the same time.  This
        # procedure will result in breaks being one element longer than
        # req_yrs, since each year will correspond to the sections of
        # time bounded by pairing each element of breaks with the next
        # one.
        # The inequality used for the while condition is inclusive.
        # When the cursor ends on the stop date, one final append of the
        # cursor and year is required.
        breaks = []
        req_yrs = []
        cursor = start
        while cursor <= stop:
            breaks.append(cursor)
            req_yrs.append(cursor.year)
            if calendar.isleap(cursor.year):
                cursor_date = cursor.date()
                feb_29 = dt.date(cursor.year, 2, 29)
                if cursor_date < feb_29:
                    cursor = dt.datetime(cursor.year, 2, 29)
                elif cursor_date == feb_29:
                    cursor = dt.datetime(cursor.year, 3, 1)
                else:
                    cursor = dt.datetime(cursor.year + 1, 1, 1)
            else:
                cursor = dt.datetime(cursor.year + 1, 1, 1)
        breaks.append(stop)

        # Convert section breaks to sections.  For 2/29, read 2/28.
        # Modify year to ensure sections fall within the TMY year, i.e.
        # so the requested data is actually found in the TMY file.
        sections = []
        for b1, b2 in zip(breaks[:-1], breaks[1:]):
            x1 = b1.replace(day=28) if is_feb29(b1) else b1
            x1 = x1.replace(year=tmy_year)
            if is_feb29(b2):
                if b2 > dt.datetime(b2.year, 2, 29):
                    # Upper bound is somewhere in the middle of 2/29.
                    x2 = b2.replace(day=28)
                else:
                    # Upper bound is exactly the start of 2/29.
                    if is_feb29(b1):
                        # An occurrence of 2/29 in both bounds where b2
                        # is on hour zero can only mean that one data
                        # point on 2/29 is requested.
                        x2 = b2.replace(day=28)
                    else:
                        # Read up to the end of 2/28 in the TMY file.
                        x2 = b2.replace(month=3, day=1)
                x2 = x2.replace(year=tmy_year)
            # An occurrence of the new year where both bounds have the
            # same year can only mean that one final data point on Jan.
            # 1st is requested.
            elif is_new_year(b2) and b2.year != b1.year:
                x2 = b2.replace(year=tmy_year+1)
            else:
                x2 = b2.replace(year=tmy_year)
            sections.append((x1, x2))
        return sections, req_yrs

    def _tmy_read_year_section(
        self,
        table,
        start,
        stop,
        year,
        arrays,
        indices,
        *args,
        return_indices=False,
        impose_year=True,
        **kwargs,
    ):
        """Read a section from the TMY file up to the end of the year.
        """
        start,stop = self._handle_start_stop_args(table,start,stop,typecast='float')
        result = self._read_timestamp_range_from_table(
            table,
            start,
            stop,
            *args,
            return_indices=return_indices,
            **kwargs,
        )
        if return_indices:
            result, idx = result
            indices.append(idx)
        if (
            impose_year
            and result.dtype.names is not None
            and 'timestamp' in result.dtype.names
        ):
            # Replace the TMY file's year with the requested one.
            result['timestamp'] = DFC.d2f_lst2arr(
                [
                    x.replace(year=year)
                    for x in DFC.f2d_arr2lst(result['timestamp'])
                ]
            )
        arrays.append(result)

class OtherTimeSeries(TimeSeriesDataSet):
    def __init__(self, filename):
        super().__init__(filename, 'other')

    def start_dates(self, as_datetime=False):
        """Returns an array of the available start dates for this data
        set.

        Keyword arguments:
        as_datetime - (bool) (Default: False) Whether to return a list
            of datetime objects instead of an array of floats.
        """
        with self.file_context() as h5f:
            floats = getattr(h5f.root, 'available_start_dates').read()
            return DFC.f2d_arr2lst(floats) if as_datetime else floats
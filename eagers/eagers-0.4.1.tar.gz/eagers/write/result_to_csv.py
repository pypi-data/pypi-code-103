"""Write results from HDF5 to CSV format.

Functions:
write_result_to_csv
"""

import csv

import tables as tb

from eagers.config.path_spec import CSV_SUFFIX, USER_DIR_SIMRESULTS
from eagers.config.text import CSV_RESULT_SEP
from eagers.write.result_file import existing_h5_result_filepath
from eagers.basic.file_handling import ensure_suffix
from eagers.basic.hdf5 import h5file_context


def write_result_to_csv(proj_name):
    """Write result from HDF5 to CSV format."""
    h5path = existing_h5_result_filepath(proj_name)
    # Open file in 'r'ead mode, requiring its existence already.
    with h5file_context(h5path, 'r') as h5f:
        # Read data from result tables.
        root = h5f.root
        tables = list(c for c in root._v_children
            if isinstance(getattr(root, c), tb.table.Table))
        data = {table: getattr(root, table).read() for table in tables}
        # Define function for walking the fields of a structured array
        # dtype.
        def walk_dtype_fields(dtype, path, base_yield):
            fields = dtype.fields
            # "is not None" accounts for dtypes with 0 fields.
            if fields is not None:
                for k, v in fields.items():
                    subp = path + f"/{k}"
                    yield from walk_dtype_fields(v[0], subp, base_yield)
            else:
                yield base_yield(path, dtype)
        # Define function for getting data at a given path.
        def data_at_path(data, path):
            split_path = path.split('/')[1:]
            d = data
            for p in split_path:
                d = d[p]
            return d
        # Write to CSV file.
        def write_to_csv(proj_name, table_name):
            filename = f"{proj_name}{CSV_RESULT_SEP}{table}"
            csvpath = USER_DIR_SIMRESULTS / ensure_suffix(filename, CSV_SUFFIX)
            headers = list(walk_dtype_fields(
                data[table].dtype, "", (lambda p, d: p)))
            with open(csvpath, 'w', newline='') as csvf:
                writer = csv.DictWriter(csvf, fieldnames=headers)
                writer.writeheader()
                for entry in data[table]:
                    writer.writerow(dict(walk_dtype_fields(
                        data[table].dtype,
                        "",
                        (lambda p, d: (p, data_at_path(entry, p))),
                    )))
        for table in tables:
            write_to_csv(proj_name, table)

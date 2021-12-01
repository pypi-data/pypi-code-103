from eagers.basic.hdf5 import DatetimeFloatConverter as DFC

def auto_set_startdate(test_data):
    """Automatically set the value of start_date based on the given
    TestData. If start_date is already set, this does nothing.

    Positional arguments:
    test_data - (TestData) TestData instance used to find start
        date.
    """
    if 'nodedata' in test_data:
        tdfield = 'nodedata'
    elif 'hydro' in test_data:
        tdfield = 'hydro'
    else:
        tdfield = 'weather'
    # Use the first date common to all tables with a 'timestamp'
    # header as the start date.
    data = test_data[tdfield]
    timestamp_tables = [t for t in data.tablenames if 'timestamp' in data.colnames(t)]
    first_dates = (test_data[tdfield].read(t, 0, 1, field='timestamp')[0] for t in timestamp_tables)
    sd = DFC.f2d_sgl2sgl(max(first_dates))
    return sd
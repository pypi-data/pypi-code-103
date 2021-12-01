import datetime 
from random import random

from eagers.config.weather_file import WTS_ATTR_MAP
from eagers.basic.hdf5 import DatetimeFloatConverter as DFC
from eagers.basic.interp_numerical import interp_numerical


def get_data(data, date, network_names):
    """Load data corresponding to the given dates. Returns a dictionary
    with the following structure:
    {
        'timestamp': 1-D list of datetime.datetime
        'weather': {
            weather fields: 1-D lists of floats
        'Node1': {
            'network': network name (e.g. 'electrical')
            'demand': 1-D list of floats
        },
        'Node2': {...},
        ...
        'Node<n>': {...},
    }

    Positional arguments:
    data - (TestData) Body of data to be indexed.
    date - (list or array-like of datetime) Date vector for which data
        should be obtained.
    network_names - (list of str) Network names for which data should be
        guaranteed. If one of these names is not found in the data,
        zeros will be returned for that network.
    """
    # Initialize return structure.
    select_data = {}
    table_list = []
    header_list = {}
    d_type = {}
    d_node = {}
    for net in list(data['nodedata_network_info'].keys()):
        for n in range(len(data['nodedata_network_info'][net])):
            cat = list(data['nodedata_network_info'][net][n].keys())
            cat.remove('network')
            cat.remove('node')
            for c in cat:
                if c in ['demand','data']:
                    if net in ['hydro']:
                        d = 'tributary'
                    else:
                        d = 'demand'
                    t_name = data['nodedata_network_info'][net][n][c][0]
                    if not t_name in table_list:
                        table_list.append(t_name)
                        header_list[t_name] = []
                        d_type[t_name] = []
                        d_node[t_name] = []
                    header_list[t_name].append(data['nodedata_network_info'][net][n][c][1])
                    d_type[t_name].append(d)
                    d_node[t_name].append(data['nodedata_network_info'][net][n]['node'])
                    if not d_node[t_name][-1] in select_data:
                        select_data[d_node[t_name][-1]] = {}
                        select_data[d_node[t_name][-1]]['network'] = net
                    if not d_type[t_name][-1] in select_data[d_node[t_name][-1]]:
                        select_data[d_node[t_name][-1]][d_type[t_name][-1]] = {}
    select_data['timestamp'] = [d for d in date]
    d_streams = sum([len(header_list[i]) for i in header_list])  # number of streams of data so that noise can be created independant for each   
    ns = len(date)
    for table in table_list:
        interpolated_data = query_interpolate(date,data['nodedata'],header_list[table],table,True)
        j = 0
        for header in header_list[table]:
            select_data[d_node[table][j]][d_type[table][j]] = interpolated_data[header]
            j +=1

    select_data['weather'] = get_weather(data['weather'], date)
    select_data['other'] = get_other(data['other'], date)

    # Create noise if interpolation is needed and variability is specified.
    variability = 0
    #TODO: Get variability from relevant source.
    if variability > 0:
        noise = create_noise(ns,d_streams,variability)# Create noise vector.
        i = 0
        for table in table_list:
            j = 0
            for header in header_list[table]:
                select_data[d_node[table][j]][d_type[table][j]][header] = [(1+float(noise[i][t]))*select_data[d_node[table][j]][d_type[table][j]][header][t] for t in range(ns)]
                j+=1
                i+=1

    return select_data


def get_weather(data, date):
    table = data.tablenames[0]
    w_data_fields = data.colnames(table)
    # Don't need all weather headers unless there is a building model.
    weather_headers = [h for h in WTS_ATTR_MAP.values() if h in w_data_fields]
    # x query values for interpolation.
    if data.table_designation(table) == 'tmy':
        weather = query_interpolate(date,data,weather_headers,table,False)
    else:
        weather = query_interpolate(date,data,weather_headers,table,True)
    return weather

def get_other(data, date):
    other = {}
    for table in data.tablenames:
        header_list = data.colnames(table)
        interpolated_data = query_interpolate(date,data,header_list,table,True)
        for header in header_list:
            if not header in other:
                other[header] = interpolated_data[header]
    return other

def query_interpolate(date,data,header_list,table,val):
    # x query values for interpolation.
    if val:
        x_query = validate_dates(date,data,table)
    else:
        x_query = DFC.d2f_lst2lst(date)
    x_query_sorted = sorted(x_query)
    if len(x_query)>1:
        dts = 2 * (date[1] - date[0]).total_seconds()
        dte = 2 * (date[-1] - date[-2]).total_seconds()
    else:
        dts = 2 * 3600
        dte = 2 * 3600
    t_data_np = []
    while len(t_data_np)==0:
        t_data_np = data.read_timestamp_range(table, x_query_sorted[0]-dts, x_query_sorted[-1]+dte)
        if len(t_data_np)==0:
            dts *=24
            dte *=24
    t_data = dict(timestamp=t_data_np['timestamp'].tolist())
    t_data_dt = DFC.f2d_arr2lst(t_data_np['timestamp'])
    t_data.update({fk: t_data_np[fk].tolist() for fk in header_list})
    date_float = DFC.d2f_lst2lst(date)
    if val:
        x_vals = reverse_validate_date_shift(date, t_data_dt)
    else:
        x_vals = t_data['timestamp']
    if len(x_vals)==1:
        dtq1 = None
    else:
        dtq1 = x_vals[1] - x_vals[0]
    interpolated_data = interp_data(x_vals, t_data, date_float, header_list, None, dtq1)
    return interpolated_data

def create_noise(ns,nd,variability):
    z = [[random() for t in range(ns)] for i in range(nd)]
    # Scaled noise to a signal with average magnitude of 1.
    noise = [[] for i in range(nd)]
    for i in range(nd):
        noise[i] = [0]
        noise[i].append((random()- 0.5) * variability)
        if noise[i][1]>noise[i][0]:
            b=1
        else:
            b = -1
        c = noise[i][1]
        for n in range(2, ns):
            # If the noise is increasing the probability is such that the noise
            # should continue to increase, but as the noise approaches the peak
            # noise magnitude the probability of switching increases.
            if (c > 0 and noise[i][n-1] > 0) or (c < 0 and noise[i][n-1] < 0):
                # Constant 2 = 97.7% probability load changes in same direction,
                # 1.5 = 93.3%, 1 = 84.4%, .5 = 69.1%.
                a = 2 * (variability - abs(noise[i][n-1])) / variability
            else:
                a = 2
            if abs(z[i][n]) > 0.68:
                # Only changes value 50% of the time.
                # c is positive if abs(noise) is increasing, negative if
                # decreasing.
                c = b * (z[i][n]+a)
                if c>0:
                    b=1
                elif c<0:
                    b = -1
                noise[i].append(noise[i][n-1] + c*variability)
            else:
                noise[i].append(noise[i][n-1])
    return noise


def validate_dates(pull_date,data,table):
    # Make checks on the timestamps available for demand data.
    date = [d for d in pull_date]
    first_timestamp = DFC.f2d_sgl2sgl(data.read(table,0,1,field='timestamp')[0])
    last_timestamp = DFC.f2d_sgl2sgl(data.read(table,-1,field='timestamp')[0])
    # Move date up to one day past where the TestData timestamps begin,
    # if needed (starting simulation without historical data).
    if date[0] < first_timestamp:
        # Add whole # (rounded up) of days.
        i = 0
        while i<len(date) and date[i] < first_timestamp:
            date[i] += datetime.timedelta(days=1)
            if date[i] >= first_timestamp:
                i += 1
    if date[-1] > last_timestamp:
        # Subtract whole # of days.
        i = len(date) - 1
        while i>=0 and date[i] > last_timestamp:
            date[i] -= datetime.timedelta(days=1)
            if date[i] <= last_timestamp:
                i -= 1
    date = DFC.d2f_lst2lst(date)
    return date


def reverse_validate_date_shift(pull_date, time_data):
    # Move date up to one day past where the TestData timestamps begin,
    # if needed (starting simulation without historical data).
    first_timestamp = min(pull_date)
    last_timestamp = max(pull_date)
    if time_data[0] > first_timestamp:
        # Subtract whole number (rounded up) of days.
        i = 0
        while i < len(time_data) and time_data[i] > first_timestamp:
            if i == 0 or time_data[i] - datetime.timedelta(days=1) > time_data[i-1]:
                time_data[i] -= datetime.timedelta(days=1)
            if time_data[i] <= first_timestamp or (i > 0 and time_data[i] - datetime.timedelta(days=1) <= time_data[i-1]):
                i += 1
    if time_data[-1] < last_timestamp:
        # Add whole number of days until > last pull date, but not
        # exceeding the value after it.
        i = len(time_data) - 1
        while i >= 0 and time_data[i] < last_timestamp:
            if i == len(time_data) - 1 or time_data[i] + datetime.timedelta(days=1) < time_data[i+1]:
                time_data[i] += datetime.timedelta(days=1)
            if time_data[i] >= last_timestamp or (i < len(time_data) - 1 and time_data[i] + datetime.timedelta(days=1) >= time_data[i+1]):
                i -= 1
    time_data = DFC.d2f_lst2lst(time_data)
    return time_data


def interp_data(x_vals, data, x_query, f, n_input, dtq1):
    select_data = {}
    for fk in f:
        if dtq1 is None:
            select_data[fk] = [data[fk][0] for t in range(len(x_query))]
        else:
            select_data[fk] = interp_numerical(data[fk], x_query, x_vals, dtq1)
        if isinstance(n_input, (float, int)):
            select_data[fk] = [select_data[fk][t][n_input] for t in range(len(select_data[fk]))]
    return select_data




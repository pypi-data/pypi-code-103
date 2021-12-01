import numpy as np 

from eagers.basic.lowess import lowess as fit
from eagers.basic.lowess import tri_cube as tri_cube
from eagers.basic.typical_day import typical_day
from eagers.basic.hdf5 import DatetimeFloatConverter as DFC


def calculate_fits(test_data, options, subnet):
    # Create typical day fits if necessary.
    hist_prof = []
    if not options['forecast'] in ['perfect','uncertain']:
        hist_prof = {}
        weather = test_data['weather'].read()
        for x in weather:
            if not x == 'timestamp':
                hist_prof[x] = typical_day(weather['timestamp'], weather[x])
        if 'hydro' in subnet:
            hist_prof['hydro_source_sink'] = {}
            #TODO creat source_sink from upstream/downstream relations
            for n in range(len(subnet['hydro']['nodes'])):
                inflow = test_data['nodedata_network_info']['hydro'][n]['inflow_history']
                inflow_data = test_data['nodedata'].read(inflow[0],0,-1, field = inflow[1])
                outflow = test_data['nodedata_network_info']['hydro'][n]['outflow_history']
                outflow_data = test_data['nodedata'].read(outflow[0],0,-1, field = outflow[1])
            
            hydro = test_data.hydro.read()
            for n in range(len(hydro['source_sink'])):
                hist_prof['hydro_source_sink'][n] = typical_day(hydro['timestamp'],hydro['source_sink'][n])
    # Create surface fits if necessary.
    if options['forecast'] == 'surface':
        select_data = {}
        for net in subnet['network_names']:
            if net in test_data['nodedata_network_info']:
                for n in range(len(test_data['nodedata_network_info'][net])):
                    cat = list(test_data['nodedata_network_info'][net][n].keys())
                    cat.remove('network')
                    cat.remove('node')
                    for c in cat:
                        if c.find('history')>=0:
                            t_name = test_data['nodedata_network_info'][net][n][c][0]
                            header = test_data['nodedata_network_info'][net][n][c][1]
                            d_type = c.replace('_history','')
                            d_node = test_data['nodedata_network_info'][net][n]['node']
                            if not d_node in select_data:
                                select_data[d_node] = {}
                            if not d_type in select_data[d_node]:
                                select_data[d_node][d_type]['timestamp'] = test_data['nodedata'].read(t_name,field = 'timestamp')
                                select_data[d_node][d_type]['data'] = []
                            #TODO check that timestamps allign and interpolate if not?
                            select_data[d_node][d_type]['data'].append([test_data['nodedata'].read(t_name,field = header)])
        hist_prof = surface_fits(select_data,weather)
    test_data['hist_prof'] = hist_prof


def surface_fits(demand, weather):
    #TODO Revise with new nodal data structure
    """Calculate fits."""
    d_surf = {}
    f = list(demand.keys())
    f.remove('timestamp')
    d_time = DFC.f2d_arr2arr(demand['timestamp'])
    w_time = DFC.f2d_arr2arr(weather['timestamp'])
    ti = find_nearest_time(w_time,d_time[0],0)
    if ((d_time[-1] -d_time[0]).total_seconds())/31536000<(1/3): #make one set of surfaces
        if (d_time[1] -d_time[0]).total_seconds()<15*60: # sub 15 minute data, average at each hour to reduce surface fitting problem
            d,dt = average_intrahourly(demand,d_time)
            x,y,min_t,max_t = build_x(d,dt,weather['t_dryb'],w_time,ti)
        else:
            x,y,min_t,max_t = build_x(demand,d_time,weather['t_dryb'],w_time,ti)
        x0 = np.mgrid[0:24:1,min_t:max_t:(max_t-min_t)/20]
        x0 = np.vstack([x0[0].ravel(), x0[1].ravel()])
        for k in f:
            d_surf[k]['annual'] = fit(x,y[k],x0, kernel=tri_cube)
            
    else: #make a separate surface for each month and weekdays/weekends
        w_day = d_time.isoweekday()
        m_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        
        x,y,min_t,max_t = split_data(demand,d_time,weather['t_dryb'],w_time,ti,w_day)    
        for m in range(12):
            x0 = np.mgrid[0:24:1,min_t[m]:max_t[m]:(max_t[m]-min_t[m])/20]
            x0 = np.vstack([x0[0].ravel(), x0[1].ravel()])
            for k in f:
                if len(x[m][0])>0:
                    d_surf[k][m_names[m]+'weekday'] = fit(x[m][0],y[k][m][0],x0, kernel=tri_cube)
                if len(x[m][1])>0:
                    d_surf[k][m_names[m]+'weekend'] = fit(x[m][1],y[k][m][1],x0, kernel=tri_cube)
    return d_surf


def split_data(d,dt,w,wt,ti,w_day):
    f = list(d.keys())
    min_t = [[] for i in range(12)]
    max_t = [[] for i in range(12)]
    nd = len(dt)
    y = {}
    for k in f:
        y[k] = [[[],[]] for i in range(12)]
    x = [[[[],[]],[[],[]]] for i in range(12)]
    for i in range(nd):
        ti = find_nearest_time(wt,dt[i],ti)
        m = dt[i].month
        if w_day[i] >= 6:
            wd = 1
        else:
            wd = 0
        for k in f:
            y[k][m][wd].append(d[k][i])
        x[m][wd][0].append(dt[i].seconds/3600)
        x[m][wd][1].append(w[ti])
        if len(max_t[m]) == 0:
            max_t[m] = w[ti]
        elif w[ti]>max_t[m]:
            max_t[m] = w[ti]
        if len(max_t[m]) == 0:
            min_t[m] = w[ti]
        elif w[ti]<min_t[m]:
            min_t[m] = w[ti]
    return x,y,min_t,max_t

def build_x(d,dt,w,wt,ti):
    f = list(d.keys())
    min_t = w[0]
    max_t = w[0]
    nd = len(dt)
    y = {}
    for k in f:
        y[k] = []
    x = [[],[]]
    for i in range(nd):
        for k in f:
            y[k].append(d[k][i])
        x[0].append(dt[i].hour + dt[i].minute/60 + dt[i].second/3600)
        ti = find_nearest_time(wt,dt[i],ti)
        x[1].append(w[ti])
        if w[ti]>max_t:
            max_t = w[ti]
        if w[ti]<min_t:
            min_t = w[ti]
    return x, y,min_t,max_t

def average_intrahourly(d,dt):
    f = list(d.keys())
    d2 = {}
    d3 = {}
    for k in f:
        d2[k] = []
        d3[k] = []
    dt2 = []
    dt3 = []
    nd = len(dt)
    i = 0
    while i<=nd:
        if i==nd or dt[i+1].hour!=dt[i].hour:
            for k in f:
                d2[k].append(sum(d3[k])/len(d3[k])) #average for hour
                d3[k] = []
            dt2.append(dt3[0]) #start of hour
            dt3 = []
        else:
            for k in f:
                d3[k].append(d[k][i])
            dt2.append(dt[i])
        i +=1
    return d2,dt2

def find_nearest_time(time,date,ti):
    nw = len(time)
    while ti<nw and time[ti]<date:
        ti +=1
    while ti>0 and abs(time[ti-1]-date)<(time[ti]-date):
        ti -=1
    return ti

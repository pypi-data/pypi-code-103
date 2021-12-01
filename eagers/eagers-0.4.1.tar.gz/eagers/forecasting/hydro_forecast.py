import datetime as dt

from eagers.basic.get_data import get_data, interp_data

def hydro_forecast(forecast,test_data,date,subnet,observer,options):
    #TODO rework for new nodal structure of forecast and prev_data/now_data
    if 'hydro' in subnet:
        freq = max([1,round(options['horizon']/24,0)]) #period of repetition (1 = 1 day) This is how far back the forecasting methods are able to see. It is irrelevant if the forecast is perfect
        d0 = date[0] - dt.timedelta(hours = 24*freq+options['resolution'])
        prev_date = [d0 + dt.timedelta(hours = i*options['resolution']) for i in range(round(24*freq/options['resolution'],0)+1)]
        prev_data = get_data(test_data,prev_date,None)
        n_s = len(prev_data['hydro']['inflow'])
        n = len(prev_data['hydro']['inflow'][0]) # Number of nodes
        now_data = get_data(test_data,date[0]-dt.timedelta(hours = options['resolution']),None)
        if observer['hydro_wy_timestamp'] !=None:
            xi = 0
            while observer['timestamp'][xi+1]>0 and observer['timestamp'][xi+1]<prev_data['timestamp'][0]:
                xi+=1
            xf = xi + 0
            while observer['timestamp'][xf+1]>0 and observer['timestamp'][xf+1]<now_data['timestamp'][0]:
                xf+=1
            yi = 0
            while prev_data['timestamp'][yi]<observer['timestamp'][0]:
                yi+=1
            prev_data['hydro']['outflow'] = [[0 for i in range(n)] for t in range(n_s)]
            now_data['hydro']['outflow'] =  [[0 for i in range(n)] for t in range(n_s)]
            #TODO revise to new node based data structure
            for n in range(len(subnet['hydro']['line_number'])):
                select_data = interp_data(observer['timestamp'],observer,prev_data['timestamp'][yi:],['lineflows'],n,options['resolution']*3600)
                prev_data['hydro']['outflow'][yi:][n] = select_data['lineflows'][0]
                now_data['hydro']['outflow'][n] = observer['lineflows'][xf][subnet['hydro']['lineNumber'][n]]
            forecast['hydro']['inflow'] = forecast_hydro(date,forecast['hydro_sourcesink'],subnet,prev_data,now_data)
        else:
            ##Only reached when finding initial operating condition: assume inflow = outflow
            if not 'inflow' in forecast['hydro']:
                forecast['hydro']['inflow'] = [[of[t] for t in range(len(of))] for of in forecast['hydro']['outflow']]
    return forecast

def forecast_hydro(date,source_sink,subnet,prev_data,now_data):
    # forecast the source/sink + previously released upsteam water flow at each 
    # time step: 1 to nS. When t<T it needs the scheduled outflow of the
    # upstream dam to be on the constant side of the optimization.
    # does not give a forecast at t=0;
    n_s = len(date)
    t_last_disp = now_data['timestamp']
    dtq1 = (date[0] - t_last_disp).total_seconds()
    in_flow = [[ss[t] for t in range(len(ss))] for ss in source_sink]
    outflow = {}
    outflow['timestamp'] = [prev_data['timestamp'],now_data['timestamp']]
    outflow['flow'] = [prev_data['hydro']['outFlow'],now_data['hydro']['outflow']]
    for n in range(len(subnet['hydro']['nodes'])):
        k = subnet['hydro']['up_river'][n]
        for j in range(len(k)):
            t_seg = subnet['hydro']['linetime'][k[j]]
            for t in range(n_s):
                if (date[t] - t_last_disp)<= t_seg/24: # All of the flow reaching this reservior at this time was previously scheduled
                    select_data = interp_data(outflow['timestamp'],outflow,date[t]-t_seg/24,['flow'],n,dtq1)
                    in_flow[t][n] = in_flow[t][n] + select_data['flow'][0] #outflow from previous dispatches because the time preceeds t_last_disp
                elif t>0 and (date[t-1] - t_last_disp)< t_seg/24: # A portion of the flow reaching this reservior at this time was previously scheduled
                    frac = (date[t]- t_last_disp - t_seg/24)/(date[t] - date[t-1])
                    if (date[t]-t_seg/24)>outflow['timestamp'][-1]:
                        in_flow[t][n] += (1-frac)*outflow[-1][k[j]]
                    else:
                        select_data = interp_data(outflow['timestamp'],outflow,date[t]-t_seg/24,['flow'],n,dtq1)
                        in_flow[t][n] += (1-frac)*select_data['flow'][0] #outflow from previous dispatches because the time preceeds t_last_disp
    return in_flow
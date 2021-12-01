from eagers.basic.hdf5 import DatetimeFloatConverter as DFC

def weather_forecast(data, prev_data, hist_prof, date):
    """Weather forecast."""
    forecast = {}
    do_not_overwrite = []
    if 'forecasts' in data and 'weather' in data.forecasts:
        f = list(data.forecasts.weather.keys())
        for k in f:
            forecast[k] = data.forecasts.weather[k]
            do_not_overwrite.append(k)
    if 'weather' in data:
        p_time = DFC.d2f_arr2arr(prev_data['timestamp'])
        hour = date.hour()
        nd = len(hour)
        n_time = DFC.d2f_arr2arr(date)
        for f in prev_data:
            if f == 'timestamp':
                forecast[f] = date
            if f in do_not_overwrite or not isinstance(prev_data[f][0],(float,int)):
                pass
            else:
                if len(date) == 1:
                    forecast[f] = prev_data[f][-1] #most recent data point
                else:
                    ip = 0
                    for t in range(nd):
                        while ip<len(p_time) and p_time[ip]<n_time(t):
                            ip+=1
                        if ip == 0:
                            yf = prev_data[f][ip]
                        else: 
                            r = (n_time[t]-p_time[ip])/(p_time[ip]-p_time[ip-1])
                            yf = r*prev_data[f][ip-1]+(1-r)*prev_data[f][ip]
                        if hour[t]<1:
                            hf = (1-hour[t])*hist_prof[f][-1]+hour[t]*hist_prof[f][0]
                        else:
                            hp = round(hour[t]-.5,0) # round down to nearest hour
                            r = hour[t] - hp
                            hf = (1-r)*hist_prof[f][hp]+hour[t]*hist_prof[f][hp+1]
                        offset = prev_data[f][-1] - prev_data[f][0] 
                        if hour[t] <1:
                            forecast[f][t] = (1-hour[t]/10)*(prev_data[f][-1])+hour[t]/10*hf
                        if hour[t]<4:
                            forecast[f][t] = (1.1-hour[t]/5)*(yf+offset)+(hour[t]/5-.1)*hf #Balanced between yesterdays T and historical T (includes forecast for current time)
    return forecast

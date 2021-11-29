'''
Interprete the EnergyPlus format schedules to get a value at the specified time
'''
from building_plus.basic.two_way_interp import two_way_interp

import datetime as dt

def load_sched(schedules,holidays,date,param,dd):
    profile = {}
    n_s = len(date) # number timesteps 
    h_days = find_holidays(date[0],holidays)
    ds_start,ds_end = find_daylight_savings(date[0])  
    if param is None:
        param = [x for x in schedules]
        single_sched = False
    elif len(param) ==1:
        single_sched = True
    for x in param:
        sched = schedules[x]['profile']
        profile[x]= [0 for i in range(n_s)]
        if 'timestamp' in  schedules[x]:
            print('user defined schedule')
            # profile[x] = interp_sched(sched,date) #user defined schedules defined at each time step
        else:
            for d in date:
                wd = d.weekday()
                holiday = False
                if any([x==dt.datetime(d.year,d.month,d.day) for x in h_days]):
                    holiday = True
                ds = False
                if d>ds_start and d<ds_end:
                    ds = True
                h = d.hour+d.minute/60+d.second/3600 # hour of day
                if h==0:
                    h=24
                if ds:
                    h = h+1
                    if h>24:
                        h=h-24
                hs = (d-dt.datetime(d.year,1,1)).total_seconds()/3600 #hours since start of year
                s = min([j for j in range(len(schedules[x]['seasons'])) if schedules[x]['seasons'][j]>=hs])
                inter = schedules[x]['interpolate'][s]
                ramp = schedules[x]['ramp']
                if 'AllOtherDays' in sched:
                    day = 'AllOtherDays'
                elif 'AllDays' in sched:
                    day = 'AllDays'
                elif 'ALLDays' in sched:
                    day = 'ALLDays'
                if holiday:
                    if 'Holidays' in sched:
                        day = 'Holidays'
                elif wd ==6:
                    if 'Sunday' in sched:
                        day = 'Sunday'
                    elif 'Sun' in sched:
                        day = 'Sun'
                elif wd ==5:
                    if 'Saturday' in sched:
                        day = 'Saturday'
                    elif 'Sat' in sched:
                        day = 'Sat'
                else:
                    if 'Weekday' in sched:
                        day = 'Weekday'
                    elif 'Weekdays' in sched:
                        day = 'Weekdays'                
                if dd and d.month>3:
                    day = 'SummerDesignDay'
                elif dd and d.month<=3:
                    day = 'WinterDesignDay'
                
                if inter:
                    if ramp>1e-3:
                        time,val = convert_sched(sched[day][s]['time'],sched[day][s]['val'],schedules[x]['ramp'])
                        profile[x] = two_way_interp(h,time,val) #interpolation
                    else:
                        profile[x] = two_way_interp(h,sched[day][s]['time'],sched[day][s]['val']) #interpolation
                else:#Energy plus step change at hour
                    k = 0
                    while sched[day][s]['time'][k]<h:
                        k +=1
                    profile[x] = sched[day][s]['val'][k]

    if single_sched:
        profile = profile[param[0]]       
    return profile

def find_holidays(date0,holidays):
    holiday = []
    month_names = ['january','february','march','april','may','june','july','august','september','october','november','december',]
    month_days = [31,28,31,30,31,30,31,31,30,31,30,31]
    weekday_names = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
    for x in holidays:
        s = holidays[x]['start'].split()
        if s[0] in month_names:
            m = month_names.index(s[0])+1
            d = int(s[1])
        else:
            m = month_names.index(s[3])+1
            wd = weekday_names.index(s[1])
            dm = [t+1 for t in range(month_days[m-1]) if dt.datetime(date0.year,m,t+1).weekday()==wd]
            if s[0] == '1st':
                d = dm[0]
            elif s[0] == '2nd':
                d = dm[1]
            elif s[0] == '3rd':
                d = dm[2]
            elif s[0] == '4th':
                d = dm[3]
            elif s[0] == 'last':
                d = dm[-1]
        if date0.month>m:
            y = date0.year+1
        else:
            y = date0.year
        holiday.append(dt.datetime(y,m,d))
        
    return holiday

def convert_sched(t1,v1,r):
    if len(t1)==2:#contant value all day
        time = t1
        val = v1
    else:
        time = [t1[0]]
        val = [v1[0]]
        for t in range(1,len(t1)):
            time.append([t1[t]-min(r,(t1[t]-t1[t-1])/2),t1[t]+min(r,(t1[t]-t1[t-1])/2)])
            val.append([v1[t-1],v1[t]])
        time.append(t1[-1])
        val.append(v1[-1])
    return time,val

def find_daylight_savings(d):
    md = [dt.datetime(d.year,3,1) + dt.timedelta(days=i) for i in range(31)]
    wd = [md[x].weekday() for x in range(31)]
    sun = [i for i,x in enumerate(wd) if x==6]
    ds_start = dt.datetime(d.year,3,sun[1]) #second sunday in march

    nd = [dt.datetime(d.year,11,1) + dt.timedelta(days=i) for i in range(30)]
    wd = [nd[x].weekday() for x in range(30)]
    sun = [i for i,x in enumerate(wd) if x==6]
    ds_end = dt.datetime(d.year,11,sun[0]) #first sunday in november
    return ds_start,ds_end

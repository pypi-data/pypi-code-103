'''
Simulate the initial day X times until initial temperature conditions reach equilibrium
'''

from building_plus.process.run_building import run_building
from building_plus.basic.interpolate_weather import interpolate_weather

import datetime
import time

def building_warmup(building,weather,date0,des_day):
    print('Begining building warmup for:  ' + building['name'] + ' ....')
    t = time.process_time()
    date = warm_up_date(building,date0)
    wu_weather = interpolate_weather(weather,date)
    T_zone = [23 for i in range(len(building['zones']['name']))]
    T_surf = [23 for i in range(len(building['ctf']['subsurf_names']))]
    humidity = [0.00825 for i in range(len(building['zones']['name']))] #initial humidity of each zone
    T_zone, T_surf, humidity, frost,_,_,_,_ = run_building(building,[T_zone],[T_surf],[humidity],wu_weather,date,des_day)
    print('warmup time was:  ' + str(time.process_time()-t) + '  seconds')
    return T_zone, T_surf, humidity, frost

def warm_up_date(building,date0):
    date = []
    wu_days = building['site']['min_warm_up'] +.25*(building['site']['max_warm_up'] - building['site']['min_warm_up']) #warm up days
    if date0>building['sim_date'][24*7-1]:
        wu_week = 1
        while wu_days-7*wu_week>0:
            wu_week+=1
        date1 = date0 + datetime.timedelta(hours=-168)
        for x in range(1,int(round(wu_week))):
            date.extend([date1 + datetime.timedelta(hours=i) for i in range(168)])
    else:
        if date0>building['sim_date'][23]:
            date1 = date0 + datetime.timedelta(hours=-24)
            for x in range(1,int(round(wu_days))):
                date.extend([date1 + datetime.timedelta(hours=i) for i in range(24)])
        else:
            n = 0
            while date0>building['sim_date'][n]:
                n +=1
            for x in range(1,int(round(wu_days))):
                date.extend([date0 + datetime.timedelta(hours=i) for i in range(24-n)])
                date.extend([building['sim_date'][0] + datetime.timedelta(hours=i) for i in range(n)])
    return date
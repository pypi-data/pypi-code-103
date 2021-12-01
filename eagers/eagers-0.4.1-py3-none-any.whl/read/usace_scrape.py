''' https://www.nwd.usace.army.mil/CRWM/'''

import urllib.request
import time
from datetime import datetime

from eagers.config.path_spec import USER_DIR_DATA_RETRIEVAL


def query_web(html_list,file_list):
    for i in range(len(html_list)):
        urllib.request.urlretrieve(html_list[i],file_list[i])
        time.sleep(1)

def build_lists(sites,param,units,save_dir,d1,d2):
    #build list of URL's and file names
    # Note that electric data only available older than 6 days
    base = 'https://www.nwd-wc.usace.army.mil/dd/common/web_service/webexec/ecsv?id='
    d_now = datetime.now()
    days = (d_now - d1).days
    if d_now.minute>30:
        tod = 'd' + str(d_now.hour) + 'h' + str(d_now.minute-30) + 'm'
    else:
        tod = 'd' + str(d_now.hour-1) + 'h' + str(d_now.minute+30) + 'm'
    weeks = int(days/7)
    days -= 7*weeks
    lookback = '&headers=true&filename=&timezone=PST&lookback=' + str(weeks) + 'w' + str(days) + tod
    days = (d_now - d2).days
    weeks = int(days/7)
    days -= 7*weeks
    lookforward = '&lookforward=' + '-' + str(weeks) + 'w' + str(days) + tod
    m = d1.month
    if m<10:
        m = '0' + str(m)
    else:
        m = str(m)
    day = d1.day
    if day<10:
        day = '0' + str(day)
    else:
        day = str(day)
    start_date = '&startdate=' + m + '%2F' + day + '%2F' + str(d1.year) + '+07%3A00'
    m = d2.month
    if m<10:
        m = '0' + str(m)
    else:
        m = str(m)
    day = d2.day
    if day<10:
        day = '0' + str(day)
    else:
        day = str(day)
    end_date = '&enddate=' + m + '%2F' + day + '%2F' + str(d2.year) + '+07%3A00'
    html_list = []
    file_list = []    
    for k in range(len(sites['names'])):
        code = sites['abbrev'][k]
        tags = ''
        for j in range(len(param)):
            tags = tags + code + param[j] + units[j]
        url = base + tags + lookback + lookforward + start_date + end_date
        f_name = save_dir + '/' + sites['names'][k]  + '.txt'
        html_list.append(url)
        file_list.append(f_name)
    return html_list, file_list

save_dir = USER_DIR_DATA_RETRIEVAL
sites = {}
sites['names'] = ['bonnevile', 'dalles', 'john_day', 'mcnary', 'priest_rapids', 'wanapum', 'rock_island', 'rocky_reach', 'wells', 'chief_joseph', 'grand_coulee', 'ice_harbor', 'lower_monumental', 'little_goose', 'lower_granite', 'dworshak', 'albeni_falls']
sites['abbrev'] = ['BON', 'TDA', 'JDA', 'MCN', 'PRD', 'WAN', 'RIS', 'RRH', 'WEL', 'CHJ', 'GCL', 'IHR', 'LMN', 'LGS', 'LWG', 'DWR', 'ALF']
start_date = datetime(2019, 10, 1)
end_date = datetime(2020, 9, 30)
param = ['.Flow-Gen.Ave.1Hour.1Hour.CBT-REV','.Flow-Spill.Ave.1Hour.1Hour.CBT-REV','.Flow-Out.Ave.1Hour.1Hour.CBT-REV','.Power.Total.1Hour.1Hour.CBT-RAW']
flow_unit = '%3Aunits%3Dkcfs'
power_unit = '%3Aunits%3DMW'
units = [flow_unit + '%7C', flow_unit + '%7C', flow_unit + '%7C', power_unit]
html_list,file_list = build_lists(sites,param,units,save_dir,start_date,end_date)
query_web(html_list,file_list)#query website

# Additional flow only data from USACE
sites['names'] = ['hells_canyon_outflow']
sites['abbrev'] = ['HCDI']
param = ['.Flow.Inst.15Minutes.0.USGS-REV']
units = [flow_unit]
html_list,file_list = build_lists(sites,param,units,save_dir,start_date,end_date)
query_web(html_list,file_list)#query website

sites['names'] = ['cabinet_gorge_outflow', 'noxon_outflow']
sites['abbrev'] = ['CAB', 'NOX']
param = ['.Flow-Out.Ave.1Hour.1Hour.CBT-RAW','.Flow-In.Ave.1Hour.0.CENWS-COMPUTED-RAW']
units = [flow_unit + '%7C', flow_unit]
html_list,file_list = build_lists(sites,param,units,save_dir,start_date,end_date)
query_web(html_list,file_list)#query website

sites['names'] = ['cabinet_gorge_inflow']
sites['abbrev'] = ['CAB']
param = ['.Flow-In.Ave.1Hour.0.CENWS-COMPUTED-RAW']
units = [flow_unit]
html_list,file_list = build_lists(sites,param,units,save_dir,start_date,end_date)
query_web(html_list,file_list)#query website

# Additional storage data from USACE
sites['names'] = ['cabinet_gorge_storage','noxon_storage']
sites['abbrev'] = ['CAB','NOX']
param = ['.Stor.Inst.1Hour.0.CBT-REV']
units = ['%3Aunits%3Dkaf']
html_list,file_list = build_lists(sites,param,units,save_dir,start_date,end_date)
query_web(html_list,file_list)#query website


'''Idaho Power data'''
'https://idastream.idahopower.com/Data/List/Parameter/Flow/Statistic/LATEST%20Flow/Interval/Latest'
'https://www.idahopower.com/community-recreation/recreation/water-information/stream-flow-data/'

''' BC Hydro'''
'https://wateroffice.ec.gc.ca/google_map/google_map_e.html?map_type=historical&search_type=region&region=PYR'
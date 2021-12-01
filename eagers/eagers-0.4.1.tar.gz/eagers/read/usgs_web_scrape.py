
import urllib.request
import time

from eagers.config.path_spec import USER_DIR_DATA_RETRIEVAL, USER_DIR_HYDRO_DATA


def query_web(html_list,file_list):
    for i in range(len(html_list)):
        urllib.request.urlretrieve(html_list[i],file_list[i])
        time.sleep(1)

def build_lists(sites,param,save_dir,date_range):
    #build list of URL's and file names
    base = 'https://nwis.waterdata.usgs.gov/usa/nwis/uv/?'
    dr = '&period=&begin_date=' + date_range[0] +'&end_date=' + date_range[1]
    html_list = []
    file_list = []
    for k in range(len(sites['names'])):
        if not sites['upriver'][k] is None:
            url = base + 'cb_' + '00060' + '=on&' + 'format=rdb&site_no=' + str(sites['upriver'][k]) + dr
            f_name = save_dir + '/' + sites['names'][k] + param + 'upriver' + '.txt'
            html_list.append(url)
            file_list.append(f_name)
        if not sites['downriver'][k] is None:
            url = base + 'cb_' + '00060' + '=on&' + 'format=rdb&site_no=' + str(sites['downriver'][k]) +dr
            f_name = save_dir + '/' + sites['names'][k] + param + 'downriver' + '.txt'
            html_list.append(url)
            file_list.append(f_name)
        if not sites['reservoir'][k] is None:
            url = base + 'cb_' + '00062' + '=on&' + 'format=rdb&site_no=' + str(sites['reservoir'][k]) +dr
            f_name = save_dir + '/' + sites['names'][k] + param + 'reservoir' + '.txt'
            html_list.append(url)
            file_list.append(f_name)
    return html_list, file_list

def site_names(n):
    sites = {}
    sites['names'] = ['Lake_Chelan_Dam',
                    'Cabinet_Gorge_Dam',
                    'Noxon_Rapids_Dam',
                    'Thompson_Falls_Dam',
                    'Bonneville_Dam',
                    'Chief_Joseph_Dam',
                    'Grand_Coulee_Dam',
                    'John_Day_Dam',
                    'Keenleyside_Dam',
                    'McNary_Dam',
                    'Mica_Dam',
                    'Priest_Rapids_Dam',
                    'Revelstoke_Dam',
                    'Rock_Island_Dam',
                    'Rocky_Reach_Dam',
                    'The_Dalles_Dam',
                    'Wanapum_Dam',
                    'Wells_Dam',
                    'Pelton_Dam',
                    'Hungry_Horse_Dam',
                    'Kerr_Dam',
                    'Brilliant_Dam',
                    'Corra_Linn_Dam',
                    'Kootenay_Canal_Generating_Station_Dam',
                    'Libby_Dam',
                    'South_Slocan_Dam',
                    'Upper_Bonnington_Falls_Dam',
                    'Dworshak_Dam',
                    'Long_Lake_Dam',
                    'Owyhee_Dam',
                    'Albeni_Falls_Dam',
                    'Boundary_Dam',
                    'Box_Canyon_Dam',
                    'Seven_Mile_Dam',
                    'Waneta_Dam',
                    'American_Falls_Dam',
                    'Bliss_Dam',
                    'Brownlee_Dam',
                    'C._J._Strike_Dam',
                    'Hells_Canyon_Dam',
                    'Ice_Harbor_Dam',
                    'Little_Goose_Dam',
                    'Lower_Granite_Dam',
                    'Lower_Monumental_Dam',
                    'Lower_Salmon_Falls_Dam',
                    'Milner_Dam',
                    'Oxbow_Dam',
                    'Shoshone_Falls_Dam',
                    'Twin_Falls_Dam']
    sites['upriver'] = [12451000,
                        None,
                        None,
                        
                        
                        ]

    sites['downriver'] = [12452500,
                          12391950,
                          12391400,

                        ]

    sites['reservoir'] = [12452000,
                          None,
                          None,
                          ]

    active_sites = {}
    for f in sites:
        active_sites[f] = [sites[f][j] for j in range(n)]
    return active_sites

from openpyxl import load_workbook


save_dir = USER_DIR_DATA_RETRIEVAL

usgs_param = {"discharge": '00060',"guage_height":'00065',"reservoir_elevation":'00062'}
wb = load_workbook(str(USER_DIR_HYDRO_DATA / 'usgs.xlsx'))
sites = site_names(2)
date_range = ['2007-01-01','2020-10-08']
html_list,file_list = build_lists(sites,usgs_param['discharge'],save_dir,date_range)
#query website
query_web(html_list,file_list)
#parse files
''' If dam A has an upstream gauge and the upstream dam has a downstream gauge, 
then source/sink can be calculated at the time resolution of the data (accounting 
for river run time). Otherwise if run of river average out daily difference in 
outflow to get avg daily source/sink'''
    #organize to common timestep and horizon

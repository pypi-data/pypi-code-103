import pickle

from building_plus.plot_sim import plot_sim
from building_plus.process.building_warmup import building_warmup
from building_plus.process.run_building import run_building
from building_plus.process.run_sim import run_sim
from building_plus.basic.interpolate_weather import interpolate_weather
from building_plus.config.building import BUILD_NAMES, CLIMATE_NAMES
from building_plus.config.path_spec import USER_DIR_BUILDINGS, USER_DIR_ENERGYPLUS_WEATHER, USER_DIR_EPLUS
from building_plus.read.weather_file import read_weather_file
from building_plus.read.load_data import load_data
from building_plus.read.load_building import load_building
from building_plus.read.example_file import load_example_file

def validate_building(build = 1,climate = '4A', start_day = 1, duration = 10, horizon = 0, mode = 'build',warmup = 'new'):
    ''''sim' for model predictive control simulation, 'build' for simulating a building without external control, 'warmup' just to warm up and save a model
      #'new' for new initialization, 'old' for a saved initialization

      buildings 2, 3, 4, 7, 8, 10 have flexibility (variable speed fans)
      build = input('Which building to run, name or 1-16?:')
      start_day = input('What day of the year will you start from (1-365)?:') 
      duaration = input('How many days will you simulate?:')
    '''
    if warmup == 'new':
        if isinstance(build,int):
            build = BUILD_NAMES[build-1]
        climate = CLIMATE_NAMES[climate]
        try:
            weather = read_weather_file(load_example_file(climate + '_TMY2.epw', 'eplus_weather'),'tmy')
            building = load_building(load_example_file('RefBldg'+build + 'New2004_v1.4_7.2_' + climate, 'eplus_buildings', suffixes=['.idf', '.eio']))
        except FileNotFoundError:
            weather = read_weather_file(USER_DIR_ENERGYPLUS_WEATHER / (climate + '_TMY2.epw'),'tmy')
            building = load_building(USER_DIR_BUILDINGS / ('RefBldg'+build + 'New2004_v1.4_7.2_' + climate))

        T_zone,T_surf,humidity,frost = building_warmup(building, weather, building['sim_date'][24*(start_day-1)], False)
        
        date = [building['sim_date'][i+24*(start_day-1)] for i in range(24*duration+1)]
        if len(weather['t_dryb']) != (len(date)+horizon):
            w_date = [building['sim_date'][i+24*(start_day-1)] for i in range(24*duration+horizon)]
            weather = interpolate_weather(weather, w_date)
        if mode == 'warmup': # save warmup variables
            f_name = input('Name the saved building model:')
            with open(f_name+'.pckl', 'wb') as f:
                pickle.dump([T_zone, T_surf, humidity, weather, building], f)
    elif warmup == 'old':
        f_name = input('Specify name of the saved building model:')
        with open(f_name + '.pckl', 'rb') as f:
            T_zone, T_surf, humidity, weather, building = pickle.load(f)

    if mode == 'build':
        T_zone, T_surf, m_v_zone, frost, m_sys, Q_transfer, facility, Q_test_plots = run_building(building, [T_zone[-1]], [T_surf[-1]], [humidity[-1]], weather, date, False)
        try:
            plot_sim(facility,T_zone,Q_transfer,building,date[1:], load_example_file('RefBldg'+build + 'New2004_v1.4_7.2_' + climate+'.csv', 'eplus_validation'))
        except FileNotFoundError:
            plot_sim(facility,T_zone,Q_transfer,building,date[1:],USER_DIR_EPLUS / ('RefBldg'+build + 'New2004_v1.4_7.2_' + climate+'.csv'))
    elif mode == 'sim':
        test_data = load_data(building, weather, date, T_zone[-1], humidity[-1])##load test_data: actual internal gains and weather different from forecast schedules?
        facility, net_elec = run_sim(building, test_data, weather, [T_zone[-1]], [T_surf[-1]], [humidity[-1]], date, horizon)
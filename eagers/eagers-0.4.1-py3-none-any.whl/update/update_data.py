
from datetime import timedelta
from numpy import log
from scipy.stats import t

from eagers.basic.get_data import get_data
from eagers.forecasting.arima import arima
from eagers.forecasting.arma import arma
from eagers.forecasting.surface_forecast import surface_forecast
from eagers.forecasting.weather_forecast import weather_forecast
from eagers.forecasting.input_cost_forecast import input_cost_forecast
from eagers.extras import bplus_forecast_dr_capacity
from eagers.simulate.renewable_output import renewable_output
from eagers.forecasting.hydro_forecast import hydro_forecast
from eagers.basic.find_gen_node import find_gen_node

def update_data(gen,building,subnet, date, options, test_data, observer,method):
    """Update forecast using any of the following forecasting
    algorithms:
    Perfect     Perfect forecast. Requires future data, and therefore is
                only available in simulation mode.
    Surface     Surface forecast.
    ARMA        AutoRegressive Moving Average forecast.
    ARIMA       AutoRegressive Integrated Moving Average forecast.
    ANN         Artificial Neural Network forecast.
    
    Positional arguments:
    options - (Optimoptions) Project options.
    date - (list of timestamp) Timestamps for which a forecast is
        requested.
    test_data 
    subnet - (dict) Network data.
    """
    
    if not method in ['perfect','uncertain']:
        #TODO replace with observer history
        d0 = date[0] # - timedelta(hours = 24+options['resolution'])
        prev_date = [d0 + timedelta(hours = i*options['resolution']) for i in range(int(round(24/options['resolution'],0)+1))]
        prev_data = get_data(test_data,prev_date,subnet['network_names'])
    data = {}
    if len(date)>1:
        date_f = date[1:]#forecaste date (excludes current timestamp)
    else:
        date_f = date
    data['timestamp'] = date_f
    
    if method != 'arima' and not method in ['perfect','uncertain']:
        data['weather'] = weather_forecast(test_data,prev_data, test_data['hist_prof'], date_f)
    if method == 'arma':
        data['demand'] = arma(date_f, prev_data)
    elif method == 'arima':
        data = arima(date_f, prev_data, options)
    elif method == 'neural_net':
        pass
    #TODO # create neural network forecasting option
    elif method == 'surface':
        data['demand'] = surface_forecast(prev_data, test_data['hist_prof']['demand'], date_f, data['weather']['t_dryb'],[])
    elif method in ['perfect','uncertain']:
        data = get_data(test_data, date_f, subnet['network_names'])
        if method in ['uncertain']:
            data = make_uncertain(data,options['forecast_uncertainty'])
    elif method == 'building':
        pass
    else:
        raise RuntimeError('Forecast option not recognized.')

    data['input_cost'] = input_cost_forecast(gen,date_f,data['other'])

    ### Make first hour forecast "perfect"
    # make_perfect(forecast,options,test_data,date_f,subnet)

    if options['spin_reserve']:
        if 'demand' in data:
            #TODO update this
            data['sr_target'] += options['spin_reserve_perc'] / 100 * sum(
                data['demand']['e'], 2)

    if 'weather' in data and 'dir_norm_irr' in data['weather']:
        data['renewable'] = []
        for g in gen:
            if g['type'] in ('Renewable', 'Solar', 'Wind') and g['enabled']:
                gen_network, i_node = find_gen_node(g, subnet)
                location = subnet[gen_network]["location"][i_node]
                gen_output = renewable_output(
                    g, date_f, data['weather']['dir_norm_irr'], location
                )
            else:
                gen_output = []
            data['renewable'].append(gen_output)
    if building:
        data['building'] = bplus_forecast_dr_capacity(building,observer,data['weather'],date)
    else:
        data['building'] = None
    data = hydro_forecast(data,test_data,date_f,subnet,[],options)
    return data


def make_uncertain(forecast,uncertain):
    '''Apply forecast error to the given forecast, using the given
    random number generator.

    Positional arguments:
    forecast - (dict) Forecast information with the same structure as
        returned by get_data().
    uncertain - Percent uncertainty or perturber object
    '''
    n = len(forecast['timestamp'])
    if isinstance(uncertain,(float,int)):
        gamma = [float(log(1+(i+1)/n*1.71828183) * uncertain)/100 for i in range(n)]

    node_names = list(forecast.keys())
    for node in node_names:
        if not node in ['weather','timestamp'] and 'demand' in forecast[node]:
            if isinstance(uncertain,(float,int)):
                forecast[node]['demand']  = rand_scale(forecast[node]['demand'], gamma)
            else:
                forecast[node]['demand']  = seeded_rand_scale(forecast[node]['demand'], uncertain)
    # Weather.
    for k in ['glo_horz_irr','dir_norm_irr','dif_horz_irr','t_dryb','wspd']:
        if k in forecast['weather']:
            if isinstance(uncertain,(float,int)):
                forecast['weather'][k]  = rand_scale(forecast['weather'][k] ,gamma)
            else:
                forecast['weather'][k]  = seeded_rand_scale(forecast['weather'][k], uncertain)
    return forecast

def rand_scale(signal,scale):
    u_signal = [signal[i]*max(0.5,min(1.5,1+t.rvs(1)*scale[i])) for i in range(len(scale))]
    return u_signal

def seeded_rand_scale(signal,seed):
    u_signal = [signal[i]*max(0.5,min(1.5,1+float(seed.rng.stats.cauchy.rvs(seed.gamma[i])))) for i in range(len(signal))]
    return u_signal


def make_perfect(forecast,options,test_data,date,subnet):
    #Make first step of forecast perfect:
    if options['method'].lower() == 'dispatch' and len(date) > 1:
        next_data = get_data(test_data, date[0], subnet['network_names'])
        for k in next_data:
            if isinstance(next_data[k], dict):
                for s_i in next_data[k]:
                    forecast[k][s_i][0] = next_data[k][s_i][0]
            else:
                forecast[k][0] = next_data[k][0]
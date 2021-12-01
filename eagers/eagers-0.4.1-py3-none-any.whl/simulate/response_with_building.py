from eagers.basic.find_gen_node import find_gen_node
from eagers.simulate.assign_disparity import assign_disparity
from eagers.solver.dispatch_loop import dispatch_loop
from eagers.basic.all_demands import all_demands
from eagers.simulate.renewable_output import renewable_output
from eagers.basic.component_output import component_output
from eagers.basic.marginal_cost import node_marginal
from eagers.extras import bplus_building_response
from eagers.simulate.check_validity import check_validity
from eagers.simulate.dispatch_network import dispatch_network


def response_with_building(
        gen, building, observer, subnet, names, actual_data,
        preload, options, forecast, date, solution):
    """Assigns where disparity between actual load and optimal dispatch
    goes. Building water loops absorb error in heating/cooling if there
    is a building model.
    """
    
    # 'control' mode runs real-time optimization that handles imbalance.
    if options['method'] =='control':
        # TODO: Reconstitute real-time control (Threshold and MPC).
        pass
    elif options['method'] =='dispatch':
        d_now = actual_data['timestamp'][0]
        t = 0
        while t<len(date)-1 and date[t+1]<d_now:
            t+=1
        tol = dict(electrical = 1e-3, direct_current = 1e-3, transmission_1 = 1e-3, district_heat = 5e-2, district_cool = 5e-2, heating_2 = 5e-2, cooling_water = 5e-2, hydrogen = 1e-3, liq_hydrogen = 1e-3, hydro = 1e-3) 
        dt_now = (d_now - date[0]).seconds/3600
        node_demand = all_demands(actual_data,subnet,[t])
        
        
        nn = list(node_demand.keys())
        # Sim all generators to determine actual heating, cooling, and waste heat to cooling loop
        for i, g in enumerate(gen):
            if g['type'] in ('Renewable', 'Solar', 'Wind'):
                gen_network, i_node = find_gen_node(g, subnet)
                location = subnet[gen_network]["location"][i_node]
                renew = renewable_output(g, [d_now], actual_data['weather']['dir_norm_irr'], location)
                solution['dispatch'][i][t+1] = renew[0]
                solution['generator_state'][g['name']][t] = renew[0]
        # ##TODO split heating and cooling among buildings
        # setpoint = {}
        # if 'district_heat' in subnet:
        #     net_heat_production, _ = component_output(gen,subnet['district_heat'],solution['generator_state'],0)
        #     setpoint['district_heat'] = [sum(actual_data['building']['water_heat']) + sum(net_heat_production) - sum(node_demand['district_heat'])]
        # if 'district_cool' in subnet:
        #     net_cool_production, _ = component_output(gen,subnet['district_cool'],solution['generator_state'],0)
        #     setpoint['district_cool'] =  [sum(net_cool_production) - sum(node_demand['district_cool'])]
            
        #sim fluid loops to assign thermal disparity to water loop
        for i in range(len(observer['fluid_loop_temperature'])):
            net_production, mag_production = component_output(gen,subnet['cooling_water'],solution['generator_state'],0)
            observer['fluid_loop_temperature'][i] += dt_now/observer['fluid_loop_capacitance'][i]*net_production[i]
        #Assign disparity for heating/cooling to utility/storage/buildings or re-optimize if none are present
        setpoint, re_opt  = building_disparity(gen,subnet,names,solution,forecast['building'],forecast['input_cost'], node_demand,dt_now,t,tol, options)
        if 'district_heat' in nn:
            nn.remove('district_heat')
        if 'district_cool' in nn:
            nn.remove('district_cool')
        setpoint['temperature'] = [solution['building'][k]['temperature'][0] for k in names['buildings']]

        #Sim buildings 
        weather_now = {}
        for i in actual_data['weather']:
            weather_now[i] = actual_data['weather'][i][0]
        observer,net_electric = bplus_building_response(building,observer, weather_now, actual_data['building'], dt_now, setpoint,d_now)
        actual_data['building']['E0'][0] = net_electric
        actual_data['building']['C0'][0] = [solution['building'][k]['cooling'][0] for k in names['buildings']]
        actual_data['building']['H0'][0] = [solution['building'][k]['heating'][0] for k in names['buildings']]

        #rebalance other networks if necessary
        for net in nn:
            request =  None 
            if net == 'electrical' and 'buildings' in subnet[net] and any([len(n)>0 for n in subnet[net]['buildings']]):
                request = {}
                request['nominal'] = net_electric
            if not re_opt:
                net_production, mag_production = component_output(gen,subnet[net],solution['generator_state'],t)
                disparity = check_validity(net_production, mag_production, node_demand[net], request, tol[net], False)
                if not disparity is None:
                    re_opt = assign_disparity(net, gen, subnet[net], disparity, solution, dt_now, t, re_opt)

        
        if re_opt:
            # Redo optimization due to disparity with actual data
            # and no slack bus, e.g. utility or storage.
            for k in forecast:
                if isinstance(forecast[k],dict) and 'demand' in forecast[k]:
                    forecast[k]['demand'][0] = actual_data[k]['demand'][0]
            forecast['building']['h_min'][0] = actual_data['building']['H0'][0]
            forecast['building']['c_min'][0] = actual_data['building']['C0'][0]
            forecast['building']['E0'][0] = actual_data['building']['E0'][0] 
            forecast['building']['C0'][0] = actual_data['building']['C0'][0]
            forecast['building']['H0'][0] = actual_data['building']['H0'][0]

            solution, _ = dispatch_loop(gen, observer, subnet, names, preload['op_mat_a'], preload['op_mat_b'],
                preload['one_step'], options, date, forecast, solution['dispatch'])

    elif options['method'] =='planning':
        n_s = len(date)-1
        for t in range(n_s):
            dt_now = (date[t+1] - date[t]).seconds/3600
            setpoint = {}
            setpoint['temperature'] = [solution['building'][k]['temperature'][t] for k in names['buildings']]
            setpoint['district_heat'] = [solution['building'][k]['heating'][t]*1000 for k in names['buildings']]
            setpoint['district_cool'] = [solution['building'][k]['cooling'][t]*1000 for k in names['buildings']]
            weather_now = {}
            for i in actual_data['weather']:
                weather_now[i] = actual_data['weather'][i][t]
            observer,net_electric = bplus_building_response(building,observer, weather_now, {},dt_now,setpoint,date[t])
            actual_data['building']['E0'][t] = net_electric
            actual_data['building']['C0'][t] = [solution['building'][k]['cooling'][t] for k in names['buildings']]
            actual_data['building']['H0'][t] = [solution['building'][k]['heating'][t] for k in names['buildings']]
            for i in range(len(observer['fluid_loop_temperature'])):
                net_production, mag_production = component_output(gen,subnet['cw'],solution['generator_state'],t)
                observer['fluid_loop_temperature'][i] += dt_now/observer['fluid_loop_capacitance'][i]*net_production[i]


def building_disparity(gen,subnet,names,solution,forecast,input_cost,node_demand,dt_now,t,tol,options):
    re_opt = False
    b_names = names['buildings']
    setpoint = {}
    ##TODO add capacity (particularly capacity for response by buildings for use in assign disparity)
    marginal = node_marginal(gen,subnet,solution['dispatch'],input_cost,solution['value_heat'])
    for net in ['district_heat', 'district_cool']:
        if net == 'district_heat':
            excess = options['excess_heat']
        else:
            excess = options['excess_cool']
        net_production, mag_production = component_output(gen,subnet[net],solution['generator_state'],0)
        request = {}
        request['minimum'] = [[0] for n in range(len(b_names))]
        request['maximum'] = [[0] for n in range(len(b_names))]
        request['nominal'] = [[0] for n in range(len(b_names))]
        for i in range(len(b_names)):
            t_avg = solution['building'][b_names[i]]['temperature'][0]
            if net == 'district_cool':
                t_bar = forecast['tc_bar'][0][i]
                ua = forecast['ua_c'][0][i]
                min_e = forecast['c_min'][0][i]
                t_min = forecast['Tmax'][0][i] #switched because Tmax should be temperature with minimum cooling
                t_max = forecast['Tmin'][0][i]
            elif net == 'district_heat':
                t_bar = forecast['th_bar'][0][i]
                ua = forecast['ua_h'][0][i]
                min_e = forecast['h_min'][0][i]
                t_min = forecast['Tmin'][0][i]
                t_max = forecast['Tmax'][0][i]
            request['nominal'][i] = max([(t_bar[0]-t_avg)*ua[0],(t_avg-t_bar[1])*ua[1],min_e])
            request['minimum'][i] = min([request['nominal'][i],max([(t_bar[0]-t_min)*ua[0],(t_min-t_bar[1])*ua[1],min_e])])
            request['maximum'][i] = max([request['nominal'][i],(t_bar[0]-t_max)*ua[0],(t_max-t_bar[1])*ua[1],min_e])

        if not request is None and 'nominal' in request:
            setpoint[net]  = [j*1000 for j in request['nominal']]
        disparity = check_validity(net_production, mag_production, node_demand[net], request, tol[net], excess)

        if not disparity is None:
            re_opt = assign_disparity(net, gen, subnet[net],disparity, solution, dt_now, t, re_opt)
            net_production, mag_production = component_output(gen,subnet[net],solution['generator_state'],t)
            setpoint[net] = distribute_heat_cool(names,subnet[net],net_production,node_demand[net],request,marginal,[])
    return setpoint, re_opt


def distribute_heat_cool(names,subnet,net_production,demand,request,marginal,capacity):
    ''' Find the thermal energy available for buildings at each node in the thermal network
    Then evenly distrubute amongs buildings at that node to minimize percent deviation from request
    Requires a optimization if there is a thermal network with line losses 
    output: thermal a list of the thermal energy provided to each building'''
    nn = subnet['nodes']
    if len(nn) == 1: #can handle multiple buildings at a single thermal node
        net_thermal = sum(net_production)
        if nn[0] in list(demand.keys()):
            net_thermal -= sum(demand[nn[0]]['demand'])
        net_request = sum(request['nominal'])
        if net_request == 0:
            thermal = [0 for j in request['nominal']]
        else:
            thermal = [j*(net_thermal/net_request)*1000 for j in request['nominal']]
    else:
        thermal = dispatch_network(names,subnet,net_production,demand,request,marginal,capacity,False)
    return thermal
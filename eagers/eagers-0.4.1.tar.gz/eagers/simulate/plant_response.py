from eagers.simulate.assign_disparity import assign_disparity
from eagers.solver.dispatch_loop import dispatch_loop
from eagers.basic.all_demands import all_demands
from eagers.simulate.renewable_response import renewable_response
from eagers.basic.component_output import component_output
from eagers.simulate.check_validity import check_validity
from eagers.simulate.response_with_building import response_with_building


def plant_response(
        gen, building, observer, subnet, names, actual_data,
        preload, options, forecast, date, solution):
    """Assigns where disparity between actual load and optimal dispatch goes.
    """
    
    if len(names['buildings'])>0:
        response_with_building(gen, building, observer, subnet, names, actual_data,
                                preload, options, forecast, date, solution)
    else:
        # 'control' mode runs real-time optimization that handles imbalance.
        if options['method'] =='control':
            # TODO: Reconstitute real-time control (Threshold and MPC).
            pass
        elif options['method'] =='dispatch':
            re_opt = False
            d_now = actual_data['timestamp'][0]
            t = 0
            while t<len(date)-1 and date[t+1]<d_now:
                t+=1
            tol = dict(electrical = 1e-3, direct_current = 1e-3, transmission_1 = 1e-3, district_heat = 5e-2, district_cool = 5e-2, heating_2 = 5e-2, cooling_water = 5e-2, hydrogen = 1e-3, liq_hydrogen = 1e-3, hydro = 1e-3) 
            dt_now = (d_now - date[0]).seconds/3600
            node_demand = all_demands(actual_data,subnet,[t])
            nn = list(node_demand.keys())
            renewable_response(gen,subnet,solution,actual_data,[d_now])

            
            #sim fluid loops to assign thermal disparity to water loop
            for i in range(len(observer['fluid_loop_temperature'])):
                net_production, mag_production = component_output(gen,subnet['cooling_water'],solution['generator_state'],t)
                observer['fluid_loop_temperature'][i] += dt_now/observer['fluid_loop_capacitance'][i]*net_production[i]
            #Assign disparity for heating/cooling to utility/storage/buildings or re-optimize if none are present
            for net in ['district_heat', 'district_cool']:
                if net == 'district_heat':
                    excess = options['excess_heat']
                else:
                    excess = options['excess_cool']
                
                if net in nn:
                    net_production, mag_production = component_output(gen,subnet[net],solution['generator_state'],t)
                    disparity = check_validity(net_production, mag_production, node_demand[net], None, tol[net], excess)
                    if not disparity is None:
                        re_opt = assign_disparity(net, gen, subnet[net],disparity, solution, dt_now, t, re_opt)
                        #temporary check to find errors
                        # error_check(gen,subnet,net,solution,t,node_demand,tol,disparity,excess)
                    nn.remove(net)
        
            #rebalance other networks if necessary
            for net in nn:
                if not re_opt:
                    net_production, mag_production = component_output(gen,subnet[net],solution['generator_state'],t)
                    disparity = check_validity(net_production, mag_production, node_demand[net], None, tol[net], False)
                    if not disparity is None:
                        re_opt = assign_disparity(net, gen, subnet[net], disparity, solution, dt_now, t,re_opt)
                        #temporary check to find errors
                        # error_check(gen,subnet,net,solution,t,node_demand,tol,disparity,excess)
                        
            if re_opt:
                # Redo optimization due to disparity with actual data
                # and no slack bus, e.g. utility or storage.
                for k in forecast:
                    if isinstance(forecast[k],dict) and 'demand' in forecast[k]:
                        forecast[k]['demand'][0] = actual_data[k]['demand'][0]
                solution, _ = dispatch_loop(gen, observer, subnet, names, preload['op_mat_a'], preload['op_mat_b'],
                    preload['one_step'], options, date, forecast, solution['dispatch'])

        elif options['method'] =='planning':
            n_s = len(date)-1
            for t in range(n_s):
                dt_now = (date[t+1] - date[t]).seconds/3600
                for i in range(len(observer['fluid_loop_temperature'])):
                    net_production, mag_production = component_output(gen,subnet['cw'],solution['generator_state'],t)
                    observer['fluid_loop_temperature'][i] += dt_now/observer['fluid_loop_capacitance'][i]*net_production[i]

def error_check(gen,subnet,net,solution,t,node_demand,tol,disparity,excess):
    new_net_production, new_mag_production = component_output(gen,subnet[net],solution['generator_state'],t)
    new_disparity = check_validity(new_net_production, new_mag_production, node_demand[net], None, tol[net], excess)
    if not new_disparity is None and abs(new_disparity/disparity)>tol[net]:
        print('A disparity of' +str(new_disparity) + 'remains in the '+ net + ' balance')
        ## Posible fixes>
        # e_net_production, e_mag_production = component_output(gen,subnet['electrical'],original_solution['generator_state'],t)
        # e_disparity = check_validity(e_net_production, e_mag_production, node_demand['electrical'], None, tol['electrical'], False)
        # assign_disparity('electrical', gen, subnet['electrical'], e_disparity, original_solution, dt_now, t, re_opt)
        # o_net_production, o_mag_production = component_output(gen,subnet[net],original_solution['generator_state'],t)
        # o_disparity = check_validity(o_net_production, o_mag_production, node_demand[net], None, tol[net], False)
        # assign_disparity(net, gen, subnet[net], o_disparity, original_solution, dt_now, t, re_opt)
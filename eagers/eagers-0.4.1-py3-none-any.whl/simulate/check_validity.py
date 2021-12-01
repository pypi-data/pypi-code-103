from eagers.basic.component_output import component_output
from eagers.basic.all_demands import all_demands
from eagers.read.load_dispatch_result import load_dispatch_result

def check_validity(net_production, mag_production, demand,request,tol,excess):
    ##TODO solve a nodal problem to determine any shortfall/excess energy in the network
    prod = sum(net_production)
    req = sum([demand[k] for k in demand])
    if not request is None and 'nominal' in request:
        req += sum(request['nominal'])
    disparity = None
    if abs(prod-req)>tol and ((abs(prod)<tol and abs(req)>tol) or (abs(prod)>tol and abs(prod-req)/sum(mag_production)>tol)):
        disparity = req - prod #Positive means there is unmet demand, negative means excess production
        if disparity<0 and excess: #can dump heat or cooling
            disparity = None
    return disparity

def verify_all_demand_met(proj):
    solution, disp_data, gen, subnet = load_dispatch_result(proj)
    tol = dict(electrical = 1e-3, direct_current = 1e-3, transmission_1 = 1e-3, district_heat = 5e-2, district_cool = 5e-2, heating_2 = 5e-2, cooling_water = 5e-2, hydrogen = 1e-3, liq_hydrogen = 1e-3, hydro = 1e-3) 
    for net in subnet['network_names']:
        if net == 'district_heat':
            excess = proj['options']['excess_heat']
        elif net == 'district_cool':
            excess = proj['options']['excess_cool']
        else:
            excess = None
        for t in range(len(solution['timestamp'])):
            node_demand = all_demands(disp_data['node_data'],subnet,[t])
            net_production, mag_production = component_output(gen,subnet[net],solution['generator_state'],t)
            disparity = check_validity(net_production, mag_production, node_demand[net], None, tol[net], excess)
            if not disparity is None:
                print('Disparity of '+str(disparity) + ' in '+net+' at step #'+str(t))
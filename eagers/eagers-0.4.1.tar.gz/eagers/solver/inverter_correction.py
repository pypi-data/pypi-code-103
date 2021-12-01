from eagers.basic.component_output import component_output

def inverter_correction(gen,subnet,forecast,solution,t):
    #temporary check to find errors
    if 'direct_current' in subnet:
        net = 'direct_current'
        acdc_i = [i for i in range(len(gen)) if gen[i]['type']=='ACDCConverter']
        nn = len(subnet['direct_current']['nodes'])
        if len(acdc_i)>0:
            for t in range(len(forecast['timestamp'])):
                net_production, mag_production = component_output(gen,subnet[net],solution['generator_state'],t)
                dc_demand = [0 for i in range(nn)] #op_mat_b['b_eq'][op_mat_b['organize']['balance']['direct_current'][0][0]]
                for an in range(len(subnet[net]['nodes'])):#run through all the nodes in this network
                    for node in subnet[net]['nodes'][an]: #run through aggregated nodes
                        if node in forecast and 'demand' in forecast[node]:
                            dc_demand[an] += forecast[node]['demand'][t]
                dc_error = [net_production[n]-dc_demand[n] for n in range(nn)]
                for n in range(nn): 
                    if abs(dc_error[n])>1E-3:
                        solution['dispatch'][acdc_i[0]][t+1] -= dc_error[n]
                        solution['generator_state'][gen[acdc_i[0]]['name']][t] -= dc_error[n]
                        net_production, mag_production = component_output(gen,subnet['direct_current'],solution['generator_state'],t)
                        dc_error[n] = net_production[n]-dc_demand[n]
                        if abs(dc_error[n])>1E-3:
                            print('A disparity of' +str(dc_error[n]) + 'in direct_current during dispatch_loop optimization')
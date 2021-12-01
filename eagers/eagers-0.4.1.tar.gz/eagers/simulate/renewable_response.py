from eagers.simulate.renewable_output import renewable_output
from eagers.basic.find_gen_node import find_gen_node
from eagers.simulate.adjust_acdc_converter import adjust_acdc_converter

def renewable_response(gen,subnet,solution,actual_data,date):
    renew_i = [i for i in range(len(gen)) if gen[i]['type'] in ('Renewable', 'Solar', 'Wind')]
    if len(renew_i)>0:
        ac_pow = [0 for t in range(len(date))]
        dc_pow = [0 for t in range(len(date))]
        for i, g in enumerate(gen):
            if g['type'] in ('Renewable', 'Solar', 'Wind'):
                gen_network, i_node = find_gen_node(g, subnet)
                location = subnet[gen_network]["location"][i_node]
                renew = renewable_output(g, date, actual_data['weather']['dir_norm_irr'], location)
                for t in range(len(date)):
                    if 'dc' in g['output']:
                        dc_pow[t] += renew[t] - solution['dispatch'][i][t+1] #Positive values mean extra production
                    elif 'e' in g['output']:
                        ac_pow[t] += renew[t] - solution['dispatch'][i][t+1] #Positive values mean extra production
                    solution['dispatch'][i][t+1] = renew[t]
                    solution['generator_state'][g['name']][t] = renew[t]
        for t in range(len(date)):
            adjust_acdc_converter(gen,solution,ac_pow[t],dc_pow[t],t)

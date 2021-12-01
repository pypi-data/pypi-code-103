def all_demands(data,subnet,t_sel):    
    squeeze, t_sel, i_sel = t_sel_indices(data,t_sel)
    # Determine the energy demands in each category at each node.
    d_n_list = list(data.keys())
    non_nodes = ["renewable", "weather", "building", "hydro"]
    for n in non_nodes:
        if n in d_n_list:
            d_n_list.remove(n)
    demand = {}
    for net in subnet['network_names']:
        demand[net] = {}
        n_list = []
        for n in range(len(subnet[net]["nodes"])):
            n_list.extend(subnet[net]["nodes"][n])

        for n in d_n_list:
            if n in n_list:
                demand[net][n] = [0 for t in t_sel]
                if 'demand' in data[n]:
                    for t in range(len(t_sel)):
                        demand[net][n][i_sel[t]] += data[n]['demand'][t_sel[t]]
    squeeze_data(demand,squeeze) 
    return demand

def add_min_building_demand(data,subnet,demand,t_sel):
    if 'building' in data and not data['building'] is None:
        for net in subnet['network_names']:
            for n in range(len(subnet[net]['nodes'])):
                if 'buildings' in subnet[net] and len(subnet[net]['buildings'][n])>0 and not subnet[net]['nodes'][n][0] in demand[net]:
                    if t_sel == None:
                        demand[net][subnet[net]['nodes'][n][0]] = [0 for t in range(len(data['timestamp']))]
                    else:
                        demand[net][subnet[net]['nodes'][n][0]] = 0
        n_b = len(data['building']['Tz_nominal'])
        b_node = {}
        for net in subnet['network_names']:
            b_node[net] = [[] for i in range(n_b)]
            for n in range(len(subnet[net]['nodes'])):
                if 'buildings' in subnet[net] and len(subnet[net]['buildings'][n])>0:
                    for b in subnet[net]['buildings'][n]:
                        b_node[net][b]=subnet[net]['nodes'][n][0]
        for i in range(n_b):   
            if t_sel == None:  
                t_sel = [t for t in range(len(data['timestamp']))]   
                for t in range(len(t_sel)):
                    if 'electrical' in demand:
                        n = b_node['electrical'][i]
                        demand['electrical'][n][t] += data['building']['E0'][t_sel[t]][i]
                    if 'district_cool' in demand:
                        n = b_node['district_cool'][i]
                        demand['district_cool'][n][t] += data['building']['c_min'][t_sel[t]][i]
                    if 'district_heat' in demand:
                        n = b_node['district_heat'][i]
                        demand['district_heat'][n][t] += data['building']['h_min'][t_sel[t]][i]
            else:
                if 'electrical' in demand:
                    demand['electrical'][b_node['electrical'][i]] += data['building']['E0'][t_sel[0]][i]
                if 'district_cool' in demand:
                    demand['district_cool'][b_node['district_cool'][i]] += data['building']['c_min'][t_sel[0]][i]
                if 'district_heat' in demand:
                    demand['district_heat'][b_node['district_heat'][i]] += data['building']['h_min'][t_sel[0]][i]


def subtract_renewable(renewable,subnet,demand):
    if 'electrical' in subnet:
        for n in range(len(subnet['electrical']['nodes'])):
            for e_name in subnet['electrical']['equipment'][n]:
                if e_name in renewable:
                    nn = subnet['electrical']['nodes'][n][0]
                    if nn in demand['electrical']:
                        demand['electrical'][nn] -= renewable[e_name]
                    else:
                        demand['electrical'][nn] = -renewable[e_name]
    if 'direct_current' in subnet:
        for n in range(len(subnet['direct_current']['nodes'])):
            for e_name in subnet['direct_current']['equipment'][n]:
                if e_name in renewable:
                    nn = subnet['direct_current']['nodes'][n][0]
                    if nn in demand['direct_current']:
                        demand['direct_current'][nn] -= renewable[e_name]
                    else:
                        demand['direct_current'][nn] = -renewable[e_name]


def t_sel_indices(data,t_sel):
    squeeze = True
    if t_sel is None:
        t_sel = [t for t in range(len(data['timestamp']))]
        squeeze = False
    i_sel = [i for i in range(len(t_sel))]
    return squeeze, t_sel, i_sel
 
def squeeze_data(demand,squeeze):
    #reduce dimension (only looking for one time step)
    if squeeze:    
        for net in demand:
            for i in demand[net]:
                demand[net][i] = demand[net][i][0]

def count_nodes(subnet,test_data):
    all_data_nodes = []
    for net in subnet['network_names']:
        if net in test_data['nodedata_network_info']:
            all_nodes = []
            net_nodes = []
            data_nodes = [test_data['nodedata_network_info'][net][i]['node'] for i in range(len(test_data['nodedata_network_info'][net]))]
            for i in range(len(subnet[net]['nodes'])):
                ag_nodes = subnet[net]['nodes'][i]
                all_nodes.extend(ag_nodes)
                net_nodes.extend([i for j in range(len(ag_nodes))])
            for j in range(len(data_nodes)):
                n = net_nodes[all_nodes.index(data_nodes[j])]
                if 'demand' in test_data['nodedata_network_info'][net][j]:
                    subnet[net]['load'][n].append(test_data['nodedata_network_info'][net][j]['demand'])
            all_data_nodes.extend(data_nodes)
    return all_data_nodes

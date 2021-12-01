"""Network loading logic.
"""

from eagers.config.network import NETWORK_NAMES, NETWORK_ABBRS


def load_network(network, gen, buildings):
    """Identify generators and lines and their position in the network.
    Organize into sub-networks.
    Group nodes between which transmission losses don't occur.
    Only create lines where transmission losses do occur.
    """

    subnet = {}
    read_network(network)
    n_nodes = len(network)
    node_names = []
    location = []
    network_names = []
    for i in range(n_nodes):
        node_names.append(network[i]['name'])
        if not network[i]['network_name'] in network_names:
            network_names.append(network[i]['network_name'])
        if 'location' in network[i]:
            location.append(network[i]['location'])
        else:
            location.append([])
        
    subnet['network_names'] = network_names
    for j in network_names:
        subnet[j] = {}

    line_number =  0  
    for net in subnet['network_names']:
        subnet[net]['abbreviation'] = NETWORK_ABBRS[NETWORK_NAMES.index(net)]
        subnet[net]['line'] = {}
        subnet[net]['line']['node1'] = []
        subnet[net]['line']['node2'] = []
        subnet[net]['line']['network'] = []
        subnet[net]['line']['number'] = []
        subnet[net]['line']['limit'] = []
        subnet[net]['line']['eff'] = []
        subnet[net]['line']['dir'] = []
        subnet[net]['nodes'] = []
        subnet[net]['location'] = []
        subnet[net]['load'] = []
        subnet[net]['connections'] = []
        for i in range(n_nodes):
            if network[i]['network_name'] == net:
                # First check to see if this node is already a part of
                # subnet node.
                # Nodes with perfect transmission are aggregated into
                # the first node in the name_list that they have a
                # perfect two-way connection with.
                ind = None
                for k in range(len(subnet[net]['nodes'])):
                    if node_names[i] in subnet[net]['nodes'][k]:
                        ind = k
                if ind is None:
                    ind, a_nodes, connect = aggregated_node(network, node_names[i], net, node_names)
                if ind == i:
                    subnet[net]['nodes'].append(a_nodes)  # Add a new subnet node.
                    subnet[net]['location'].append(location[i])
                    subnet[net]['load'].append([])
                    if connect is None:
                        connections = None
                    else:
                        connections = []
                        for j in range(len(connect[1])):
                            if not connect[1][j] in a_nodes:#imperfect transmission, need a line
                                J, c_nodes,_ = aggregated_node(network, connect[1][j], net,node_names)
                                p_connected = node_names[J] #name of node that the connected node will be agregated into if it is perfectly connected to any others
                                connections.append(p_connected)
                                if J>i: #new line connection, otherwise this was handled previously in the reverse direction
                                    eff, limit, direction = line_prop(network,a_nodes, c_nodes, net,node_names)
                                    if direction == 'none': #no transmission (zero efficiency)
                                        pass #do nothing
                                    else:
                                        subnet[net]['line']['dir'].append(direction)
                                        subnet[net]['line']['network'].append(net)
                                        if direction == 'reverse':
                                            subnet[net]['line']['node1'].append(p_connected)
                                            subnet[net]['line']['node2'].append(node_names[i])
                                        else:
                                            subnet[net]['line']['node1'].append(node_names[i])
                                            subnet[net]['line']['node2'].append(p_connected)
                                        subnet[net]['line']['eff'].append(eff)
                                        subnet[net]['line']['limit'].append(limit)
                                        subnet[net]['line']['number'].append(line_number)
                                        line_number += 1
                    subnet[net]['connections'].append(connections)
    subnet = create_obj_lists(network, subnet, node_names, 'equipment')
    if 'hydro' in network_names:
        subnet = add_river_segments(network, gen, subnet, line_number, location, node_names)
    if buildings:
        f_names = [b['filename'] for b in buildings]
        for n in network:
            if not n['buildings'] is None:
                n['buildings'] = [f_names.index(k) for k in n['buildings']]
        subnet = create_obj_lists(network,subnet,node_names,'buildings')
    return subnet


def create_obj_lists(network,subnet,node_names,o_type):
    """Identify objects at each sub-net node (objects can appear in
    multiple sub-nets if they produce heat and power or use water to
    produce electricity, but can only appear at one node in a sub-net.
    """
    for net in subnet['network_names']:
        subnet[net][o_type] = []
        for n in range(len(subnet[net]['nodes'])):
            obj_at_node = []
            node_m = subnet[net]['nodes'][n]
            for k in range(len(node_m)):
                i_net = node_names.index(node_m[k])
                if o_type == 'equipment':
                    if network[i_net]['equipment'] is not None:
                        obj_at_node.extend(network[i_net]['equipment'])
                elif o_type == 'buildings':
                    if network[i_net]['buildings'] is not None:
                        obj_at_node.extend(network[i_net]['buildings'])
            subnet[net][o_type].append(obj_at_node)
    return subnet


def line_prop(network, node_1, node_2, net,node_names):
    """Find the transmission efficiency and limit between 2 connected
    nodes. If one of the nodes is perfectly connected to another node
    there may be more than one pathway connecting them, so aggregate the
    lines.
    """
    def eff_and_limit(eff,limit,new_eff,new_limit,ind):
        if new_limit == float('inf') or limit[ind] == 0:
            eff[ind] = new_eff
            limit[ind] = new_limit
        else:
            weight = new_limit/(limit[ind] + new_limit)
            eff[ind] = (1-weight)*eff[ind] + weight*new_eff
            limit[ind] = limit[ind] + new_limit
        return eff, limit

    eff = [0 for i in range(2)]
    limit = [0 for i in range(2)]
    for j in node_1:
        name_index = node_names.index(j)
        for k in node_2:
            J = node_names.index(k)
            if k in network[name_index]['connections']['node_name'] and j in network[J]['connections']['node_name']:
                #forward direction efficiency and limit
                c = network[name_index]['connections']['node_name'].index(k)
                eff, limit = eff_and_limit(eff,limit,network[name_index]['connections']['line_efficiency'][c],network[name_index]['connections']['line_limit'][c],0)
                #reverse direction efficiency and limit
                c = network[J]['connections']['node_name'].index(j)
                eff, limit = eff_and_limit(eff,limit,network[J]['connections']['line_efficiency'][c],network[J]['connections']['line_limit'][c],1)
    if eff[0]==0 and eff[1]>0:
        direction = 'reverse'
        eff = [eff[1]]
        limit = [limit[1]]
    elif eff[0]>0 and eff[1]==0:
        direction = 'forward'
        eff = [eff[0]]
        limit = [limit[0]]
    elif eff[0]==0 and eff[1]==0:
        direction = 'none'
        eff = []
        limit = []
    else:
        direction = 'dual'
    return eff, limit, direction


def aggregated_node(network, node, net, node_names):
    # Any connected nodes with perfect bi-directional transfer are
    # aggregated into the node earliest in the list of names.
    # This function finds which node in the list that is
    name_index = node_names.index(node)
    a_nodes = [node]
    connect = None
    if network[name_index]['connections']['node_name'] != None:
        nc = len(network[name_index]['connections']['node_name'])
        connect = [[node for i in range(nc)],network[name_index]['connections']['node_name']]
        k = 0
        while k<len(connect[1]):
            if not connect[1][k] in a_nodes: #avoid looking at connections to nodes already in agregated node
                eff,_,_  = line_prop(network,a_nodes, [connect[1][k]],net,node_names)
                if len(eff)==2 and min(eff)==1 and not net == 'hydro': #perfect bi-directional energy transfer, hydro lines are river segments, can't agregate
                    J = node_names.index(connect[1][k])
                    a_nodes.append(connect[1][k])
                    new_connect = [nn for nn in network[J]['connections']['node_name'] if nn not in a_nodes]
                    connect[0].extend([connect[1][k] for i in range(len(new_connect))])
                    connect[1].extend(new_connect)
                    del connect[0][k]
                    del connect[1][k]
                    k -= 1
                    if J<name_index:
                        name_index =J#keep lowest number (index in list of node names)
            k += 1
        if len(connect[1])==0:
            connect = None
    return name_index, a_nodes, connect


def add_river_segments(network,gen,subnet,line_number,location,node_names):
    subnet['hydro'] = {}
    subnet['hydro']['nodes']  = []
    subnet['hydro']['abbreviation'] = 'w'
    subnet['hydro']['location'] = []
    subnet['hydro']['connections'] = []
    subnet['hydro']['load'] = []
    subnet['hydro']['line']['number'] = []
    subnet['hydro']['line']['minimum'] = []
    subnet['hydro']['line']['limit'] = []
    subnet['hydro']['equipment'] = []
    subnet['hydro']['line']['node1'] = []
    subnet['hydro']['line']['node2'] = []
    subnet['hydro']['line']['network'] = []
    subnet['hydro']['line']['time'] = []

    num_gen = len(gen)
    gen_names = []
    for i in range(num_gen):
        gen_names.append(gen[i]['name'])

    hydro_node = []
    down_river = []
    for i in range(len(network)):
        if network[i]['network_name'] == 'hydro':#add a new subnet node
            line_number = line_number+1
            gen_at_node = []
            equip = network[i]['equipment']
            for j in equip:
                gen_i = gen_names.index(j)
                if gen[gen_i].type()== 'HydroStorage':
                    gen_at_node.append(gen_i)
            subnet['hydro']['nodes'].append(network[i]['name'])
            subnet['hydro']['location'].append(location[i])
            subnet['hydro']['connections'].append(network[i]['hydro']['connections'])
            subnet['hydro']['load'].append([]) #not empty if there is a water diversion for irrigation etc
            subnet['hydro']['line']['number'].append(line_number)
            subnet['hydro']['line']['minimum'].append(network[i]['hydro']['instream_flow'])
            subnet['hydro']['line']['limit'].append(float('inf'))
            subnet['hydro']['equipment'].append(gen_at_node)
            subnet['hydro']['line']['network'].append('hydro')
            hydro_node.append(network[i]['name']) #node names of the upriver node (origin of line segment)
            connect_nodes = network[i]['connections']['node_name']
            if not connect_nodes is None:
                dr_node = node_names.index(connect_nodes[0])
                down_river.append(network[dr_node]['name']) #node names of the downriver node (end of line segment)
                subnet['hydro']['line']['node1'].append(network[i]['name'])
                subnet['hydro']['line']['node2'].append(network[dr_node]['name'])
                subnet['hydro']['line']['time'].append(network[i]['hydro']['time_to_sea'] - network[dr_node]['hydro']['time_to_sea']) #transit time from current river to downstream river
            else:#last dam before the sea
                subnet['hydro']['line']['node1'].append(network[i]['name'])
                subnet['hydro']['line']['node2'].append(None)
                subnet['hydro']['line']['time'].append(network[i]['hydro']['time_to_sea']) #no downstream dam
    #following indexing helps locate upstream nodes during load_matrices, and forecast_hydro
    subnet['hydro']['up_river'] = []
    for i in range(len(subnet['hydro']['nodes'])):
        subnet['hydro']['up_river'].append(down_river.index(hydro_node[i])) #finds which nodes the current node is downstream of
    return subnet

def read_network(network):
    ''' interpret network  information'''
    con = ['node_name','line_limit','line_efficiency']
    for net_i in network:
        if not 'equipment' in net_i:
            net_i['equipment'] = None
        if not 'buildings' in net_i:
            net_i['buildings'] = None
        if 'location' not in net_i:
            net_i['location'] = {'latitude': net_i['latitude'],'longitude': net_i['longitude'],'time_zone': net_i['time_zone']}
        if any(['Connexn' in h for h in list(net_i.keys())]):
            net_i['connections'] = {'node_name': [], 'line_limit': [], 'line_efficiency': []}
            headers = [h for h in list(net_i.keys()) if 'Connexn' in h]
            for h in headers:
                for c in con:
                    if c in h:
                        net_i['connections'][c].append(net_i.pop(h))
        else:
            net_i['connections'] = {'node_name': None, 'line_limit': None, 'line_efficiency': None}
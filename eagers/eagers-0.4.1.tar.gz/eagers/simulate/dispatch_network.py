from eagers.solver.ecos_qp import ecos_qp

def dispatch_network(names,subnet,production,demand,request,marginal,capacity,constrained):
    '''Performs a quadratic optimization to find the shortage/excess of demand on the network
    and the most cost effective node to add energy production
    If constrained is true it treats any buildings as constant loads, otherwise it considers building flexibility'''
    qp = build_net_optimization(names,subnet,production,demand,request,marginal,capacity,constrained)
    x, feasible = ecos_qp(qp['h'], qp['f'], qp['a'], qp['b'], qp['a_eq'], qp['b_eq'], qp['ub'], qp['lb'], qp['x_keep'], qp['r_keep'], qp['req_keep'])
    if feasible == 0:
        if constrained:
            ##TODO return imbalance by node
            thermal = sum(x[-len(subnet['nodes']):]) #sum of slack nodes is the net energy imbalance on the network
        else:
            building_thermal = x[:len(names['buildings'])]
            thermal = [0 for i in range(len(subnet['nodes']))]
            for i in range(len(names['buildings'])):
                for n in range(len(subnet['nodes'])):
                    if 'buildings' in subnet and len(subnet['buildings'][n])>0:
                        if i in subnet['buildings'][n]:
                            thermal[n] += building_thermal[i]*1000
    else:
        if constrained:
            thermal = 0 #no energy imbalance to redistribute
        else:
            thermal = [j*1000 for j in request['nominal']] #stick with original guess from optimization (will result in imbalance somewhere)
        print('Simulation error: Cannot find feasible network solution.')
    return thermal 

def build_net_optimization(names,subnet,production,demand,request,marginal,capacity,constrained):
    x_l = len(names['buildings']) + sum([2 if s == 'dual' else 1 for s in subnet['line']['dir']]) + len(subnet['nodes']) #building thermal, line flow , and slack states
    nn = len(subnet['nodes'])
    qp = {}
    qp['h'] = [0 for j in range(x_l)]
    qp['f'] = [0 for j in range(x_l)]
    qp['x_keep'] = [True for j in range(x_l)]
    qp['a'] = []
    qp['b'] = []
    qp['r_keep'] = []
    qp['a_eq'] = [[0 for j in range(x_l)] for i in range(nn)]
    qp['b_eq'] = [0 for i in range(nn)]
    qp['req_keep'] = [True for j in range(nn)]
    qp['lb'] = [0 for j in range(x_l)]
    qp['ub'] = [0 for j in range(x_l)]
    for n in range(nn):
        if 'buildings' in subnet and len(subnet['buildings'][n])>0:
            ##TODO consider normalizing by building water loop thermal capacity rather than nominal load
            for j in subnet['buildings'][n]:
                qp['a_eq'][n][j] = request['nominal'][j]
                if constrained:
                    qp['lb'][j] = 1
                    qp['ub'][j] = 1 + 1e-8
                else:
                    qp['h'][j] = 1
                    qp['lb'][j] = request['minimum'][j]/request['nominal'][j]
                    qp['ub'][j] = request['maximum'][j]/request['nominal'][j]
    ind = len(names['buildings'])
    node_names = [subnet['nodes'][j][0] for j in range(nn)]
    for i in range(len(subnet['line']['dir'])):
        j = node_names.index(subnet['line']['node1'][i])
        k = node_names.index(subnet['line']['node2'][i])
        qp['a_eq'][j][ind] = -1 #energy leaving node 1
        qp['a_eq'][k][ind] = subnet['line']['eff'][0] #energy arriving at node 2
        qp['ub'][ind] = subnet['line']['limit'][0]
        ind += 1
        if subnet['line']['dir'] == 'dual':
            qp['a_eq'][k][ind] = -1 #energy leaving node 2
            qp['a_eq'][j][ind] = subnet['line']['eff'][1] #energy arriving at node 1
            qp['ub'][ind] = subnet['line']['limit'][1]
            ind += 1
    for n in range(nn):
        qp['a_eq'][n][ind] = 1 #slack variable for production at this node
        qp['b_eq'][n] = production[n]
        if subnet['nodes'][n][0] in list(demand.keys()):
            qp['b_eq'][n] -= demand[subnet['nodes'][n][0]]
        qp['f'][ind] = marginal[n]
        qp['ub'][ind] = capacity[n]
        if not constrained:
            qp['f'][ind] += 1e3 #add cost so it uses building flexibility first
        ind += 1
    return qp
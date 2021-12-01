"""Fix infeasible result.
"""

from copy import copy, deepcopy

from eagers.solver.ecos_qp import ecos_qp


def fix_infeasible(qp):
    qp_new = {}
    # Copy 1-D lists and deepcopy nested lists.
    qp_new['h'] = copy(qp['h'])
    qp_new['f'] = copy(qp['f'])
    qp_new['a'] = deepcopy(qp['a'])
    qp_new['b'] = copy(qp['b'])
    qp_new['a_eq'] = deepcopy(qp['a_eq'])
    qp_new['b_eq'] = copy(qp['b_eq'])
    qp_new['ub'] = copy(qp['ub'])
    qp_new['lb'] = copy(qp['lb'])
    qp_new['x_keep'] = copy(qp['x_keep'])
    qp_new['r_keep'] = copy(qp['r_keep'])
    qp_new['req_keep'] = copy(qp['req_keep'])
    n_s = qp['organize']['n_s']
    node_bal = qp['organize']['balance']
    bal = dict(num = [], row = [], net = [], time = [], node = [])
    b = 0
    f_name = list(qp['organize']['balance'].keys())
    for net in f_name:
        for j,row in enumerate(node_bal[net]):
            bal['num'].extend([b+t for t in range(n_s)])
            bal['row'].extend(row) 
            bal['net'].extend([net] * n_s)
            bal['time'].extend([t+1 for t in range(n_s)])
            node_name = qp['network'][net]['node_names'][j]
            bal['node'].extend([node_name for t in range(n_s)])
            b= bal['num'][-1]+1
    s_add = sum([sum([len(n) for n in node_bal[net]]) for net in f_name])
    z_add = [0 for i in range(s_add)]
    r = len(qp_new['a'])
    r_eq = len(qp_new['a_eq'])
    x_l = len(qp_new['f'])
    qp_new['h'].extend(z_add)
    max_c = 1e3 * max(qp_new['f'])
    qp_new['f'].extend([max_c for i in range(s_add)])
    for rq in range(r_eq):
        qp_new['a_eq'][rq].extend(z_add)
    for rnq in range(r):
        qp_new['a'][rnq].extend(z_add)
    qp_new['lb'].extend(z_add)
    qp_new['ub'].extend([1e10 for i in range(s_add)])
    qp_new['x_keep'].extend([True for i in range(s_add)])
    for j in range(len(bal['row'])):
        qp_new['a_eq'][bal['row'][j]][x_l+bal['num'][j]] = 1

    x, feasible = ecos_qp(qp_new['h'], qp_new['f'], qp_new['a'], qp_new['b'], qp_new['a_eq'], qp_new['b_eq'], qp_new['ub'], qp_new['lb'], qp_new['x_keep'], qp_new['r_keep'], qp_new['req_keep'])
    x = x[:len(qp['f'])]
    if feasible != 0:
        print('Some additional contraints making problem infeasible.\n' \
            + 'Tried adding infinite sources.')
    else:
        node_makeup = [[val,i] for i,val in enumerate(x[x_l:]) if abs(val)>1e-3]
        n_mku = len(node_makeup)
        if n_mku > 0:
            if n_mku <= 4:
                # Display:
                # - The energy type for which production was
                #   insufficient,
                # - The node at which this occurred,
                # - The time interval into the future at which this
                #   occurred.
                for i in range(n_mku):
                    j = bal['num'].index(node_makeup[i][1])
                    net = bal['net'][j]
                    v = node_makeup[i][0]
                    t = bal['time'][j]
                    node = bal['node'][j]
                    print(
                        f'Short production capacity of {net} '
                        f'By approximately {v}'
                        f'at node {node} '
                        f'at time interval {t}.'
                    )
            else:
                short_net = dict(net = [],ti = [])
                for i in range(n_mku):
                    j = bal['num'].index(node_makeup[i][1])
                    if not bal['net'][j] in short_net:
                        short_net['net'].append(bal['net'][j])
                        short_net['ti'].append(1)
                    else:
                        n = short_net['net'].index(bal['net'][j])
                        short_net['ti'][n] +=1
                for f in range(len(short_net['net'])):
                    net = short_net['net'][f]
                    n = short_net['ti'][f]
                print(f'Short production capacity of {net}')
    return x, feasible

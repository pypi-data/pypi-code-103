from eagers.config.network import NETWORK_NAMES, NETWORK_ABBRS


def case_marginal(dispatch, gen, qp, v_h):
    # Find all ouptuts to have marginal cost of.
    out_names = list(qp['organize']['balance'].keys())
    outs = []
    marginal = {}
    for k in range(len(NETWORK_NAMES)):
        if NETWORK_NAMES[k] in out_names:
            outs.append(NETWORK_ABBRS[k])
            marginal[NETWORK_ABBRS[k]] = None

    # If storage, use marginal cost from dispatch of storage.
    ac_dc = None
    n_g = len(gen)
    for i in range(n_g):
        if gen[i]['type'] == 'ACDCConverter':
            ac_dc = gen[i]
    for i in range(n_g):
        if gen[i]['type'] == 'ElectricStorage':
            s = qp['indices'][i][0][0]
            mar = dispatch[i] * qp['h'][s] + qp['f'][s]
            if 'e' in outs:
                if not ac_dc is None and 'dc' in gen[i]['output']:
                    marginal['e'] = mar / abs(ac_dc['output']['e'][0][-1])
                else:
                    marginal['e'] = mar
            if 'dc' in outs:
                if not ac_dc is None and 'e' in gen[i]['output']:
                    marginal['dc'] = mar / ac_dc['output']['dc'][0][0]
                else:
                    marginal['dc'] = mar
        if gen[i]['type'] == 'ThermalStorage':
            s = qp['indices'][i][0][0]
            mar = dispatch[i] * qp['h'][s] + qp['f'][s]
            f = list(gen[i]['output'].keys())
            marginal[f[0]] = mar
    # Otherwise find marginal cost of each active generator with this
    # output and take max.
    for k, out in enumerate(outs):
        if marginal[out] is None:
            for i in range(n_g):
                d = dispatch[i]
                s = qp['indices'][i][0]
                if d > 0 and 'output' in gen[i] and not s is None:
                    f = list(gen[i]['output'].keys())
                    if out in f and all([output>0 for output in gen[i]['output'][out][-1]]):
                        j = 0
                        while d > 0 and j < len(s):
                            seg = min([qp['ub'][s[j]], d])
                            mar = dispatch[i] * qp['h'][s[j]] + qp['f'][s[j]]
                            d -= seg
                            j += 1
                        if mar == 0:
                            s2 = list(marginal.keys())
                            for k2 in s2:
                                if not marginal[k2] is None and k2 in gen[i]['output']:
                                    mar = max(-output * marginal[k2] for output in gen[i]['output'][k2][-1])
                                    break
                        if gen[i]['type'] == 'CombinedHeatPower':
                            if out == 'h':
                                mar = mar * 0.3
                            elif v_h and (out == 'e' or out == 'dc'):
                                mar = mar * 0.7
                        if marginal[out] is None:
                            marginal[out] = mar
                        else:
                            marginal[out] = max([marginal[outs[k]], mar])
        if marginal[out] is None:
            marginal[out] = 1  # Should only reach this if there is no storage an demand = 0 (only way for zero generators to be active).
    return marginal

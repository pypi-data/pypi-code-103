"""Result template logic.
"""

def result_template(all_data_nodes,names, zones, pl):
    """Returns an empty dictionary with the necessary result fields."""
    weather_headers = ['glo_horz_irr','dir_norm_irr','dif_horz_irr','t_dryb','t_dewp','rh','pres_pa','wdir','wspd','tot_cld','opq_cld']
    f_build = ['avg_T', 'electric', 'cooling', 'heating', 'Tzone', 'return_', 'supply']
    res = dict(
        timestamp = [],
        nodedata = dict((k, {}) for k in all_data_nodes),
        weather = dict((k, []) for k in weather_headers),
        building= dict((k,dict((k,[]) for k in f_build)) for k in names['buildings']),
        fluid_loop = dict((fl,[]) for fl in names['fluid_loop']),
        generator_state = dict((g,[]) for g in names['components']),
        storage_state = dict((n,[]) for n in names['storage']),
        hydro_spill = dict((h,[]) for h in names['hydro']),
        hydro_outflow = dict((h,[]) for h in names['hydro']),
        line_flow = dict((l,[]) for l in names['lines']),
        line_loss = dict((l,[]) for l in names['lines']),
    )
    for i,n in enumerate(names['buildings']):
        res['building'][n]['Tzone'] = [[] for j in range(zones[i])]
        res['building'][n]['return_'] = [[] for j in range(pl[i])]
        res['building'][n]['supply'] = [[] for j in range(pl[i])]
    return res

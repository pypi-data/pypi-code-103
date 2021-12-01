"""Logic for checking whether AC/DC conversion capabilities are properly
outfitted for a project.

Functions:
check_ac_dc
"""

def check_ac_dc(components, buildings, test_data):
    """Check whether AC/DC conversion capabilities are correctly
    configured for the given set of components, buildings, and test
    data.
    """
    has_dc = False
    has_ac = False
    has_ac_dc = False
    need_ac = False
    need_dc = False

    for comp in components:
        if comp['type'] == 'ACDCConverter':
            has_ac_dc = True
        else:
            if 'output' in comp:
                if 'direct current' in comp['output']:
                    has_dc = True
                if 'electricity' in comp['output']:
                    has_ac = True
            if 'source' in comp:
                if 'direct_current' in comp['source']:
                    has_dc = True
                if 'electricity' in comp['source']:
                    has_ac = True
        if comp['type'] == 'HydroStorage':
            has_ac = True
    if ('nodedata' in test_data \
            and len(test_data['nodedata'].tablenames) > 0
            and any('e' in test_data['nodedata'].colnames(tn)
                for tn in test_data['nodedata'].tablenames)):
        need_ac = True
    if ('nodedata' in test_data \
            and len(test_data['nodedata'].tablenames) > 0
            and any('dc' in test_data['nodedata'].colnames(tn)
                for tn in test_data['nodedata'].tablenames)):
        need_dc = True
    if buildings:
        need_ac = True
        for b in buildings:
            if 'dc_loads' in b:
                need_dc = True

    if not has_ac_dc and (need_ac and not has_ac) or (need_dc and not has_dc):
        # Add default AC/DC converter model to list of components.
        qpform = dict(
            # state is AC power transferred to DC power.
            states=[['a']],
            output=dict(e=[[-1]],dc=[[1]]),
            a=dict(ub=1e12, lb=-1e12, f=0, h=0,))
        components.append(qpform)    
    return components

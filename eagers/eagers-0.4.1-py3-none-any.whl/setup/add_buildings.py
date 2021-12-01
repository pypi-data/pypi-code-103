def add_buildings(buildings,subnet,gen):
    """identify what subnet node of electrical heating and cooling the building is on,
    and if there are chillers/heaters connected, disengage the internal HVAC
    """
    nb = len(buildings)
    if nb == 0:
        qpform = []
    else:
        template = {'name':[],'location':[],'electrical_subnet_node':[],'district_heat_subnet_node':[],'heating':[],'district_cool_subnet_node':[],'cooling':[]}
        qpform = [template for i in range(nb)]
        for net in subnet['network_names']:
            if 'buildings' in subnet[net]:
                nodes = subnet[net]['nodes']
                for n in range(len(nodes)):
                    b_num =subnet[net]['buildings'][n]
                    for i in b_num:
                        qpform[i]['name'] = []
                        if net == 'electrical':
                            qpform[i]['electrical_subnet_node'] = n
                            qpform[i]['location'] = subnet['electrical']['location'][n]
                        elif net == 'district_heat':
                            qpform[i]['district_heat_subnet_node'] = n
                            equip = subnet['district_heat']['equipment'][n]
                            for j in range(len(equip)):
                                if gen[j]['type'] in ['heater','chp_generator']:
                                    qpform[i]['heating'] = True
                            if not subnet['district_heat']['connections'][n] is None: #connected to heaters at a different node
                                qpform[i]['heating'] = True
                        elif net == 'district_cool':
                            qpform[i]['district_cool_subnet_node'] = n
                            equip = subnet['district_cool']['equipment'][n]
                            for j in range(len(equip)):
                                if gen[j]['type'] == 'chiller':
                                    qpform[i]['cooling'] = True
                            if not subnet['district_cool']['connections'][n] is None: #connected to chillers at a different node
                                qpform[i]['cooling'] = True
    return qpform
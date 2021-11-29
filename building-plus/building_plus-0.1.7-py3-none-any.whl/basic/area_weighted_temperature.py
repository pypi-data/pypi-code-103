def area_weighted_temperature(building,Tzone):
    nz = len(building['zones']['name'])
    hvac = [0 for i in range(nz)]
    for i in building['zone_controls']:
        if building['zone_controls'][i]['type']=='Thermostat':
            z = building['zones']['name'].index(building['zone_controls'][i]['zone'])
            hvac[z] = 1
    A = [building['zones']['floor_area'][z]*building['zones']['multiplier'][z]*hvac[z] for z in range(nz)]
    T = sum([Tzone[z]*A[z] for z in range(nz)])/sum(A)
    return T
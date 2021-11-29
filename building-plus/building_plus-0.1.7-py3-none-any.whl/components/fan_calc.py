def fan_calc(fan,air,avail):
    air_density = 1.204  #kg/m^3
    air_out={}
    flow = min(air['m_dot']/air_density,fan['flow_rate']*avail)
    if flow>0:
        if fan['type']=='ConstantVolume' or fan['type']=='OnOff':
            PLF = 1 #should be determined by partial loading of other components in HVAC loop, see page 1040
            RTF = flow/fan['flow_rate']/PLF
            Q_tot = RTF*fan['flow_rate']*fan['pressure_rise']/fan['fan_efficiency'] # m^3/s * Pa = N*m/s = W
        elif fan['type']=='VariableVolume':
            f_flow = flow/fan['flow_rate']
            f_pl = fan['a1'] + fan['a2']*f_flow + fan['a3']*f_flow**2 + fan['a4']*f_flow**3 + fan['a5']*f_flow**4
            Q_tot = f_pl*fan['flow_rate']*fan['pressure_rise']/fan['fan_efficiency'] # m^3/s * Pa = N*m/s = W
        elif fan['type']=='SystemModel':  #designed to replace other types
            pass
        Q_shaft = fan['motor_efficiency']*Q_tot
        Q_to_air = Q_shaft + (Q_tot-Q_shaft)*fan['motor_frac'] #W
        cp = (1006 + 1860*air['w'])*air_density
        air_out['Tdb'] = air['Tdb'] + Q_to_air/(cp*flow)
        air_out['w'] = air['w']+0
        air_out['h'] = air['h'] + Q_to_air/(flow*air_density) #all h in J/kg
        air_out['flow'] = flow+0
        air_out['m_dot'] = flow*air_density
    else:
        air_out = {}
        for k in air:
            air_out[k] = air[k]+0
        Q_tot = 0
        Q_to_air = 0
    return air_out,Q_tot,Q_to_air
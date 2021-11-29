

def water_equipment(we,profile,T_mains,T_tank):    
    if we['cold_supply_temperature_schedule'] == None:
        T_cold = T_mains
    else:
        T_cold = profile[we['cold_supply_temperature_schedule']]
    if T_tank==None:
        T_hot =  profile[we['hot_supply_temperature_schedule']]
    else:
        T_hot = T_tank 
    if we['target_temperature_schedule']==None:
        T_target = T_mains
    else:
        T_target = min(T_hot,profile[we['target_temperature_schedule']])
    den_water = 997  #kg/m^3
    m_mix = we['peak_flow']*profile[we['flow_schedule']]*den_water
    m_hot = m_mix*(T_target- T_cold)/(T_hot - T_cold)
    m_cold = m_mix-m_hot
    flow = m_hot
    T_return = T_cold
    return flow,T_return,T_target,T_hot,T_cold
def half_loop_tank(volume,den,flow,T_old,pump,T_inlet,dt):
    if flow>0:
        Cp_water = 4186  #J/kg*K
        e = 2.718281828459 # natural logarithm
        M_tank = volume*den #Mass of fluid in tank
        A = (flow*Cp_water*T_inlet+pump)/(flow*Cp_water) #Watts / J/s*K
        T_new = (T_old - A)*e**(-flow*Cp_water*dt/(M_tank*Cp_water)) + A 
        # T_average = (T_old - A)*e**(-flow*Cp_water*dt/(2*M_tank*Cp_water)) + A #temperature halfway through time period
        T_average = M_tank/(flow*dt)*(T_old - A)*(1-e**(-flow*dt/M_tank)) + A #Reference manual page 468
    else:
        T_new = T_old+0
        T_average = T_old+0
    return T_new,T_average
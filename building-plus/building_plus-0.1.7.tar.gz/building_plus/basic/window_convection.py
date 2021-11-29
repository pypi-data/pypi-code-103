import numpy as np

def window_convection(windows,T_int,T_i,cp_air):
    ## correlations for changing tilt angle (page 362)
    ## note temperatures must be in Kelvin!!
    air_density = 1.204 #kg/m^3 %standard air density (1.204 kg/m3) adjusted for the local barometric pressure (standard barometric pressure corrected for altitude, ASHRAE 1997 HOF pg. 6.1).
    g = 9.81 #m/s^2 gravity
    n_win = len(windows['name'])
    deltaT = [T_int[i]-T_i[i] for i in range(n_win)]
    nusselt = [0 for i in range(n_win)]
    h = [0 for i in range(n_win)]
    tilt = []
    for i in range(n_win):
        if abs(windows['normal'][i][2])>0:
            tilt.append(abs(float(np.degrees(np.arctan((windows['normal'][i][0]**2+windows['normal'][i][1]**2)**.5/windows['normal'][i][2])))))
        else:
            tilt.append(90)
    for i in range(n_win):
        if deltaT[i]>0:
            tilt[i] = 180 - tilt[i]
    T_mf = [T_i[i] + 0.25*deltaT[i] for i in range(n_win)]
    mu = [3.723e-6 + 4.94e-8*T_mf[i] for i in range(n_win)]
    lam = [2.873e-3 + 7.76e-5*T_mf[i] for i in range(n_win)]
    Ra_h = [air_density**2*windows['height'][i]**3*g*cp_air[i]*abs(deltaT[i])/(T_mf[i]*mu[i]*lam[i]) for i in range(n_win)]
    Ra_cv = []
    for i in range(n_win):
        if tilt[i]<=179:
            Ra_cv.append(2.5e5*float(np.exp(.72*tilt[i])/np.sin(np.radians(tilt[i])))**(1/5))
        else:
            Ra_cv.append(0)

    for i in range(n_win):
        if tilt[i]<15:
            nusselt[i] = 0.13*Ra_h[i]**(1/3)
        elif tilt[i]>=15 and tilt[i]<=90 and Ra_h[i]<=Ra_cv[i]:
            nusselt[i] = 0.56*(Ra_h[i]*float(np.sin(np.radians(tilt[i]))))**(1/4)
        elif tilt[i]>=15 and tilt[i]<=90 and Ra_h[i]>Ra_cv[i]:
            nusselt[i] = 0.13*(Ra_h[i]**(1/3) - Ra_cv[i]**(1/3)) + 0.56*(Ra_cv[i]*float(np.sin(np.radians(tilt[i]))))**(1/4)
        elif tilt[i]>90 and tilt[i]<=179:
            nusselt[i] = 0.56*(max(min(Ra_h[i],1e11),1e5)*float(np.sin(np.radians(tilt[i]))))**(1/4)
        elif tilt[i]>179:
            nusselt[i] = 0.58*(min(Ra_h[i],1e11))**(1/5)
        h[i] = nusselt[i]*(lam[i]/windows['height'][i])
    return h
import numpy as np
import copy

def lin_load_increase(T_eff,load,hvac_elec):
    # s = sorted(range(len(T_eff)), key=lambda k: T_eff[k])
    # n = len(s)
    # T_eff = [T_eff[s[i]] for i in range(n)]
    # load = [load[s[i]] for i in range(n)]
    # hvac_elec = [hvac_elec[s[i]] for i in range(n)]

    #interpolate to find when load starts increasing
    T = [T_eff[0],T_eff[-1]]
    UA = [0,0]
    hvac2elec = 0
    min_load = min(load)
    if not all([load[i] == load[0] for i in range(len(load))]):
        i = 0
        while i<len(T_eff)-1 and load[i]>min_load:
            i+=1
        i_min = copy.copy(i)
        while i<len(T_eff)-1 and load[i]<=min_load:
            i+=1
        i_max = copy.copy(i)

        ##Parameters for increase in heating/cooling with decrease in temperature
        if i_min == 1:
            UA[0] = (load[0] - min_load)/(T_eff[1] - T_eff[0])
            T[0] = T_eff[1] + min_load/UA[0] #intercept with given slope
        elif i_min!=0:
            p = np.polyfit(T_eff[:i_min],load[:i_min],1)
            if p[0]<0:
                UA[0] = float(-p[0])
                T[0] = -float(p[1])/float(p[0]) #intercept with given slope

        #Parameters for increase in heating/cooling with increase in temperature
        if i_max == len(T_eff)-2:
            UA[1] = (load[-1] - min_load)/(T_eff[-1] - T_eff[i_max])
            T[1] = T_eff[-1] - min_load/UA[1] #intercept with given slope
        elif i_max!=len(T_eff)-1:
            p = np.polyfit(T_eff[i_max:],load[i_max:],1)
            if p[0]>0:
                UA[1] = float(p[0])
                T[1] = -float(p[1])/float(p[0]) #intercept with min_load
    #Average slope of electric load vs. heating/cooling
        sindex = sorted(range(len(load)), key=lambda k: load[k])
        sort_load = [load[i] for i in sindex]
        sort_elec = [hvac_elec[i] for i in sindex]
        q = np.polyfit(sort_load,sort_elec,1)
        if q[0]>1e-6:
            hvac2elec = float(q[0])

    return T,UA,min_load,hvac2elec
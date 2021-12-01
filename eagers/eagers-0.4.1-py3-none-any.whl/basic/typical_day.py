import datetime as dt

from eagers.basic.hdf5 import DatetimeFloatConverter as DFC

def typical_day(timestamp, data):
    timestamp = DFC.f2d_arr2lst(timestamp)#convert float back to datetime
    x = [[[] for j in range(24)] for i in range(12)]
    z = [[[] for j in range(24)] for i in range(12)]
    for i, t in enumerate(timestamp):
        x[t.month][t.hour].append(data[i])
    for m in range(12):
        if all([len(x[m][h])>0 for h in range(24)]): #data exists for every hour
            for h in range(24):
                if any(x[m][h]):
                    z[m][h] = sum(x[m][h])/len(x[m][h]) #average at this hour
                else:
                    z[m][h] = 0
    not_empty = [m2 for m2 in range(12) if len([h2 for h2 in range(24) if len(z[m2][h2])>0])>0]
    for m in range(12):
        if not m in not_empty:
            a = [min([abs(m-m2),abs(m-12 - m2),abs(m+12-m2)]) for m2 in not_empty]
            minpos = a.index(min(a)) #find nearest non-empty month
            z[m] = z[not_empty[minpos]]    
        not_empty2 = [h2 for h2 in range(24) if len(z[m][h2])>0]
        for h in range(24):
            if not h in not_empty2:
                a = [min([abs(h-h2),abs(h-24 - h2),abs(h+24-h2)]) for h2 in not_empty2]
                minpos = a.index(min(a)) #find nearest non-empty hour
                z[m][h] = z[m][not_empty2[minpos]]
    return z
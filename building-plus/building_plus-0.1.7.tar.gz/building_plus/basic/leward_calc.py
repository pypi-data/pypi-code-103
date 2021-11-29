import numpy as np

def leward_calc(wind,surf_normal):
    threshold = 100 #degrees difference between wind and surface normal to be considered leward
    surf = [np.degrees(np.arctan2(surf_normal[i][0],surf_normal[i][1])) for i in range(len(surf_normal))]
    wind2 = wind-360
    leward = []
    for i in range(len(surf_normal)):
        if surf_normal[i][2]==1 or surf_normal[i][2]==-1:
            leward.append(True) 
        elif abs(wind-surf[i])>threshold and abs(wind2-surf[i])>threshold:
            leward.append(True)  
        else:
            leward.append(False)
    return leward
from typing import List, Tuple, Union
import numpy as np

def fast_hist_func(array: List[Union[int, float]], 
              bins: int) -> Tuple[List[int], List[float]]:
    sorted_arr = (array)
    mn = min(sorted_arr)
    mx = max(sorted_arr)
    interval = (np.linspace(mn,mx, num = bins + 1))
    bins_width = (mx - mn)/bins
    counted = [0]*(bins)
    
    for i in range(0, len(array)):
        if (i < len(interval) - 1):
             interval[i] = interval[i] + bins_width/2
                
        ind = int(np.floor((bins)*(sorted_arr[i] - mn)/
                               (mx - mn)))
        if ind == bins:
            counted[-1]+=1
        else:
             counted[ind]+=1  

    return counted, interval[:-1]
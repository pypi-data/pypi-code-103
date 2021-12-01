import os
import numpy as np

def get_imbalance_weight(root_dir, n_classes):
    file_list = os.listdir(root_dir)
    result = np.zeros(n_classes)
    for file in file_list:
        if 'npz' in file:
            seg = np.load(os.path.join(root_dir, file))['y']
            id, num = np.unique(seg, return_counts = True)
            result[id.astype(int)] += num
    
    
    return (result.sum()/result).astype(float)



def get_maximum_patch_size(root_dir, n_classes):
    file_list = os.listdir(root_dir)
    result = np.array((0,0,0))
    npz_list = []
    pkl_list = []
    
    for file in file_list:
        if 'npz' in file:
            npz_list.append(file)
        
        elif 'pkl' in file:
            pkl_list.append(file)
        
    
    npz_list = sorted(npz_list)
    pkl_list = sorted(pkl_list)

    for i in range(len(npz_list)):
        seg = np.load(os.path.join(root_dir, file))['y']
        result = np.max((result,np.array(seg.shape)), axis = 0)
    
    return result
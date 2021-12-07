import numpy as np
import torch
import time

def is_overlap(points, current_point):
    if points[current_point[0], current_point[1], current_point[2], current_point[3]] != 0:
        return True
    else:
        return False

"""
def get_random_sample(points, candidates, batch_index):
    n_candidates = len(candidates[0])
    index = np.random.choice(np.arange(n_candidates), size = (n_candidates,), replace = False)
    p_batch = batch_index
    i = 0
    x = candidates[-3][index[i]]
    y = candidates[-2][index[i]]
    z = candidates[-1][index[i]]
    
    while is_overlap(points, current_point=[p_batch, x, y, z]) and i < len(index) - 1:
        i += 1
        p_batch = batch_index
        x = candidates[-3][index[i]]
        y = candidates[-2][index[i]]
        z = candidates[-1][index[i]]
    
    point = [p_batch, x, y, z]
    if not is_overlap(points, point):
        points[point[0], point[1], point[2], point[3]] = 1
    return points
"""

"""

def get_random_sample(points, candidates, batch_index):
    n_candidates = len(candidates[0])
    index = np.random.choice(np.arange(n_candidates), size = (1,), replace = False)

    x = candidates[-3][index[0]]
    y = candidates[-2][index[0]]
    z = candidates[-1][index[0]]
    
    point = [batch_index, x, y, z]
    points[point[0], point[1], point[2], point[3]] = 1
    return points
"""
def point_sampler(target, output = None, positive_points = None, negative_points = None, first = False):
    # target shpae, prev_seg => (batch, x, y, z)
    # positive_points, negative_points => (n, 4) [(batch_index, x_index, y_index, z_index), ...과 같은 방식], 입력 시 Transpose를 이용해 쉽게 넣을 수 있다.
    # 초기값 세팅
    bs, x, y, z = target.shape
    
    id_time = time.time()
    if type(output) == type(None):
        prev_seg = torch.zeros(target.shape).to(target.device.index)
    
    else:
        prev_seg = (output[:, 0] > 0.5).long()
        
    if type(positive_points) == type(None):
        positive_points = torch.zeros(target.shape).to(target.device.index)
    
    if type(negative_points) == type(None):
        negative_points = torch.zeros(target.shape).to(target.device.index)

    print("id time", time.time()- id_time)
    
    for batch_index in range(bs):
        if (prev_seg[batch_index] != target[batch_index]).sum() == 0:
            # Ground truth = Predicted Segmentation
            continue

        elif prev_seg[batch_index].sum() >= target[batch_index].sum():
            # negative sampling
            cand_time = time.time()
            candidates = torch.where((target * (prev_seg != target)) == 0)
            n_candidates = len(candidates[0])
            index = torch.randint(low = 0, high = n_candidates, size = (1,))
            negative_points[batch_index, candidates[-3][index], candidates[-2][index],candidates[-1][index]] = 1
            print("find cand", time.time()- cand_time)

        elif prev_seg[batch_index].sum() < target[batch_index].sum():
            # positive sampling
            cand_time = time.time()
            candidates = torch.where((target * (prev_seg != target)) == 1)
            n_candidates = len(candidates[0])
            index = torch.randint(low = 0, high = n_candidates, size = (1,))
            positive_points[batch_index, candidates[-3][index], candidates[-2][index],candidates[-1][index]] = 1
            print("find cand", time.time()- cand_time)

    if first:
        return positive_points, negative_points


def get_filter(arr_size, r):
    center = np.array(arr_size)//2
    coords = np.ogrid[:arr_size[0], :arr_size[1], :arr_size[2]]
    distance = np.sqrt((coords[0] - center[0])**2 + (coords[1]-center[1])**2 + (coords[2]-center[2])**2) 
    return torch.tensor((distance <= r*1.1)).unsqueeze(0).unsqueeze(0).long()



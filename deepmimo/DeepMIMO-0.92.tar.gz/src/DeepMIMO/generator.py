# -*- coding: utf-8 -*-
"""
@author: Umut Demirhan
"""

from DeepMIMO.raytracing import read_raytracing
from DeepMIMO.construct_deepmimo import generate_MIMO_channel
import DeepMIMO.consts as c
import numpy as np
import os
from DeepMIMO.utils import safe_print

def generate_data(params):
    # If dynamic scenario
    if 'dyn' in params[c.PARAMSET_SCENARIO]:
        scene_list = np.arange(params[c.PARAMSET_DYNAMIC][c.PARAMSET_DYNAMIC_FIRST]-1, params[c.PARAMSET_DYNAMIC][c.PARAMSET_DYNAMIC_LAST])
        num_of_scenes = len(scene_list)
        dataset = []
        for scene_i in range(num_of_scenes):
            scene = scene_list[scene_i]
            params[c.PARAMSET_SCENARIO_FIL] = os.path.join(
                                        os.path.abspath(params[c.PARAMSET_DATASET_FOLDER]), 
                                        params[c.PARAMSET_SCENARIO],
                                        'scene_' + str(scene), # 'scene_i' folder
                                        params[c.PARAMSET_SCENARIO]
                                        )
            print('\nScene %i/%i' %(scene_i+1, num_of_scenes))
            dataset.append(generate_scene_data(params))
    # If static scenario
    else:
        params[c.PARAMSET_SCENARIO_FIL] = os.path.join(
                                    os.path.abspath(params[c.PARAMSET_DATASET_FOLDER]), 
                                    params[c.PARAMSET_SCENARIO], 
                                    params[c.PARAMSET_SCENARIO]
                                    )
        dataset = generate_scene_data(params)
    return dataset
        
def generate_scene_data(params):
    num_active_bs = len(params[c.PARAMSET_ACTIVE_BS])
    dataset = [{c.DICT_UE_IDX: dict(), c.DICT_BS_IDX: dict(), c.OUT_LOC: None} for x in range(num_active_bs)]
    
    for i in range(num_active_bs):
        bs_indx = params[c.PARAMSET_ACTIVE_BS][i]
        
        safe_print('\nBasestation %i' % bs_indx)
        
        safe_print('\nUE-BS Channels')
        dataset[i][c.DICT_UE_IDX], dataset[i][c.OUT_LOC] = read_raytracing(bs_indx, params, user=True)
        dataset[i][c.DICT_UE_IDX][c.OUT_CHANNEL] = generate_MIMO_channel(dataset[i][c.DICT_UE_IDX][c.OUT_PATH], 
                                                                                                 params, 
                                                                                                 params[c.PARAMSET_ANT_BS], 
                                                                                                 params[c.PARAMSET_ANT_UE])
        
        if params[c.PARAMSET_BS2BS]:
            safe_print('\nBS-BS Channels')
            
            dataset[i][c.DICT_BS_IDX], _ = read_raytracing(bs_indx, params, user=False)
            dataset[i][c.DICT_BS_IDX][c.OUT_CHANNEL] = generate_MIMO_channel(dataset[i][c.DICT_BS_IDX][c.OUT_PATH], 
                                                                                 params, 
                                                                                 params[c.PARAMSET_ANT_BS], 
                                                                                 params[c.PARAMSET_ANT_BS])

    return dataset

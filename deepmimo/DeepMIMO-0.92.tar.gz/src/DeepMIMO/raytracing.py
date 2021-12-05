# -*- coding: utf-8 -*-
"""
@author: Umut Demirhan
"""

import scipy.io
import numpy as np
from tqdm import tqdm
import DeepMIMO.consts as c
from DeepMIMO.utils import safe_print

def read_raytracing(bs_id, params, user=True):
      
    scenario_files = params[c.PARAMSET_SCENARIO_FIL]
    params[c.PARAMSET_SCENARIO_PARAMS] = load_scenario_params(scenario_files)
    
    
    if user:
        generation_idx = find_users_from_rows(params) # Active User IDX
    else:
        generation_idx = params[c.PARAMSET_ACTIVE_BS]-1 # Active BS IDX
        
    ray_data = load_ray_data(scenario_files, bs_id, user=user)
    data = extract_data_from_ray(ray_data, generation_idx, params)
    
    bs_loc = load_bs_loc(scenario_files, bs_id)
    return data, bs_loc

def load_bs_loc(scenario_files, bs_id):
    TX_loc_file = scenario_files + '.TX_Loc.mat'
    data = scipy.io.loadmat(TX_loc_file)
    return data[list(data.keys())[3]].astype(float)[bs_id-1, 1:4]

def load_scenario_params(scenario_files):
    file_loc = scenario_files + c.LOAD_FILE_SP_EXT # Scenario parameters file
    data = scipy.io.loadmat(file_loc)
    scenario_params = {c.PARAMSET_SCENARIO_PARAMS_CF: data[c.LOAD_FILE_SP_CF].astype(float).item(),
                       c.PARAMSET_SCENARIO_PARAMS_TX_POW: data[c.LOAD_FILE_SP_TX_POW].astype(float).item(),
                       c.PARAMSET_SCENARIO_PARAMS_NUM_BS: data[c.LOAD_FILE_SP_NUM_BS].astype(int).item(),
                       c.PARAMSET_SCENARIO_PARAMS_USER_GRIDS: data[c.LOAD_FILE_SP_USER_GRIDS].astype(int)
                       }
    return scenario_params

# Loads the user and basestation dataset files
def load_ray_data(scenario_files, bs_id, user=True):
    # File Types and Directories
    file_list = c.LOAD_FILE_EXT
    
    if user:
        file_loc = [scenario_files +  '.%i.' % bs_id + c.LOAD_FILE_EXT_UE[0], 
                    scenario_files +  '.%i.' % bs_id + c.LOAD_FILE_EXT_UE[1], 
                    scenario_files +  '.%i.' % bs_id + c.LOAD_FILE_EXT_UE[2], 
                    scenario_files +  '.%i.' % bs_id + c.LOAD_FILE_EXT_UE[3], 
                    scenario_files +  '.' + c.LOAD_FILE_EXT_UE[4]]
    else: # Basestation
        file_loc = [scenario_files +  '.%i.' % bs_id + c.LOAD_FILE_EXT_BS[0], 
                    scenario_files +  '.%i.' % bs_id + c.LOAD_FILE_EXT_BS[1], 
                    scenario_files +  '.%i.' % bs_id + c.LOAD_FILE_EXT_BS[2], 
                    scenario_files +  '.%i.' % bs_id + c.LOAD_FILE_EXT_BS[3], 
                    scenario_files +  '.' + c.LOAD_FILE_EXT_BS[4]]
    
    # Load files
    ray_data = dict.fromkeys(file_list)
    for i in range(len(file_list)-1):
        data = scipy.io.loadmat(file_loc[i])
        ray_data[file_list[i]] = data[list(data.keys())[3]].reshape(-1) # 3rd key is the data
    i += 1
    data = scipy.io.loadmat(file_loc[i])
    ray_data[file_list[i]] = data[list(data.keys())[3]] # 3rd key is the data

    return ray_data

# Extracts the information to a dictionary from the loaded data file
# for the users given in IDs, and with maximum number of paths
def extract_data_from_ray(ray_data, ids, params):
    
    path_verifier = PathVerifier(params)
    
    num_channels = len(ids)
    
    pointer = 1 # First user ID
    
    # Generate empty user array of dictionaries
    path_dict = {c.OUT_PATH_NUM: 0,
                 c.OUT_PATH_DOD_PHI: [],
                 c.OUT_PATH_DOD_THETA: [],
                 c.OUT_PATH_DOA_PHI: [],
                 c.OUT_PATH_DOA_THETA: [],
                 c.OUT_PATH_PHASE: [],
                 c.OUT_PATH_TOA: [],
                 c.OUT_PATH_DS: [],
                 c.OUT_PATH_RX_POW: [],
                 c.OUT_PATH_ACTIVE: []
                 }
    data = {c.OUT_PATH: [dict(path_dict) for j in range(len(ids))],
                c.OUT_LOS : np.zeros(num_channels, dtype=int),
                c.OUT_LOC : np.zeros((num_channels, 3)),
                c.OUT_DIST : np.zeros(num_channels),
                c.OUT_PL : np.zeros(num_channels)
                }
    
    j = 0
    for user in tqdm(range(max(ids)+1), desc='Reading ray-tracing'):
        pointer += 1 # Number of Paths
        num_paths_available = int(ray_data[c.LOAD_FILE_EXT[0]][pointer]) # DoD file
        pointer += 1 # First Path
        if user in ids:
            num_paths_read = min(num_paths_available, params[c.PARAMSET_NUM_PATHS])
            path_limited_data_length = num_paths_read*4;
                
            if num_paths_available>0:
                data[c.OUT_PATH][j] = load_variables(num_paths_read=num_paths_read, 
                                                     path_DoD=ray_data[c.LOAD_FILE_EXT[0]][(pointer):(pointer+path_limited_data_length)], 
                                                     path_DoA=ray_data[c.LOAD_FILE_EXT[1]][(pointer):(pointer+path_limited_data_length)], 
                                                     path_CIR=ray_data[c.LOAD_FILE_EXT[2]][(pointer):(pointer+path_limited_data_length)], 
                                                     path_verifier=path_verifier, 
                                                     params=params)
                
            data[c.OUT_LOS][j] = ray_data[c.LOAD_FILE_EXT[3]][user+1]
            data[c.OUT_LOC][j] = ray_data[c.LOAD_FILE_EXT[4]][user, 1:4]
            data[c.OUT_DIST][j] = ray_data[c.LOAD_FILE_EXT[4]][user, 4]
            data[c.OUT_PL][j] = ray_data[c.LOAD_FILE_EXT[4]][user, 5]
            j += 1
            
        pointer += num_paths_available*4
        
    path_verifier.notify()
    return data

# Split variables into a dictionary
def load_variables(num_paths_read, path_DoD, path_DoA, path_CIR, path_verifier, params):
    user_data = dict()
    user_data[c.OUT_PATH_NUM] = num_paths_read
    user_data[c.OUT_PATH_DOD_PHI] = path_DoD[1::4]
    user_data[c.OUT_PATH_DOD_THETA] = path_DoD[2::4]
    user_data[c.OUT_PATH_DOA_PHI] = path_DoA[1::4]
    user_data[c.OUT_PATH_DOA_THETA] = path_DoA[2::4]
    user_data[c.OUT_PATH_PHASE] = path_CIR[1::4]
    user_data[c.OUT_PATH_TOA] = path_CIR[2::4]
    user_data[c.OUT_PATH_DS] = user_data[c.OUT_PATH_TOA] - min(user_data[c.OUT_PATH_TOA])
    user_data[c.OUT_PATH_RX_POW] = dbm2pow(path_CIR[3::4] + 30 - params[c.PARAMSET_SCENARIO_PARAMS][c.PARAMSET_SCENARIO_PARAMS_TX_POW])
    user_data[c.OUT_PATH_ACTIVE] = path_verifier.verify_path(user_data[c.OUT_PATH_DS], user_data[c.OUT_PATH_RX_POW])
    return user_data

# Generate the set of users to be activated
def find_users_from_rows(params):

    def rand_perm_per(vector, percentage):
        if percentage == 1: return vector
        num_of_subsampled = round(len(vector)*percentage)
        if num_of_subsampled < 1: num_of_subsampled = 1 
        subsampled = np.arange(len(vector))
        np.random.shuffle(subsampled)
        subsampled = vector[subsampled[:num_of_subsampled]]
        return subsampled
    
    def get_user_ids(row, grids):
        row_prev_ids = np.sum((row > grids[:, 1])*(grids[:, 1] - grids[:, 0] + 1)*grids[:, 2])
        row_cur_ind = (grids[:, 1] >= row) * (row >= grids[:, 0])
        row_curr_ids = ((row - grids[:, 0])*grids[:, 2])[row_cur_ind]
        user_ids = row_prev_ids + row_curr_ids + np.arange(grids[:, 2][row_cur_ind])
        return user_ids
    
    np.random.seed(1001)
    
    grids = params[c.PARAMSET_SCENARIO_PARAMS][c.PARAMSET_SCENARIO_PARAMS_USER_GRIDS]
    rows = np.arange(params[c.PARAMSET_USER_ROW_FIRST], params[c.PARAMSET_USER_ROW_LAST]+1)
    active_rows = rand_perm_per(rows, params[c.PARAMSET_USER_ROW_SUBSAMP])
    
    user_ids = np.array([], dtype=int)
    for row in active_rows:
        user_ids_row = get_user_ids(row, grids)
        user_ids_row = rand_perm_per(user_ids_row, params[c.PARAMSET_USER_SUBSAMP])
        user_ids = np.concatenate((user_ids, user_ids_row))
    
    user_ids = np.sort(user_ids)
    return user_ids
    
# Determine active paths with the given configurations
# (For OFDM, only the paths within DS are activated)
class PathVerifier:
    def __init__(self, params):
        self.params = params
        Ts = 1 / (params[c.PARAMSET_OFDM][c.PARAMSET_OFDM_BW]*c.PARAMSET_OFDM_BW_MULT)
        self.CP_duration = np.floor(params[c.PARAMSET_OFDM][c.PARAMSET_OFDM_CP]
                                    *params[c.PARAMSET_OFDM][c.PARAMSET_OFDM_SC_NUM]) * Ts
        self.max_DS = 0
        self.path_ratio = []
    
    def verify_path(self, DS, power):
        if self.params[c.PARAMSET_FDTD]: # OFDM CH
            self.max_DS = np.maximum(np.max(DS), self.max_DS)
            path_activation = DS < self.CP_duration
            self.path_ratio.append( sum(power[path_activation])/sum(power) )
            return path_activation
        else: # TD CH
            return np.ones(len(DS))
        
    def notify(self):
        if self.params[c.PARAMSET_FDTD]: # IF OFDM
            if self.max_DS > self.CP_duration:
                print('Maximum delay spread %.2e is larger than the OFDM cyclic prefix %.2e'%(self.max_DS, self.CP_duration))
                safe_print('Any path over the cyclic prefix duration are deactivated.. %.3f%% of the total power is preserved.'%(np.mean(self.path_ratio)*100))

def dbm2pow(val):
    return 10**(val/10 - 3)
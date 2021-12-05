# -*- coding: utf-8 -*-
"""
@author: Umut Demirhan
"""

DICT_UE_IDX = 'user'
DICT_BS_IDX = 'basestation'

# NAME OF PARAMETER VARIABLES
PARAMSET_DATASET_FOLDER = 'dataset_folder'
PARAMSET_SCENARIO = 'scenario'
PARAMSET_DYNAMIC = 'dynamic_settings'
PARAMSET_DYNAMIC_FIRST = 'first_scene'
PARAMSET_DYNAMIC_LAST = 'last_scene'

PARAMSET_NUM_PATHS = 'num_paths'
PARAMSET_ACTIVE_BS = 'active_BS'
PARAMSET_USER_ROW_FIRST = 'user_row_first'
PARAMSET_USER_ROW_LAST = 'user_row_last'
PARAMSET_USER_ROW_SUBSAMP = 'row_subsampling'
PARAMSET_USER_SUBSAMP = 'user_subsampling'

PARAMSET_BS2BS = 'enable_BS2BS'
PARAMSET_FDTD = 'OFDM_channels' # TD/OFDM

PARAMSET_OFDM = 'OFDM'
PARAMSET_OFDM_SC_NUM = 'subcarriers'
PARAMSET_OFDM_SC_LIM = 'subcarriers_limit'
PARAMSET_OFDM_SC_SAMP = 'subcarriers_sampling'
PARAMSET_OFDM_CP = 'cyclic_prefix_ratio'
PARAMSET_OFDM_BW = 'bandwidth'
PARAMSET_OFDM_BW_MULT = 1e9 # Input is GHz, multiply by this
PARAMSET_OFDM_PULSE = 'pulse_shaping'
PARAMSET_OFDM_RCOS_ROLLOFF = 'rolloff_factor'
PARAMSET_OFDM_UPSAMPLING = 'upsampling_factor'
PARAMSET_OFDM_LPF = 'low_pass_filter_ideal'

PARAMSET_ANT_BS = 'bs_antenna'
PARAMSET_ANT_UE = 'ue_antenna'
PARAMSET_ANT_SHAPE = 'shape'
PARAMSET_ANT_SPACING = 'spacing'

# INNER VARIABLES
PARAMSET_SCENARIO_FIL = 'scenario_files'
#PARAMSET_ACTIVE_USERS = 'active_user_idx'

# SCENARIO PARAMS
PARAMSET_SCENARIO_PARAMS = 'scenario_params'
PARAMSET_SCENARIO_PARAMS_CF = 'carrier_freq'
PARAMSET_SCENARIO_PARAMS_TX_POW = 'tx_power'
PARAMSET_SCENARIO_PARAMS_NUM_BS = 'num_BS'
PARAMSET_SCENARIO_PARAMS_USER_GRIDS = 'user_grids'

# OUTPUT VARIABLES
OUT_CHANNEL = 'channel'
OUT_PATH = 'paths'
OUT_LOS = 'LoS'
OUT_LOC = 'location'
OUT_DIST = 'distance'
OUT_PL = 'pathloss'

OUT_PATH_NUM = 'num_paths'
OUT_PATH_DOD_PHI = 'DoD_phi'
OUT_PATH_DOD_THETA = 'DoD_theta'
OUT_PATH_DOA_PHI = 'DoA_phi'
OUT_PATH_DOA_THETA = 'DoA_theta'
OUT_PATH_PHASE = 'phase'
OUT_PATH_TOA = 'ToA'
OUT_PATH_DS = 'DS'
OUT_PATH_RX_POW = 'power'
OUT_PATH_ACTIVE = 'active_paths'

# FILE LISTS - raytracing.load_ray_data()
LOAD_FILE_EXT = ['DoD', 'DoA', 'CIR', 'LoS', 'Loc']
LOAD_FILE_EXT_UE = ['DoD.mat', 'DoA.mat', 'CIR.mat', 'LoS.mat', 'Loc.mat']
LOAD_FILE_EXT_BS = ['DoD.BSBS.mat', 'DoA.BSBS.mat', 'CIR.BSBS.mat', 'LoS.BSBS.mat', 'BSBS.RX_Loc.mat']

# TX LOCATION FILE VARIABLE NAME - load_scenario_params()
LOAD_FILE_TX_LOC = 'TX_Loc_array_full'

# SCENARIO PARAMS FILE VARIABLE NAMES - load_scenario_params()
LOAD_FILE_SP_EXT = '.params.mat'
LOAD_FILE_SP_CF = 'carrier_freq'
LOAD_FILE_SP_TX_POW = 'transmit_power'
LOAD_FILE_SP_NUM_BS = 'num_BS'
LOAD_FILE_SP_USER_GRIDS = 'user_grids'

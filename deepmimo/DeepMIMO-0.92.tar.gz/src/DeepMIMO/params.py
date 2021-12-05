# -*- coding: utf-8 -*-
"""
@author: Umut Demirhan
"""

import numpy as np
import DeepMIMO.consts as c

def default_params():
    params = {c.PARAMSET_DATASET_FOLDER: './Raytracing_scenarios', # To be implemented
              c.PARAMSET_SCENARIO:'O1_60',
              
              # Dynamic scenario scene selection
              c.PARAMSET_DYNAMIC: {
                  c.PARAMSET_DYNAMIC_FIRST: 1,
                  c.PARAMSET_DYNAMIC_LAST: 5
                  },
              
              # Maximum # of paths to be loaded
              c.PARAMSET_NUM_PATHS: 10,
              
              # Active Basestation IDs
              c.PARAMSET_ACTIVE_BS: np.array([1, 2]), # To be implemented
              
              # Selected user rows
              c.PARAMSET_USER_ROW_FIRST: 1,
              c.PARAMSET_USER_ROW_LAST: 2,
              
              # Subsampling
              c.PARAMSET_USER_ROW_SUBSAMP: 1,
              c.PARAMSET_USER_SUBSAMP: 1,
              
              c.PARAMSET_BS2BS: 1, # To be implemented
              
              c.PARAMSET_FDTD: 1 , 
              # OFDM if 1 
              # Time domain if 0.
              # In time domain, the channel of 
              # RX antennas x TX antennas x Number of available paths is generated.
              # Each matrix of RX ant x TX ant represent the response matrix of that path.
              
              # OFDM Parameters
              c.PARAMSET_OFDM: {
                  c.PARAMSET_OFDM_SC_NUM: 512, # Number of total subcarriers
                  
                  c.PARAMSET_OFDM_SC_LIM: 32, # Take first subcarriers
                  c.PARAMSET_OFDM_SC_SAMP: 1, # Sample the subcarriers
                  # The selected subcarriers are given by range(0, subcarriers_limit, subcarriers_sampling)
                  
                  c.PARAMSET_OFDM_CP: 0.1,
                  
                  c.PARAMSET_OFDM_BW: 0.05, #GHz
                  
                  # 0: No pulse shaping (DeepMIMOv1)
                  # 1: Sinc
                  # 2: Raised Cosine
                  # Function of t: Custom pulse shape
                  c.PARAMSET_OFDM_PULSE: 0,
                  c.PARAMSET_OFDM_RCOS_ROLLOFF: 0.5,
                  c.PARAMSET_OFDM_UPSAMPLING: 50.,
                  
                  # Receive Low Pass Filter
                  # 0: No Low Pass Filter - Delta Function 
                  # 1: Ideal (Rectangular) Low Pass Filter - Sinc Function
                  c.PARAMSET_OFDM_LPF: 1
                  },
              
              # BS Antenna Parameters
              c.PARAMSET_ANT_BS: {
                  c.PARAMSET_ANT_SHAPE: np.array([1, 4, 4]), # Antenna dimensions in X - Y - Z
                  c.PARAMSET_ANT_SPACING: 0.5
                  },
              
              # UE Antenna Parameters
              c.PARAMSET_ANT_UE: {
                  c.PARAMSET_ANT_SHAPE: np.array([1, 2, 2]), # Antenna dimensions in X - Y - Z
                  c.PARAMSET_ANT_SPACING: 0.5
                  }
              }
    return params
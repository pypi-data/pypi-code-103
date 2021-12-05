# -*- coding: utf-8 -*-
"""
@author: Umut Demirhan
"""

import DeepMIMO.consts as c
from scipy.signal import convolve
import numpy as np
from tqdm import tqdm
import types

def generate_MIMO_channel(raydata, params, tx_ant_params, rx_ant_params):
    
    bandwidth = params[c.PARAMSET_OFDM][c.PARAMSET_OFDM_BW] * c.PARAMSET_OFDM_BW_MULT
    
    kd_tx = 2*np.pi*tx_ant_params[c.PARAMSET_ANT_SPACING]
    kd_rx = 2*np.pi*rx_ant_params[c.PARAMSET_ANT_SPACING]
    Ts = 1/bandwidth
    subcarriers = np.arange(0, params[c.PARAMSET_OFDM][c.PARAMSET_OFDM_SC_LIM], params[c.PARAMSET_OFDM][c.PARAMSET_OFDM_SC_SAMP])
    path_gen = OFDM_PathGenerator(params[c.PARAMSET_OFDM], subcarriers)
    
    M_tx = np.prod(tx_ant_params[c.PARAMSET_ANT_SHAPE])
    ant_tx_ind = ant_indices(tx_ant_params[c.PARAMSET_ANT_SHAPE])
    
    M_rx = np.prod(rx_ant_params[c.PARAMSET_ANT_SHAPE])
    ant_rx_ind = ant_indices(rx_ant_params[c.PARAMSET_ANT_SHAPE])
    
    if  params[c.PARAMSET_FDTD]:
        channel = np.zeros((len(raydata), M_rx, M_tx, len(subcarriers)), dtype = np.csingle)
    else:
        channel = np.zeros((len(raydata), M_rx, M_tx, params[c.PARAMSET_NUM_PATHS]), dtype = np.csingle)
        
    for i in tqdm(range(len(raydata)), desc='Generating channels'):
        
        if raydata[i][c.OUT_PATH_NUM]==0:
            continue
        
        array_response_TX = array_response(ant_tx_ind, 
                                           raydata[i][c.OUT_PATH_DOD_THETA], 
                                           raydata[i][c.OUT_PATH_DOD_PHI], kd_tx)
        array_response_RX = array_response(ant_rx_ind, 
                                           raydata[i][c.OUT_PATH_DOA_THETA], 
                                           raydata[i][c.OUT_PATH_DOA_PHI], kd_rx)
        
        if  params[c.PARAMSET_FDTD]: # OFDM
            path_const = path_gen.generate(raydata[i][c.OUT_PATH_RX_POW].reshape(-1, 1), 
                                           (raydata[i][c.OUT_PATH_DS]/Ts).reshape(-1, 1), 
                                           raydata[i][c.OUT_PATH_PHASE].reshape(-1,1))
            
            # The next step is to be defined
            if params[c.PARAMSET_OFDM][c.PARAMSET_OFDM_PULSE] == 0:
                channel[i] = np.sum(array_response_RX[:, None, None, :] * np.conj(array_response_TX)[None, :, None, :] * path_const.T[None, None, :, :], axis=3)
            else:
                channel[i] = np.sum(array_response_RX[:, None, None, :] * np.conj(array_response_TX)[None, :, None, :] * path_const.T[None, None, :, :], axis=3)@path_gen.delay_to_OFDM
        
        else: # TD channel
            channel[i, :, :, :raydata[i][c.OUT_PATH_NUM]] = array_response_RX[:, None, :] * np.conj(array_response_TX)[None, :, :] * (np.sqrt(raydata[i][c.OUT_PATH_RX_POW]) * np.exp(1j*np.deg2rad(raydata[i][c.OUT_PATH_PHASE])))[None, None, :]

    return channel

def array_response(ant_ind, theta, phi, kd):
    gamma = array_response_phase(theta, phi, kd)
    return np.exp(ant_ind@gamma.T)
    
def array_response_phase(theta, phi, kd):
    gamma_x = -1j*kd*np.sin(np.deg2rad(theta))*np.cos(np.deg2rad(phi))
    gamma_y = -1j*kd*np.sin(np.deg2rad(theta))*np.sin(np.deg2rad(phi))
    gamma_z = -1j*kd*np.cos(np.deg2rad(theta))
    return np.vstack([gamma_x, gamma_y, gamma_z]).T
 
def ant_indices(panel_size):
    gamma_x = np.tile(np.arange(panel_size[0]), panel_size[1]*panel_size[2])
    gamma_y = np.tile(np.repeat(np.arange(panel_size[1]), panel_size[0]), panel_size[2])
    gamma_z = np.repeat(np.arange(panel_size[2]), panel_size[0]*panel_size[1])
    return np.vstack([gamma_x, gamma_y, gamma_z]).T

class OFDM_PathGenerator:
    def __init__(self, OFDM_params, subcarriers):
        if OFDM_params[c.PARAMSET_OFDM_PULSE] == 0: # No Pulse Shaping
            self.generate = getattr(self, 'no_pulse_shaping')
        else: # Pulse Shaping
            self.generate = getattr(self, 'with_pulse_shaping')
            
            if OFDM_params[c.PARAMSET_OFDM_PULSE] == 1: # SINC
                self.pulse_fn = getattr(np, 'sinc')
                
            elif OFDM_params[c.PARAMSET_OFDM_PULSE] == 2: # RAISED COS
                self.pulse_fn = getattr(self, 'raised_cosine')
                self.rolloff_factor = OFDM_params[c.PARAMSET_OFDM_RCOS_ROLLOFF]
                
            elif isinstance(OFDM_params[c.PARAMSET_OFDM_PULSE], types.FunctionType): # CUSTOM
                self.pulse_fn = OFDM_params[c.PARAMSET_OFDM_PULSE]
            else:
                raise NotImplementedError
            
                
        self.subcarriers = subcarriers
        self.total_subcarriers = OFDM_params[c.PARAMSET_OFDM_SC_NUM]
        
        self.cyclic_prefix_length =  np.floor(OFDM_params[c.PARAMSET_OFDM_CP]*OFDM_params[c.PARAMSET_OFDM_SC_NUM])
        self.delay_d = np.arange(self.cyclic_prefix_length)
        self.conv_interval = max(10., self.cyclic_prefix_length)
        self.upsampling_factor = float(OFDM_params[c.PARAMSET_OFDM_UPSAMPLING]) # Fixed
        self.t = np.arange(-self.conv_interval, self.cyclic_prefix_length + 6, 1/self.upsampling_factor).reshape(1, -1) # Constant
        
        # Low Pass Filter Selection
        if OFDM_params[c.PARAMSET_OFDM_LPF]:
            self.LPF = np.sinc(self.t).reshape(-1) # Fixed
        else:
            self.LPF = self.delta_func(self.t).reshape(-1) # Fixed
        
        self.downsample = (self.upsampling_factor*np.arange(self.conv_interval*2, self.conv_interval*2+self.cyclic_prefix_length)).astype(int)
        self.delay_to_OFDM = np.exp(-1j*2*np.pi/self.total_subcarriers*np.outer(self.delay_d, self.subcarriers))
        
    def no_pulse_shaping(self, power, delay, phase):
        return np.sqrt(power/self.total_subcarriers)*np.exp(1j*(np.deg2rad(phase) - (2*np.pi/self.total_subcarriers)*np.outer(delay, self.subcarriers) ))
    
    def with_pulse_shaping(self, power, delay, phase):
        
        # Ignore the paths over CP
        paths_over_CP = (delay >= self.cyclic_prefix_length)
        power[paths_over_CP] = 0
        delay[paths_over_CP] = self.cyclic_prefix_length
        
        # Pulse - LPF convolution and channel generation
        pulse = self.pulse_fn(self.t-delay)
        res = np.zeros((pulse.shape[0], len(self.LPF)*2-1), dtype=np.complex64)
        for i in range(len(power)):
            res[i, :] = convolve(pulse[i, :], self.LPF)
        res /= np.max(np.abs(res), 1, keepdims=True) # Power normalization
        res = res[:, self.downsample]
        res *= np.sqrt(power/self.total_subcarriers) * np.exp(1j*np.deg2rad(phase)) # Power scaling
        return res
    
    def raised_cosine(self, t):
        t_roll = self.rolloff_factor*t
        t_ind = np.logical_or(t_roll == 1/2, t_roll == -1/2)
        t_roll[t_ind] = 0
        rcos_filter = np.sinc(t)*np.cos(np.pi*t_roll)/(1-np.square(2*t_roll))
        rcos_filter[t_ind] = (np.pi/4)*np.sinc(1/(2*self.rolloff_factor))
        return rcos_filter
    
    def delta_func(self, t):
        pulse = np.zeros(t)
        pulse[t==0] = 1
        return pulse
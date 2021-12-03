#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#%%
def Planck():
    
    """
    ========== DESCRIPTION ==========
    
    This function return the Planck constant

    ========== VALIDITE ==========
    
    Always

    ========== FROM ==========
    
    Wikipedia : https://en.wikipedia.org/wiki/Planck_constant 

    ========== INPUT ==========
        
    ========== OUTPUT ==========
    
    [Planck]
    	The Planck constant [kg].[m]**(2).[s]**(-1)
    
    ========== STATUS ==========     
    
    Status : Checked

    """
    
    ################## MODULES ###############################################
    
    ################## CONDITIONS ############################################
            
    ################## INITIALISATION ####################################
        
    return  6.626070040e-34  

#%% 
def ReducedPlanck():
    
    """
    ========== DESCRIPTION ==========
    
    This function return the reduced Planc constant

    ========== VALIDITY ==========
    
    Always

    ========== FROM ==========
    
    Wikipedia : https://en.wikipedia.org/wiki/Planck_constant 

    ========== INPUT ==========
        
    ========== OUTPUT ==========
    
    [ReducedPlanck]
    	The reduced Planck constant [kg].[m]**(2).[s]**(-1)
    
    ========== STATUS ==========     
    
    Status : Checked

    """
    
    ################## MODULES ###############################################
    
    import numpy as np
    import cryopy
    
    ################## CONDITIONS ############################################
            
    ################## INITIALISATION ####################################
        
    return  cryopy.Constant.Planck()/2/np.pi 

#%%
def Gas():
    
    """
    ========== DESCRIPTION ==========
    
    This function return the gas constant

    ========== VALIDITY ==========
    
    Always

    ========== FROM ==========
    
    Wikipedia : https://en.wikipedia.org/wiki/Gas_constant

    ========== INPUT ==========
        
    ========== OUTPUT ==========
    
    [Gas]
    	The Gas constant in [J].[K]**(-1).[mol]**(-1)
    
    ========== STATUS ==========     
    
    Status : Checked

    """
    
    ################## MODULES ###############################################
    
    ################## CONDITIONS ############################################
            
    ################## INITIALISATION ####################################
        
    return  8.31446261815324 

#%%
def Boltzmann():
    
    """
    ========== DESCRIPTION ==========
    
    This function return the Boltzmann constant

    ========== VALIDITY ==========
    
    Always

    ========== FROM ==========
    
    Wikipedia : https://en.wikipedia.org/wiki/Boltzmann_constant

    ========== INPUT ==========
        
    ========== OUTPUT ==========
    
    [Boltzmann]
    	The Boltzmann constant in [J].[K]**(-1)
    
    ========== STATUS ==========     
    
    Status : Checked

    """
    
    ################## MODULES ###############################################
    
    ################## CONDITIONS ############################################
            
    ################## INITIALISATION ####################################
        
    return  1.38064852e-23

#%%
def Avogadro():
    
    """
    ========== DESCRIPTION ==========
    
    This function return the Avogadro constant

    ========== VALIDITY ==========
    
    Always

    ========== SOURCE ==========
    
    Wikipedia : https://en.wikipedia.org/wiki/Avogadro_constant

    ========== INPUT ==========
        
    ========== OUTPUT ==========
    
    [Avogadro]
    	The Avogadro constant in [mol]**(-1)
    
    ========== STATUS ==========     
    
    Status : Checked

    """
    
    ################## MODULES ###############################################
    
    ################## CONDITIONS ############################################
            
    ################## INITIALISATION ####################################
        
    return  6.022140857e23

#%% 
def SpeedOfLight():
    
    """
    ========== DESCRIPTION ==========
    
    This function return the speed of light in vacuum

    ========== VALIDITY ==========
    
    Only in Vacuum

    ========== FROM ==========
    
    Wikipedia : https://en.wikipedia.org/wiki/Speed_of_light

    ========== INPUT ==========
        
    ========== OUTPUT ==========
    
    [SpeedOfLight]
    	The speed of light in [m].[s]**(-1)
    
    ========== STATUS ==========     
    
    Status : Checked

    """
    
    ################## MODULES ###############################################
    
    ################## CONDITIONS ############################################
            
    ################## INITIALISATION ####################################
        
    return  299792458


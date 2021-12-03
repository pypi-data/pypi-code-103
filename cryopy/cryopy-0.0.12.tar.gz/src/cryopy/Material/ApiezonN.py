#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#%%
def SpecificHeat(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the specific heat of Apiezon N grease
    
    ========== Validity ==========

    3K < Temperature < 300K

    ========== FROM ==========
    
    https://trc.nist.gov/cryogenics/materials/Apiezon%20N/ApiezonN_rev.htm
    
    ========== INPUT ==========

    [Temperature]
        The temperature of the material in [K]

    ========== OUTPUT ==========

    [SpecificHeat]
        The specific heat in [J].[kg]**(-1).[K]**(-1)

    ========== STATUS ==========

    Status : Checked

    """

    ################## MODULES ###############################################

    import numpy as np

    ################## CONDITIONS ############################################

    if Temperature <= 200 and Temperature >= 2:

        ################## INITIALISATION ####################################
        
        Coefficients = [-1.61975,3.10923,-0.712719,4.93675,-9.37993,7.58304,-3.11048,0.628309,-0.0482634]
        Sum = 0
        
        ################## IF CONDITION TRUE #####################

        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*np.log10(Temperature)**i

        return 10**Sum
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The specitif heat of ApiezonN is not defined for T = '+str(Temperature)+' K')
        return np.nan
    
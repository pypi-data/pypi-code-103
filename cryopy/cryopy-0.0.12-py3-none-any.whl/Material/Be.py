#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def SpecificHeat(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the specific heat of Beryllium
    
    ========== Validity ==========

    14K < Temperature < 284K

    ========== FROM ==========
    
    https://trc.nist.gov/cryogenics/materials/Beryllium/Beryllium_rev.htm

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

    if Temperature <= 284 and Temperature >= 14:

        ################## INITIALISATION ####################################
        
        Coefficients = [-526.84477,2755.4105,-6209.8985,7859.2257,-6106.2095,2982.9958,-894.99967,150.85256,-10.943615]
        Sum = 0
        
        ################## IF CONDITION TRUE #####################

        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*np.log10(Temperature)**i

        return 10**Sum
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The specitif heat of Al6061-T6 is not defined for T = '+str(Temperature)+' K')
        return np.nan
    
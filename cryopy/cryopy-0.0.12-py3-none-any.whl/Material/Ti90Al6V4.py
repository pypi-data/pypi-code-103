#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def ThermalConductivity(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of 90% Titane, 6% ALuminium and 4% Vanadium
    
    ========== Validity ==========

    20K < Temperature < 300K

    ========== FROM ==========
    
    E. D. Marquardt, J. P. Le, et R. Radebaugh, « Cryogenic Material Properties Database », p. 7, 2000.

    ========== INPUT ==========

    [Temperature]
        The temperature of the material in [K]

    ========== OUTPUT ==========

    [ThermalConductivity]
        The thermal conductivity in [W].[m]**(-1).[K]**(-1)

    ========== STATUS ==========

    Status : Checked

    """

    ################## MODULES ###############################################

    import numpy as np

    ################## CONDITIONS ############################################

    if Temperature <= 300 and Temperature >= 20:

        ################## INITIALISATION ####################################
        
        Coefficients = [-5107.8774,19240.422,-30789.0064,27134.756,-14226.379,4438.2154,-763.07767,55.796592,0]
        Sum = 0
        ################## IF CONDITION TRUE #####################

        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*np.log10(Temperature)**i

        return 10**Sum
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The thermal conductivity of Ti90Al6V4 is not defined for T = '+str(Temperature)+' K')
        return np.nan
    
    
    
#%%
def LinearThermalExpansion(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the linear thermal expansion of 90% Titane, 6% ALuminium and 4% Vanadium
    
    ========== Validity ==========

    4K < Temperature < 300K

    ========== FROM ==========
    
    E. D. Marquardt, J. P. Le, et R. Radebaugh, « Cryogenic Material Properties Database », p. 7, 2000.

    ========== INPUT ==========

    [Temperature]
        The temperature of the material in [K]

    ========== OUTPUT ==========

    [LinearThermalExpansion]
        The linear thermal expansion in [%]

    ========== STATUS ==========

    Status : Checked

    """

    ################## MODULES ###############################################

    ################## CONDITIONS ############################################

    if Temperature <= 300 and Temperature >= 4:

        ################## INITIALISATION ####################################
        
        Coefficients = [-1.711e2,-2.171e-1,4.841e-3,-7.202e-6,0]
        Sum = 0
        ################## IF CONDITION TRUE #####################

        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*Temperature**i

        return Sum*1e-5
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The linear thermal expansion of Ti90Al6V4 is not defined for T = '+str(Temperature)+' K')
        return np.nan
    


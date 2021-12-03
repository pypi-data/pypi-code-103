#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def ThermalConductivity(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of NiTi
    
    ========== Validity ==========

    0.1K < Temperature < 9K

    ========== FROM ==========
    
    F. Pobell, Matter and methods at low temperatures, 3rd, rev.expanded ed éd. Berlin ; New York: Springer, 2007.

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

    if Temperature <= 9 and Temperature >= 0.1:

        if Temperature <=9 and Temperature >=4:  
            return 0.0075*Temperature**1.85
        
        if Temperature <=1 and Temperature >=0.1:
            return 0.015*Temperature**2
        
        print('Warning: The thermal conductivity of NiTi is not defined for T = '+str(Temperature)+' K')
        return np.nan        
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The thermal conductivity of NiTi is not defined for T = '+str(Temperature)+' K')
        return np.nan



#%%
def LinearThermalExpansion(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the linear thermal expansion of Niobium Titane
    
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
        
        Coefficients = [-1.862e2,-2.568e-1,8.334e-3,-2.951e-5,3.908e-8]
        Sum = 0
        ################## IF CONDITION TRUE #####################

        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*Temperature**i

        return Sum*1e-5
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The linear thermal expansion of NiTi is not defined for T = '+str(Temperature)+' K')
        return np.nan
    


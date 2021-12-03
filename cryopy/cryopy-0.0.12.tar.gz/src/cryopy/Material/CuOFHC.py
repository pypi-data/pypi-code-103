#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def ThermalConductivity(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of OFHC Copper
    
    ========== Validity ==========

    4K < Temperature < 300K

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

    if Temperature <= 300 and Temperature >= 4:

        ################## INITIALISATION ####################################
        ################## IF CONDITION TRUE #####################

        value = (2.2154 - 0.88068*Temperature**0.5 + 0.29505*Temperature - 0.048310*Temperature**1.5 + 0.003207*Temperature**2)/(1 - 0.47461*Temperature**0.5 + 0.13871*Temperature - 0.020430*Temperature**1.5 +  0.001281*Temperature**2)

        return 10**value
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The thermal conductivity of CuOFHC is not defined for T = '+str(Temperature)+' K')
        return np.nan
    
    
    
#%%
def SpecificHeat(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the specific heat of OFHC copper
    
    ========== Validity ==========

    3K < Temperature < 300K

    ========== FROM ==========
    
    E. D. Marquardt, J. P. Le, et R. Radebaugh, « Cryogenic Material Properties Database », p. 7, 2000.

    ========== INPUT ==========

    [Temperature]
        The temperature of the material in [K]

    ========== OUTPUT ==========

    [ThermalConductivity]
        The thermal conductivity in [J].[kg]**(-1).[K]**(-1)

    ========== STATUS ==========

    Status : Checked

    """

    ################## MODULES ###############################################

    import numpy as np

    ################## CONDITIONS ############################################

    if Temperature <= 300 and Temperature >= 3:

        ################## INITIALISATION ####################################
        
        Coefficients = [-1.91844,-0.15973,8.61013,-18.99640,21.96610,-12.73280,3.54322,-0.37970,0]
        Sum = 0
        ################## IF CONDITION TRUE #####################

        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*np.log10(Temperature)**i

        return 10**Sum
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The specitif heat of CuOFHC is not defined for T = '+str(Temperature)+' K')
        return np.nan
    
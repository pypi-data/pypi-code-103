#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def ThermalConductivity(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Stainless Steel 304L
    
    ========== Validity ==========

    4K < Temperature < 300K

    ========== FROM ==========
    
    https://trc.nist.gov/cryogenics/materials/304LStainless/304LStainless_rev.htm

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
        
        Coefficients = [-1.4087,1.3982,0.2543,-0.6260,0.2334,0.4256,-0.4658,0.1650,-0.0199]
        Sum = 0
        ################## IF CONDITION TRUE #####################

        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*np.log10(Temperature)**i

        return 10**Sum
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The thermal conductivity of SS304L is not defined for T = '+str(Temperature)+' K')
        return np.nan
    


#%%
def SpecificHeat(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the specific heat of Stainless Steel 304L
    
    ========== Validity ==========

    4K < Temperature < 20K

    ========== FROM ==========
    
    https://trc.nist.gov/cryogenics/materials/304LStainless/304LStainless_rev.htm

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

    if Temperature <= 20 and Temperature >= 4:

        ################## INITIALISATION ####################################
        
        Coefficients = [-351.51,3123.695,-12017.28,26143.99,-35176.33,29981.75,-15812.78,4719.64,-610.515]
        Sum = 0
        
        ################## IF CONDITION TRUE #####################

        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*np.log10(Temperature)**i

        return 10**Sum
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The specitif heat of SS304L is not defined for T = '+str(Temperature)+' K')
        return np.nan
    
    
#%%
def LinearThermalExpansion(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the linear thermal expansion of Stainless Steel 304L
    
    ========== Validity ==========

    4K < Temperature < 300K

    ========== FROM ==========
    
    https://trc.nist.gov/cryogenics/materials/304LStainless/304LStainless_rev.htm

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
        
        Coefficients = [-2.9546e2,-4.0518e-1,9.4014e-3,-2.1098e-5,1.8780e-8]
        Sum = 0
        ################## IF CONDITION TRUE #####################

        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*Temperature**i

        return Sum*1e-5
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The linear thermal expansion of SS304L is not defined for T = '+str(Temperature)+' K')
        return np.nan
#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def ThermalConductivity(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Aluminium 6061-T6
    
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
        
        Coefficients = [0.07918,1.09570,-0.07277,0.08084,0.02803,-0.09464,0.04179,-0.00571,0]
        Sum = 0
        ################## IF CONDITION TRUE #####################

        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*np.log10(Temperature)**i

        return 10**Sum
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The thermal conductivity of Al6061-T6 is not defined for T = '+str(Temperature)+' K')
        return np.nan


#%%
def SpecificHeat(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the specific heat of Aluminium 6061-T6
    
    ========== Validity ==========

    3K < Temperature < 300K

    ========== FROM ==========
    
    https://trc.nist.gov/cryogenics/materials/6061%20Aluminum/6061_T6Aluminum_rev.htm

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

    if Temperature <= 300 and Temperature >= 4:

        ################## INITIALISATION ####################################
        
        Coefficients = [46.6467,-314.292,866.662,-1298.3,1162.27,-637.795,210.351,-38.3094,2.96344]
        Sum = 0
        
        ################## IF CONDITION TRUE #####################

        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*np.log10(Temperature)**i

        return 10**Sum
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The specitif heat of Al6061-T6 is not defined for T = '+str(Temperature)+' K')
        return np.nan
    

#%%
def LinearThermalExpansion(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the linear thermal expansion of Aluminium 6061-T6
    
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
        
        Coefficients = [-4.1277e2,-3.0389e-1,8.7696e-3,-9.9821e-6,0]
        Sum = 0
        ################## IF CONDITION TRUE #####################

        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*Temperature**i

        return Sum*1e-5
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The linear thermal expansion of Al6061-T6 is not defined for T = '+str(Temperature)+' K')
        return np.nan
    

#%% 
def YoungsModulus(Temperature):
    
    """
    ========== DESCRIPTION ==========

    This function return the Young's Modulus of Aluminium 6061-T6
    
    ========== Validity ==========

    5K < Temperature < 300K

    ========== FROM ==========
    
    https://trc.nist.gov/cryogenics/materials/materialproperties.htm

    ========== INPUT ==========

    [Temperature]
        The temperature of the material in [K]

    ========== OUTPUT ==========

    [YoungsModulus]
        The Young's modulus in [Pa]

    ========== STATUS ==========

    Status : Checked

    """

    ################## MODULES ###############################################

    ################## CONDITIONS ############################################

    if Temperature <= 295 and Temperature >= 2:
        

        ################## INITIALISATION ####################################
            
        Coefficients = [7.771221e1,1.030646e-2,-2.924100e-4,8.993600e-7,-1.070900e-9]
        Sum = 0
            
        ################## IF CONDITION TRUE #####################
    
        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*Temperature**i
    
        return Sum*10**9
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The Youngs Modulus of Al6061T6 is not defined for T = '+str(Temperature)+' K')
        return np.nan

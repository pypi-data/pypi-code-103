#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def ThermalConductivity(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Stainless Steel 304
    
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
        
        Coefficients = [-1.4087,1.3982,0.2543,-0.6260,0.2334,0.4256,-0.4658,0.1650,-0.0199]
        Sum = 0
        ################## IF CONDITION TRUE #####################

        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*np.log10(Temperature)**i

        return 10**Sum
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The thermal conductivity of SS304 is not defined for T = '+str(Temperature)+' K')
        return np.nan
    


#%%
def SpecificHeat(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the specific heat of Stainless Steel 304
    
    ========== Validity ==========

    3K < Temperature < 300K

    ========== FROM ==========
    
    E. D. Marquardt, J. P. Le, et R. Radebaugh, « Cryogenic Material Properties Database », p. 7, 2000.

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

    if Temperature <= 300 and Temperature >= 3:

        ################## INITIALISATION ####################################
        
        Coefficients = [22.0061,-127.5528,303.6470,-381.0098,274.0328,-112.9212,24.7593,-2.239153,0]
        Sum = 0
        ################## IF CONDITION TRUE #####################

        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*np.log10(Temperature)**i

        return 10**Sum
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The specitif heat of SS304 is not defined for T = '+str(Temperature)+' K')
        return np.nan
    
    
#%%
def LinearThermalExpansion(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the linear thermal expansion of Stainless Steel 304
    
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
        
        Coefficients = [-2.9554e2,-3.9811e-1,9.2683e-3,-2.026e-5,1.7127e-8]
        Sum = 0
        ################## IF CONDITION TRUE #####################

        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*Temperature**i

        return Sum*1e-5
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The linear thermal expansion of SS304 is not defined for T = '+str(Temperature)+' K')
        return np.nan
    
    
#%% 
def YoungsModulus(Temperature):
    
    """
    ========== DESCRIPTION ==========

    This function return the Young's Modulus of Stainless Steel 304 
    
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

    if Temperature <= 293 and Temperature >= 5:
        
        if Temperature <=293 and Temperature >=57:

            ################## INITIALISATION ####################################
            
            Coefficients = [2.100593e2,1.534883e-1,-1.617390e-3,5.117060e-6,-6.154600e-9]
            Sum = 0
            
            ################## IF CONDITION TRUE #####################
    
            for i in range(len(Coefficients)):
                Sum = Sum + Coefficients[i]*Temperature**i
    
            return Sum*10**9
        
        else:
            
            ################## INITIALISATION ####################################
            
            Coefficients = [2.098145e2,1.217019e-1,-1.1469999e-2,3.605430e-4,-3.017900e-6]
            Sum = 0
            
            ################## IF CONDITION TRUE #####################
    
            for i in range(len(Coefficients)):
                Sum = Sum + Coefficients[i]*Temperature**i
    
            return Sum*10**9
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The Youngs Modulus of SS304 is not defined for T = '+str(Temperature)+' K')
        return np.nan
    
    
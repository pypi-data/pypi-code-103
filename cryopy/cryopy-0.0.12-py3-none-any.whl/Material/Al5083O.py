#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def ThermalConductivity(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Aluminium 5083 O
    
    ========== Validity ==========

    4K < Temperature < 300K

    ========== FROM ==========
    
    https://trc.nist.gov/cryogenics/materials/5083%20Aluminum/5083Aluminum_rev.htm

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
        
        Coefficients = [-0.90933,5.751,-11.112,13.612,-9.3977,3.6873,-0.77295,0.067336]
        Sum = 0
        ################## IF CONDITION TRUE #####################

        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*np.log10(Temperature)**i

        return 10**Sum
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The thermal conductivity of Al5083O is not defined for T = '+str(Temperature)+' K')
        return np.nan

#%%
def SpecificHeat(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the specific heat of  Aluminium 5083 0
    
    ========== Validity ==========

    4K < Temperature < 300K

    ========== FROM ==========
    
    https://trc.nist.gov/cryogenics/materials/5083%20Aluminum/5083Aluminum_rev.htm

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
        
        Coefficients = [46.6437,-314.292,866.662,-1298.3,1162.27,-637.795,210.351,-38.3094,2.96334]
        Sum = 0
        
        ################## IF CONDITION TRUE #####################

        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*np.log10(Temperature)**i

        return 10**Sum
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The specitif heat of Al5083O is not defined for T = '+str(Temperature)+' K')
        return np.nan
    
    
#%%
def LinearThermalExpansion(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the linear thermal expansion of Aluminium 5083 O
    
    ========== Validity ==========

    4K < Temperature < 300K

    ========== FROM ==========
    
    https://trc.nist.gov/cryogenics/materials/5083%20Aluminum/5083Aluminum_rev.htm

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

        print('Warning: The linear thermal expansion of Al5083O is not defined for T = '+str(Temperature)+' K')
        return np.nan
    
#%% 
def YoungsModulus(Temperature):
    
    """
    ========== DESCRIPTION ==========

    This function return the Young's Modulus of Aluminium 5083 O
    
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
            
        Coefficients = [8.083212e1,1.061708e-2,-3.016100e-4,7.561340e-7,-6.99487e-10]
        Sum = 0
            
        ################## IF CONDITION TRUE #####################
    
        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*Temperature**i
    
        return Sum*10**9
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The Youngs Modulus of Al5083O is not defined for T = '+str(Temperature)+' K')
        return np.nan
    
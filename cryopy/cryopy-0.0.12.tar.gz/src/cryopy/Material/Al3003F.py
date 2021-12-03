#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def ThermalConductivity(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Aluminium 3003 F
    
    ========== Validity ==========

    4K < Temperature < 300K

    ========== FROM ==========
    
    https://trc.nist.gov/cryogenics/materials/3003F%20Aluminum/3003FAluminum_rev.htm

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
        
        Coefficients = [0.63736,-1.1437,7.4624,-12.6905,11.9165,-6.18721,1.63939,-0.172667]
        Sum = 0
        ################## IF CONDITION TRUE #####################

        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*np.log10(Temperature)**i

        return 10**Sum
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The thermal conductivity of Al3003F is not defined for T = '+str(Temperature)+' K')
        return np.nan

#%%
def SpecificHeat(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the specific heat of  Aluminium 3003 F
    
    ========== Validity ==========

    3K < Temperature < 300K

    ========== FROM ==========
    
    https://trc.nist.gov/cryogenics/materials/3003F%20Aluminum/3003FAluminum_rev.htm

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
        
        Coefficients = [46.6467,-314.292,866.662,-1298.3,1162.27,-637.795,210.351,-38.3094,2.96344]
        Sum = 0
        ################## IF CONDITION TRUE #####################

        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*np.log10(Temperature)**i

        return 10**Sum
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The specitif heat of Al3003F is not defined for T = '+str(Temperature)+' K')
        return np.nan
    
    
#%%
def LinearThermalExpansion(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the linear thermal expansion of Aluminium 3003 F
    
    ========== Validity ==========

    4K < Temperature < 300K

    ========== FROM ==========
    
    https://trc.nist.gov/cryogenics/materials/3003F%20Aluminum/3003FAluminum_rev.htm

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

        print('Warning: The linear thermal expansion of Al3003F is not defined for T = '+str(Temperature)+' K')
        return np.nan
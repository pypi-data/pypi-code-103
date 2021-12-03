#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def ThermalConductivity(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Brass
    
    ========== Validity ==========

    5K < Temperature < 110K

    ========== FROM ==========
    
    https://trc.nist.gov/cryogenics/materials/Brass/Brass_rev.htm

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

    if Temperature <= 110 and Temperature >= 5:

        ################## INITIALISATION ####################################
        
        Coefficients = [0.021035,-1.01835,4.54083,-5.03374,3.20536,-1.12933,0.174057,-0.0038151]
        Sum = 0
        ################## IF CONDITION TRUE #####################

        for i in range(len(Coefficients)):
            Sum = Sum + Coefficients[i]*np.log10(Temperature)**i

        return 10**Sum
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The thermal conductivity of Brass is not defined for T = '+str(Temperature)+' K')
        return np.nan


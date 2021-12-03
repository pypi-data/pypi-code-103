#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#%%
def ThermalConductivity(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of manganin (Cu 84%, Ni 4%, Mn 12%)
    
    ========== Validity ==========

    0.1 K < Temperature < 4 K

    ========== FROM ==========

    I. Peroni, E. Gottardi, A. Peruzzi, G. Ponti, et G. Ventura, 
    « Thermal conductivity of manganin below 1 K », Nuclear Physics B - 
    Proceedings Supplements, vol. 78, no 1‑3, p. 573‑575, août 1999, 
    doi: 10.1016/S0920-5632(99)00606-4.
    
    D.T. Corzett, A.M.Miller and P.Seligmann, Cryogenics 16,505 (1976)

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

    if Temperature <= 4 and Temperature >= 0.1:

        ################## INITIALISATION ####################################

        ################## IF CONDITION TRUE #####################

        return 0.095*Temperature**1.19
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The thermal conductivity of Cu84Ni4Mn12 is not defined for T = '+str(Temperature)+' K')
        return np.nan
#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def ThermalConductivity(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Ni60Cr15Fe16Mo7
    
    ========== Validity ==========

    2K < Temperature < 20K

    ========== FROM ==========
    
    J. K. Hulm, « The Thermal Conductivity of a Copper-Nickel Alloy at Low Temperatures », Proc. Phys. Soc. B, vol. 64, no 3, p. 207‑211, mars 1951, doi: 10.1088/0370-1301/64/3/304.


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

    if Temperature <= 20 and Temperature >= 2:

        return 2*1e-2*Temperature**1.4
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The thermal conductivity of Ni60Cr15Fe16Mo7 is not defined for T = '+str(Temperature)+' K')
        return np.nan


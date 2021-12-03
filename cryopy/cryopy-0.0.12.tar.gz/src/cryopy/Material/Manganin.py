#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#%%
def ThermalConductivity(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Manganin
    
    ========== Validity ==========

    1K < Temperature < 4K

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

    if Temperature <= 4 and Temperature >= 1:

        return 0.094*Temperature**1.2
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The thermal conductivity of Manganin is not defined for T = '+str(Temperature)+' K')
        return np.nan


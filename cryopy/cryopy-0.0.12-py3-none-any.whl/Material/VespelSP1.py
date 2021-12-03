#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#%%
def ThermalConductivity(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Vespel SP1
    
    ========== Validity ==========

    1.4 K < Temperature < 45 K

    ========== FROM ==========

    L Duband, A Lange, et J. J. Bock. « Helium adsorption coolers for space ». 
    Submillimetre and Far-Infrared Space Instrumentation, Proceedings of the 
    30th ESLAB Symposium held in Noordwijk, 24-26 September 1996. 
    Edited by E.J. Rolfe and G. Pilbratt. ESA SP-388. 
    Paris: European Space Agency, 1996., p.289, s. d.

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

    if Temperature <= 45 and Temperature >= 1.4:

        ################## INITIALISATION ####################################

        ################## IF CONDITION TRUE #####################

        return 1.7e-3*Temperature**1.18
    
        ################## SINON NAN #########################################

    else:

        print('Warning: The thermal conductivity of Vespel SP1 is not defined for T = '+str(Temperature)+' K')
        return np.nan
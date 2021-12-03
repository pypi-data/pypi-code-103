# -*- coding: utf-8 -*-

#%%
def ThermalConductivity(Temperature):

    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of Kevlar 29
    
    ========== Validity ==========

    1.8 K < Temperature < 4 K
    5 K < Temperature < 40 K

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

    if Temperature <= 4 and Temperature >= 1.8:

        ################## INITIALISATION ####################################

        ################## IF CONDITION TRUE #####################

        return 1.9e-3*Temperature**2
    
        ################## SINON NAN #########################################

    else:
        if Temperature <= 40 and Temperature >= 5:
    
            ################## INITIALISATION ####################################
    
            ################## IF CONDITION TRUE #####################
    
            return 2.1e-3*Temperature**1.6  
        
        else:
            print('Warning: The thermal conductivity of Kevlar 29 is not defined for T = '+str(Temperature)+' K')
            return np.nan
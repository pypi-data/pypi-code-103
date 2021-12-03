# -*- coding: utf-8 -*-


#%% 
def MolarSpecificHeat():

    
    ############### MODULES ##################
    
    from cryopy.Helium import Helium3
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    
    
    ############### PARAMETERS RANGE ################
    
    Temperature = np.arange(0.00,1.8,0.001)
    P = 0
    
    ############### DATA FROM LITTERATURE #################
    
    KUERTEN1985 = pd.DataFrame({'Temperature':[0,0.001,0.002,0.003,0.004,0.005,0.006,0.008,0.01,0.012,0.014,0.016,0.018,0.02,0.025,0.03,0.035,0.04,0.045,0.05,0.06,0.07,0.08,0.09,0.1,0.11,0.12,0.13,0.14,0.15,0.16,0.17,0.18,0.19,0.2,0.21,0.22,0.23,0.24,0.25,0.3,0.35,0.40,0.45],
                            'Pressure': np.zeros(44),
                            'MolarSpecificHeat':[0,2.279e-2,4.558e-2,6.837e-2,9.114e-2,1.139e-1,1.366e-1,1.821e-1,2.274e-1,2.726e-1,3.177e-1,3.625e-1,4.072e-1,4.516e-1,5.615e-1,6.693e-1,7.748e-1,8.775e-1,8.773e-1,1.674,1.256,1.424,1.579,1.722,1.858,1.988,2.167,2.215,2.314,2.403,2.483,2.554,2.618,2.675,2.725,2.770,2.810,2.847,2.880,2.910,3.032,3.124,3.188,3.251]})
    
    
    ############### FUNCTION FROM CRYOPY ###################
        
    CRYOPY = pd.DataFrame({'Temperature':Temperature,
                           'Pressure': np.zeros(len(Temperature)),
                           'MolarSpecificHeat':[Helium3.MolarSpecificHeat(T,P) for T in Temperature]})
    
    ################ PLOT PART #######################
    
    plt.figure(figsize=[10,5])
    plt.plot(CRYOPY.Temperature,CRYOPY.MolarSpecificHeat)
    plt.plot(KUERTEN1985.Temperature,KUERTEN1985.MolarSpecificHeat,'v')
    plt.title(r'Molar Specific Heat of Helium 3 at various temperatures for P = '+str(P)+' Pa')
    plt.legend(['CRYOPY','KUERTEN (1985)'])
    plt.xlabel(r'Temperature [K]')
    plt.ylabel(r'Molar Specific Heat [ $J.mol^{-1}.K^{-1}$]')
    plt.grid()
    plt.savefig(r'Helium3.MolarSpecificHeat.pdf')
    
#%%
def MolarEnthalpy():
    
    ############### MODULES ##################
    
    from cryopy.Helium import Helium3
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    
    
    ############### PARAMETERS RANGE ################
    
    Temperature = np.arange(0.00,0.450,0.001)
    P = 0
    
    ############### DATA FROM LITTERATURE #################
    
    KUERTEN1985 = pd.DataFrame({'Temperature':[0,0.001,0.002,0.003,0.004,0.005,0.006,0.008,0.01,0.012,0.014,0.016,0.018,0.02,0.025,0.03,0.035,0.04,0.045,0.05,0.06,0.07,0.08,0.09,0.1,0.11,0.12,0.13,0.14,0.15,0.16,0.17,0.18,0.19,0.2,0.21,0.22,0.23,0.24,0.25,0.3,0.35,0.40,0.45],
                            'Pressure': np.zeros(44),
                            'MolarEnthalpy':[0,1.140e-5,4.558e-5,1.026e-4,1.823e-4,2.848e-4,4.101e-4,7.288e-4,1.138e-3,1.638e-3,2.229e-3,2.909e-3,3.679e-3,4.537e-3,7.071e-3,1.015e-2,1.376e-2,1.789e-2,2.253e-2,2.766e-2,3.932e-2,5.273e-2,6.776e-2,8.427e-2,0.1022,0.1214,0.1419,0.1635,0.1862,0.2098,0.2342,0.2594,0.2853,0.3117,0.3387,0.3662,0.3941,0.4224,0.4510,0.4800,0.6287,0.7827,0.9406,1.101]})
    
    
    ############### FUNCTION FROM CRYOPY ###################
        
    CRYOPY = pd.DataFrame({'Temperature':Temperature,
                           'Pressure': np.zeros(len(Temperature)),
                           'MolarEnthalpy':[Helium3.MolarEnthalpy(T,P) for T in Temperature]})
    
    ################ PLOT PART #######################
    
    plt.figure(figsize=[10,5])
    plt.plot(CRYOPY.Temperature,CRYOPY.MolarEnthalpy)
    plt.plot(KUERTEN1985.Temperature,KUERTEN1985.MolarEnthalpy,'v')
    plt.title(r'Molar Enthalpy of Helium 3 at various temperatures for P = '+str(P)+' Pa')
    plt.legend(['CRYOPY','KUERTEN (1985)'])
    plt.xlabel(r'Temperature [K]')
    plt.ylabel(r'Molar Enthalpy [ $J.mol^{-1}.K^{-1}$]')
    plt.grid()
    plt.savefig(r'Helium3.MolarEnthalpy.pdf')
    
#%%
def MolarEntropy():
    
    ############### MODULES ##################
    
    from cryopy.Helium import Helium3
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    
    
    ############### PARAMETERS RANGE ################
    
    Temperature = np.arange(0.00,0.450,0.001)
    P = 0
    
    ############### DATA FROM LITTERATURE #################
    
    KUERTEN1985 = pd.DataFrame({'Temperature':[0,0.001,0.002,0.003,0.004,0.005,0.006,0.008,0.01,0.012,0.014,0.016,0.018,0.02,0.025,0.03,0.035,0.04,0.045,0.05,0.06,0.07,0.08,0.09,0.1,0.11,0.12,0.13,0.14,0.15,0.16,0.17,0.18,0.19,0.2,0.21,0.22,0.23,0.24,0.25,0.3,0.35,0.40,0.45],
                            'Pressure': np.zeros(44),
                            'MolarEntropy':[0,2.279e-2,4.559e-2,6.838e-2,9.116e-2,1.139e-1,1.367e-1,1.823e-1,2.278e-1,2.732e-1,3.186e-1,3.646e-1,4.092e-1,4.545e-1,5.671e-1,6.796e-1,7.901e-1,9.003e-1,1.009,1.117,1.330,1.536,1.736,1.931,2.119,2.302,2.481,2.654,2.821,2.984,3.142,3.295,3.442,3.585,3.724,3.858,3.988,4.114,4.235,4.354,4.895,5.370,5.792,6.176]})
    
    
    ############### FUNCTION FROM CRYOPY ###################
        
    CRYOPY = pd.DataFrame({'Temperature':Temperature,
                           'Pressure': np.zeros(len(Temperature)),
                           'MolarEntropy':[Helium3.MolarEntropy(T,P) for T in Temperature]})
    
    ################ PLOT PART #######################
    
    plt.figure(figsize=[10,5])
    plt.plot(CRYOPY.Temperature,CRYOPY.MolarEntropy)
    plt.plot(KUERTEN1985.Temperature,KUERTEN1985.MolarEntropy,'v')
    plt.title(r'Molar Entropy of Helium 3 at various temperatures for P = '+str(P)+' Pa')
    plt.legend(['CRYOPY','KUERTEN (1985)'])
    plt.xlabel(r'Temperature [K]')
    plt.ylabel(r'Molar Entropy [ $J.mol^{-1}.K^{-1}$]')
    plt.grid()
    plt.savefig(r'Helium3.MolarEntropy.pdf')

#%%
def ChemicalPotential():
    
    ############### MODULES ##################
    
    from cryopy.Helium import Helium3
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    
    
    ############### PARAMETERS RANGE ################
    
    Temperature = np.arange(0.00,0.450,0.001)
    P = 0
    
    ############### DATA FROM LITTERATURE #################
    
    KUERTEN1985 = pd.DataFrame({'Temperature':[0,0.001,0.002,0.003,0.004,0.005,0.006,0.008,0.01,0.012,0.014,0.016,0.018,0.02,0.025,0.03,0.035,0.04,0.045,0.05,0.06,0.07,0.08,0.09,0.1,0.11,0.12,0.13,0.14,0.15,0.16,0.17,0.18,0.19,0.2,0.21,0.22,0.23,0.24,0.25,0.3,0.35,0.40,0.45],
                            'Pressure': np.zeros(44),
                            'ChemicalPotential':[0.00000,-1.140e-5,-4.559e-5,-1.026e-4,-1.823e-4,-2.849e-4,-4.102e-4,-7.292e-4,-1.139e-3, -1.640e-3,-2.232e-3,-2.915e-3,-3.688e-3,-4.552e-3,-7.106e-3,-1.022e-2,-1.389e-2,-1.812e-2,-2.290e-2,-2.821e-2,-4.045e-2,-5.479e-2,-7.115e-2,-8.949e-2,-1.097e-1,-1.319e-1,-1.558e-1,-1.815e-1,-2.088e-1,-2.379e-1,-2.685e-1,-3.007e-1,-3.344e-1,-3.695e-1,-4.061e-1,-4.440e-1,-4.832e-1,-5.237e-1,-5.655e-1,-6.084e-1,-8.400e-1,-1.097,-1.376,-1.675]})
    
    
    ############### FUNCTION FROM CRYOPY ###################
        
    CRYOPY = pd.DataFrame({'Temperature':Temperature,
                           'Pressure': np.zeros(len(Temperature)),
                           'ChemicalPotential':[Helium3.ChemicalPotential(T,P) for T in Temperature]})
    
    ################ PLOT PART #######################
    
    plt.figure(figsize=[10,5])
    plt.plot(CRYOPY.Temperature,CRYOPY.ChemicalPotential)
    plt.plot(KUERTEN1985.Temperature,KUERTEN1985.ChemicalPotential,'v')
    plt.title(r' Chemical potential of Helium 3 at various temperatures for P = '+str(P)+' Pa')
    plt.legend(['CRYOPY','KUERTEN (1985)'])
    plt.xlabel(r'Temperature [K]')
    plt.ylabel(r' ChemicalPotential [ $J.mol^{-1}.K^{-1}$]')
    plt.grid()
    plt.savefig(r'Helium3.ChemicalPotential.pdf')
    
    
#%%
def LiquidThermalConductivity():
    
    ############### MODULES ##################
    
    from cryopy.Helium import Helium3
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    
    
    ############### PARAMETERS RANGE ################
    
    Temperature = np.arange(0.003,1,0.001)
    P = 0
    
    ############### DATA FROM LITTERATURE #################
    
    ############### FUNCTION FROM CRYOPY ###################
        
    CRYOPY = pd.DataFrame({'Temperature':Temperature,
                           'Pressure': np.zeros(len(Temperature)),
                           'LiquidThermalConductivity':[Helium3.LiquidThermalConductivity(T,P) for T in Temperature]})
    
    ################ PLOT PART #######################
    
    plt.figure(figsize=[10,5])
    plt.plot(CRYOPY.Temperature,CRYOPY.LiquidThermalConductivity)
    plt.title(r' Liquid thermal conductivity of Helium 3 at various temperatures for P = '+str(P)+' Pa')
    plt.legend(['CRYOPY'])
    plt.xlabel(r'Temperature [K]')
    plt.ylabel(r' Liquid Thermal Conductivity [ $J.mol^{-1}.K^{-1}$]')
    plt.grid()
    plt.savefig(r'Helium3.LiquidThermalConductivity.pdf')


#%%
def MolarVolume():
    
    ############### MODULES ##################
    
    from cryopy.Helium import Helium3
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    
    
    ############### PARAMETERS RANGE ################
    
    Temperature = np.arange(0.000,1.2,0.001)
    P = 0
    
    ############### DATA FROM LITTERATURE #################

    ABRAHAM1971 = pd.DataFrame({'Temperature':[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,1.1,1.2],
                            'Pressure': np.zeros(13),
                            'MolarVolume':[36.873e-6,36.847e-6,36.794e-6,36.741e-6,36.705e-6,36.690e-6,36.697e-6,36.726e-6,36.771e-6,36.831e-6,36.903e-6,36.987e-6,37.088e-6]})
    
    ############### FUNCTION FROM CRYOPY ###################
        
    CRYOPY = pd.DataFrame({'Temperature':Temperature,
                           'Pressure': np.zeros(len(Temperature)),
                           'MolarVolume':[Helium3.MolarVolume(T,P) for T in Temperature]})
    
    ################ PLOT PART #######################
    
    plt.figure(figsize=[10,5])
    plt.plot(CRYOPY.Temperature,CRYOPY.MolarVolume)
    plt.plot(ABRAHAM1971.Temperature,ABRAHAM1971.MolarVolume,'v')
    plt.title(r' Molar volume of Helium 3 at various temperatures for P = '+str(P)+' Pa')
    plt.legend(['CRYOPY','ABRAHAM (1971)'])
    plt.xlabel(r'Temperature [K]')
    plt.ylabel(r' Molar Volume [ $m^{3}.mol^{-1}$]')
    plt.grid()
    plt.savefig(r'Helium3.MolarVolume.pdf')

# -*- coding: utf-8 -*-
#%% 
def Mass():
    
    """
    
    Return the constant mass of a single Helium 3 atom.
    This function does not require parameter since this is a constant
    
    
    Parameters
    ----------
    
    None
    
    
    Returns
    -------
    
    "Mass" : [kg]
        The mass of a single atom of Helium 3
        

    Sources
    -------
    
    Wikipedia : https://en.wikipedia.org/wiki/Helium-3
    
    
    Status
    ------
    
    This function is CHECKED
    
    Notes
    -----
    
    None
    

    """
    
    ################## MODULES ###############################################
    
    ################## CONDITIONS ############################################
            
    ################## INITIALISATION ####################################
        
    return  5.0082344373334204e-27  

#%% 
def EffectiveMass():
    
    """
    
    Return the effective mass of a single atom of Helium 3.
    This function does not require parameter since this is a constant
    
    Parameters
    ----------
    
    None
    
    
    Returns
    -------
    
    "EffectiveMass" : [kg]
        The effective mass of a single atom of Helium 3
        

    Sources
    -------
    
    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (44)
    
    POBELL - Matter and methods at low temperature - Second edition -  P.125

    Status
    ------
    
    This function is CHECKED

    Notes
    -----
    
    A potential improvement can be done since the effective mass of Helium 3
        can change if Helium 3 is in a Helium 3 /Helium 4 mixture
    
    """

    
    ################## MODULES ###############################################
    
    from cryopy.Helium import Helium3
    
    ################## CONDITIONS ############################################
            
    ################## INITIALISATION ####################################
        
    return  2.46*Helium3.Mass()


#%% 
def MolarSpecificHeat(Temperature,Pressure):
    
    """
    
    This function return the molar specific heat of pure Helium 3
    
    Parameters
    ----------
    
    "Temperature" : [K]
        The temperature of Helium 3
        
    "Pressure" : [Pa]
        The pressure of Helium 3
        
    Validity
    --------
    
    "Temperature" : [0,1.8]
    "Pressure" : [0]
    
    Returns
    -------
    
    "MolarSpecificHeat" : [J].[K]**(-1).[mol]**(-1)
        The molar specific heat of pure Helium 3
        
    Sources
    -------
    
    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (48)
    
    CHAUDHRY - Thermodynamic properties of liquid 3He-4he mixtures
    between 0.15 K and 1.8 K - Equation (A14)

    Status
    ------
    
    This function is CHECKED 

    Notes
    -----
    
    This function requires the implementation of pressure changes
    
    
    """
    
    
    ################## MODULES ###############################################

    from cryopy import Constant
    import pandas as pd
    import numpy as np

    ################## CONDITION 1 ############################################
    
    if Pressure == 0:
        
        ################## CONDITION 2 ############################################
    
        if Temperature <= 1.8 and Temperature >= 0:
                
            ################## INITIALISATION ####################################
        
            result = 0
            Coefficients = pd.DataFrame(np.array([[np.nan,0.0245435],
                                                      [2.7415,1.85688],
                                                      [0,9.39988],
                                                      [-61.78929,-117.910],
                                                      [-177.8937,440.368],
                                                      [2890.0675,-735.836],
                                                      [0,468.741]]),
                                            columns = ['C_1','C_2'])
               
            ################## IF C1 True & C2 True #####################
                
            if Temperature<=0.1:
                for j in [1,2,3,4,5]:
                    result = result + Coefficients.C_1[j]*Temperature**j
                return Constant.Gas()*result
        
            if Temperature<=0.45 and Temperature>0.1:
                for j in [0,1,2,3,4,5,6]:
                    result = result + Coefficients.C_2[j]*Temperature**j
                return Constant.Gas()*result
        
            else:
                return 3.6851551 - 1.9650072*Temperature + 3.3601049 * Temperature**2 - 0.8351251 * Temperature**3 - (0.0444842/(Temperature**2))*np.exp(-0.0977175 / Temperature)
            
            ################## IF C1 True & C2 False #####################
            
        print('Warning: The function Helium3.MolarSpecificHeat is not defined for T = '+str(Temperature)+' K')
        return np.nan

            ################## IF C1 False & C2 False #########################################
    else:
        
        print('Warning: The function Helium3.MolarSpecificHeat is not defined for P = '+str(Pressure)+' Pa')
        return np.nan   

    
#%% 
def MolarEnthalpy(Temperature,Pressure):

    """
    ========== DESCRIPTION ==========
    
    This function can return the molar enthalpy of Helium 3


    ========== VALIDITY ==========
    
    0 mK < Temperature < 450 mK
    Pressure = 0 Pa

    ========== FROM ==========
    
    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (37)

     ========== INPUT ==========
     
     [Temperature]
         The temperature of Helium 3 in [K]
         
     [Pressure]
         The pressure of Helium 3 in [Pa]
  
     ========== OUTPUT ==========
     
     [MolarEnthalpy]
         The molar enthalpy of Helium 3 in [J].[mol]**(-1)
     
     ========== STATUS ==========     
     
     Status : In progress (Pressure variation is not implemented)
     
     ========= IMPROVEMENT ========== 
     
         - Add Pressure variation 
         
    """
    
    ################## MODULES ###############################################

    from cryopy import Constant
    import pandas as pd
    import numpy as np

    ################## CONDITION 1 ############################################
    
    if Pressure == 0:
        
        ################## CONDITION 2 ############################################

        if Temperature <= 0.450 and Temperature >= 0:
            
            ################## INITIALISATION ####################################
    
            result = 0
            Coefficients = pd.DataFrame(np.array([[np.nan,0.0245435],
                                                  [2.7415,1.85688],
                                                  [0,9.39988],
                                                  [-61.78929,-117.910],
                                                  [-177.8937,440.368],
                                                  [2890.0675,-735.836],
                                                  [0,468.741]]),
                                        columns = ['C_1','C_2'])
           
            ################## IF C1 True & C2 True #####################
            
            if Temperature<=0.1:
                for j in [1,2,3,4,5]:
                    result = result + Coefficients.C_1[j]*Temperature**(j+1)/(j+1)
                return Constant.Gas()*result
    
            if Temperature<=0.45 and Temperature>0.1:
                result = result -0.0004006515045376974
                for j in [0,1,2,3,4,5,6]:
                    result = result + Coefficients.C_2[j]*Temperature**(j+1)/(j+1)
                return Constant.Gas()*result
    
            ################## IF C1 True & C2 False #########################################
            
        else :
            
            print('Warning: The function Helium3.MolarEnthalpy is not defined for T = '+str(Temperature)+' K')
            return np.nan
        
            ################## IF C1 False & C2 False #########################################
    else:
        
        print('Warning: The function Helium3.MolarEnthalpy is not defined for P = '+str(Pressure)+' Pa')
        return np.nan     

#%% 
def MolarEntropy(Temperature,Pressure):
    
    """
    ========== DESCRIPTION ==========
    
    This function can return the molar entropy of Helium 3

    ========== VALIDITY ==========
    
    0 mK < Temperature < 450 mK
    Pressure = 0 Pa
    

    ========== FROM ==========
    
    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Table for Helium 3

    ========== INPUT ==========
    
    [Temperature]
        The temperature of Helium 3 in [K]
        
    [Pressure]
        The pressure of Helium 3 in [Pa]
 
    ========== OUTPUT ==========
    
    [MolarEntropy]
        The molar entropy of Helium 3 in [J].[K]**(-1).[mol]**(-1)
    
    ========== STATUS ==========     
    
    Status : In progress (Pressure variation is not implemented)
    
    ========= IMPROVEMENT ========== 
    
        - Add Pressure variation 

    """
    
    ################## MODULES ###############################################

    import numpy as np

    ################## CONDITION 1 ############################################
    
    if Pressure == 0:
        
        ################## CONDITION 2 ############################################

        if Temperature <= 0.450 and Temperature >= 0:
            
            ################## INITIALISATION ####################################
    
            Coefficients = [ 5.64822229e+02, -8.94486733e+02,  5.54757487e+02, -1.45763639e+02,
           -9.26752184e+00,  2.31209308e+01, -1.62015854e-03]
            Polynome = np.poly1d(Coefficients)
            
            ################## IF C1 True & C2 True #####################
            
            return Polynome(Temperature)
    
            ################## IF C1 True & C2 False ###############################
            
        else:
            
            print('Warning: The function Helium3.MolarEntropy is not defined for T = '+str(Temperature)+' K')
            return np.nan
        
        ################## IF C1 False & C2 False ###############################
        
    else:
        
        print('Warning: The function Helium3.MolarEntropy is not defined for P = '+str(Pressure)+' Pa')
        return np.nan     
    

#%% 
def ChemicalPotential(Temperature,Pressure):
    
    """
    ========== DESCRIPTION ==========
    
    This function return the chemical potential of Helium 3

    ========== VALIDITY ==========
    
    Always (TBC)

    ========== FROM ==========
    
    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (38)

    ========== INPUT ==========
    
    [Temperature]
        The temperature of Helium 3 in [K]
        
    [Pressure]
        The pressure of Helium 3 in [Pa]

    ========== OUTPUT ==========
    
    [ChemicalPotential]
        The chemical potential of Helium 3 in [J].[mol]**(-1)
    
    ========== STATUS ==========     
    
    Status : In progress (need to be verified with new values of pressure)

    """
    
    ################## MODULES ###############################################
    
    from cryopy.Helium import Helium3

    ################## CONDITIONS ############################################

    ################## INITIALISATION ####################################

    ################## FONCTION SI CONDITION REMPLIE #####################

    return Helium3.MolarEnthalpy(Temperature,Pressure)-Temperature*Helium3.MolarEntropy(Temperature,Pressure)

  
#%% 
def InternalEnergy(Temperature,Pressure):
    
    """
    ========== DESCRIPTION ==========
    
    This function return the internal energy of Helium 3

    ========== VALIDITY ==========
    
    Always

    ========== FROM ==========
    
    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (37)

    ========== INPUT ==========
    
    [Temperature]
        The temperature of Helium 3 in [K]
        
    [Pressure]
        The pressure of Helium 3 in [Pa]

    ========== OUTPUT ==========
    
    [InternalEnergy]
        The internal energy of Helium 3 in [J].[mol]**(-1).[K]**(-1)
    
    ========== STATUS ==========     
    
    Status : In progress (need to be verified with new values of pressure)

    """
    
    ################## MODULES ###############################################
    
    from cryopy.Helium import Helium3

    ################## CONDITIONS ############################################

    ################## INITIALISATION ####################################

    ################## FONCTION SI CONDITION REMPLIE #####################

    return Helium3.EntalpieMolaire(Temperature,Pressure)
          
    
    
#%% 
def MolarVolume(Temperature,Pressure):
    
    """
    ========== DESCRIPTION ==========
    
    This function return the molar volume of a mole of Helium 3

    ========== VALIDITY ==========
    
    0 K < Temperature < 1 K
    0 Pa < pressure < 15,7e5 Pa

    ========== FROM ==========
    
    CHAUDHRY - Thermodynamic properties of liquid 3He-4he mixtures
    between 0.15 K and 1.8 K - Equation (A.22)

    ========== INPUT ==========
    
    [Temperature]
        The temperature of Helium 3 in [K]
        
    [Pressure]
        The pressure of Helium 3 in [Pa]     
        
    ========== OUTPUT ==========
    
    [MolarVolume]
        The molar volume of Helium 3 in [m3].[mol]**(-1)
    
    ========== STATUS ==========
    
    Status : Checked
    

    """
    
    ################## MODULES ###############################################
    
    import numpy as np
 
    ################## INITIALISATION ####################################

    Coefficients = np.array([[40.723012,-1.3151948,0.0409498],
                             [-0.6614794,0.1275125,-0.0091931],
                             [0.5542147,-0.1527959,0.0113764],
                             [0.1430724,-0.0034712,-0.0008515],
                             [-0.2603492,np.nan,-0.0051946]])

    ################## CONDITION 1 ############################################
    
    if Pressure <=15.7e5 and Pressure >=0.00:

    
    ################## CONDITION 2 ############################################
    
        if Temperature <=1.2 and Temperature >= 0.00:
                                
    ################## If C1 True & C2 True #####################
    
            
            Pressure = Pressure*1e-5 # From [Pa] to [Bar]
            
            result = 0
            for i in range(3):
                for j in range(2):
                    result = result + Coefficients[i][j]*Temperature**i*Pressure**j
    
            return (result + 1/(Coefficients[4][2]*Pressure**2+Coefficients[4][0]))*1e-6 # 1e-6 to SI
        
            ################## IF C1 True & C2 False ###############################
            
        else:
            
            print('Warning: The function Helium3.MolarVolume is not defined for T = '+str(Temperature)+' K')
            return np.nan
        
        ################## IF C1 False & C2 False ###############################
        
    else:
        
        print('Warning: The function Helium3.MolarVolume is not defined for P = '+str(Pressure)+' Pa')
        return np.nan  
    

        
#%% 
def SolidLiquidTransition(Temperature):
    
    """
    ========== DESCRIPTION ==========
    
    This function return the pressure of the Solid/Liquid transition of Helium 3 at a given temperature

    ========== VALIDITY ==========
    
    1 K < Temperature < 3.15 K

    ========== FROM ==========
    
    SHERMAN - Pressure-Volume-Temperature Relations of Liquid He3 from 1K 
    to 3.3K - Equation (1)

    ========== INPUT ==========
    
    [Temperature]
        The temperature of Helium 3 in [K]
        
    ========== OUTPUT ==========
    
    [SolidLiquidTransition]
        The pressure of the transition in [Pa]
    
    ========== STATUS ==========
    
    Status : Checked
    

    """
    
    ################## MODULES ###############################################
 
    ################## INITIALISATION ####################################

    ################## CONDITION 1 ############################################

    if Temperature <= 3.15 and Temperature >= 1.07:
    
    ################## If C1 True #####################
         
        return (24.599 + 16.639*Temperature**2 - 2.0659*Temperature**3 + 0.11212*Temperature**4)*1e5
    
    ################## If C1 False ############################################
    
    else:
        print('Warning: The function Helium3.SolidLiquidTransition is not defined for T = '+str(Temperature)+' K')
    
#%% 
def LiquidThermalConductivity(Temperature,Pressure):
    
    """
    ========== DESCRIPTION ==========
    
    This function return the thermal conductivity of liquid Helium 3

    ========== VALIDITY ==========
    
    0.003 K < Temperature < 300 K
    0 Pa < Pressure < 20e6

    ========== FROM ==========
    
    HUANG - Thermal conductivity of helium-3 between 3 mK and 300 K
    
    ========== INPUT ==========
    
    [Temperature]
        The temperature of Helium 3 in [K]
        
    [Pressure]
        The pressure of Helium 3 in [Pa]     
        
    ========== OUTPUT ==========
    
    [LiquidThermalConductivity]
        The thermal conductivity of liquid Helium 3 in [W].[m]**(-1).[K]**(-1)
    
    ========== STATUS ==========
    
    Status : Checked
  

    """
    
    ################## MODULES ###############################################
    
    import numpy as np
 
    ################## INITIALISATION ####################################
    
    Coefficients = np.array([[-4.96046174,-0.65469605,0.22709943,-0.048878330,-0.014822690,-0.0065179072],
                             [0.73147012,1.1285816,-0.35962597,0.068654087,0.016518400,np.nan],
                             [0.89421626,-0.079608445,0.018861074,0.029884542,np.nan,np.nan],
                             [-0.0084984819,-0.054117908,0.016515130,np.nan,np.nan,np.nan],
                             [-0.10296191,-0.022615875,np.nan,np.nan,np.nan,np.nan],
                             [-0.015211058,np.nan,np.nan,np.nan,np.nan,np.nan]])
                                    
    
    x = np.log(Temperature) # Log scale of the Temperature
    y = Pressure/101325 # From [Pa] to [Bar]

    x = x*2/np.log(300/0.003)-np.log(0.003)*2/np.log(300/0.003)-1  # Normalize between -1 and 1
    y = y*0.010132500000000001-1 # Normalize between -1 and 1
    
    ################## CONDITION 1 ############################################
    
    if Pressure <= 20e6 and Pressure >= 0:
        
        ################## CONDITION 2 ############################################
    
        if Temperature <= 300 and Temperature >= 0.003:
        
        ################## If C1 True & C2 True #####################
        
            result = 0
            
            for j in np.arange(1,6):
                for i in np.arange(1,6-j):
                    result = result + Coefficients[i][j]*np.cos(i*np.arccos(x))*np.cos(j*np.arccos(y))
                    
            for i in np.arange(1,6):
                result = result + Coefficients[i][0]*np.cos(i*np.arccos(x))
            
            for j in np.arange(1,6):
                result = result + Coefficients[0][j]*np.cos(j*np.arccos(y))
            
            result = result + Coefficients[0][0]
            
            return np.exp(result)
        
            ################## IF C1 True & C2 False ###############################
            
        else:
            
            print('Warning: The function Helium3.LiquidThermalConductivity is not defined for T = '+str(Temperature)+' K')
            return np.nan
        
        ################## IF C1 False & C2 False ###############################
        
    else:
        
        print('Warning: The function Helium3.LiquidThermalConductivity is not defined for P = '+str(Pressure)+' Pa')
        return np.nan  

#%% 
def GasThermalConductivity(Temperature,Pressure):
    
    """
    ========== DESCRIPTION ==========
    
    This function return the thermal conductivity of gaseous Helium 3

    ========== VALIDITY ==========
    
    0.003 K < Temperature < 300 K
    0 Pa < Pressure < 20e6

    ========== FROM ==========
    
    HUANG - Thermal conductivity of helium-3 between 3 mK and 300 K
    
    ========== INPUT ==========
    
    [Temperature]
        The temperature of Helium 3 in [K]
        
    [Pressure]
        The pressure of Helium 3 in [Pa]     
        
    ========== OUTPUT ==========
    
    [GasThermalConductivity]
        The thermal conductivity of gaseous Helium 3 in [W].[m]**(-1).[K]**(-1)
    
    ========== STATUS ==========
    
    Status : To be checked
  

    """
    
    ################## MODULES ###############################################
    
    import numpy as np
 
    ################## INITIALISATION ####################################
    
    Coefficients = np.array([[85.487315,5.495659,3.089753,1.276371,0.577591],
                             [98.529019,-4.351606,-2.525931,-0.430895,np.nan],
                             [38.396887,-1.862116,-0.798918,np.nan,np.nan],
                             [12.020784,2.80104,np.nan,np.nan,np.nan],
                             [2.159515,np.nan,np.nan,np.nan,np.nan]])
                                    
    
    x = np.log(Temperature) # Log scale of the Temperature
    y = Pressure/101325 # From [Pa] to [Bar]

    x = x*2/np.log(300/0.003)-np.log(0.003)*2/np.log(300/0.003)-1  # Normalize between -1 and 1
    y = y*0.010132500000000001-1 # Normalize between -1 and 1
    
    ################## CONDITION 1 ############################################
    
    if Pressure <= 20e6 and Pressure >= 0:
        
        ################## CONDITION 2 ############################################
    
        if Temperature <= 300 and Temperature >= 0.003:
        
        ################## If C1 True & C2 True #####################
        
            result = 0
            
            for j in np.arange(1,5):
                for i in np.arange(1,5-j):
                    result = result + Coefficients[i][j]*np.cos(i*np.arccos(x))*np.cos(j*np.arccos(y))
                    
            for i in np.arange(1,5):
                result = result + Coefficients[i][0]*np.cos(i*np.arccos(x))
            
            for j in np.arange(1,5):
                result = result + Coefficients[0][j]*np.cos(j*np.arccos(y))
            
            result = result + Coefficients[0][0]
            
            return np.exp(result)
        
            ################## IF C1 True & C2 False ###############################
            
        else:
            
            print('Warning: The function Helium3.GasThermalConductivity is not defined for T = '+str(Temperature)+' K')
            return np.nan
        
        ################## IF C1 False & C2 False ###############################
        
    else:
        
        print('Warning: The function Helium3.GasThermalConductivity is not defined for P = '+str(Pressure)+' Pa')
        return np.nan  




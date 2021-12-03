# -*- coding: utf-8 -*-
#%% Volume Molaire - Vérifiée
def VolumeMolaire(Temperature,Pression):
    
    """
    ========== DESCRIPTION ==========
    
    Cette fonction permet de déterminer le volume molaire de l'Helium 4

    ========== VALIDITE ==========
    
    0 mK < Temperature < 1 K

    ========== SOURCE ==========
    
    TANAKA (2000) - Molar volume of pure liquide 4He : dependence on temperature (50-1000mK)
    and pressure (0-1.57 MPa) - Equation (25)
    

    ========== ENTREE ==========
    
    [Temperature]
        La température du fluide en K
    [Pression]
        La pression en Pa        
        
    ========== SORTIE ==========
    
    [VolumeMolaire]
        Le volume molaire de l'Helium 4 en m3/mol
    
    ========== STATUS ==========     
    
    Status : Vérifiée

    ========== MISE A JOUR ==========     
    
    2021-05-07:
        Dans CHAUDHRY (2012) - P59, on peut prolonger les données jusqu'à 1.8K
        avec une erreur max de 0.1%
    

    """
    
    ################## MODULES ###############################################
    
    import numpy as np
    import pandas as pd
    from scipy.special import erfc
    
    ################## CONDITIONS ############################################
    
    if Temperature <=1.8 and Temperature >= 0.001:
    
        ################## INITIALISATION ####################################
        Coefficients = pd.DataFrame(np.array([[2.757930e-5,8.618,1.863e8,2.191],
                                              [-3.361585e-12,-7.487e-7,7.664e6,-1.702e-7],
                                              [1.602419e-18,5.308e-14,np.nan,np.nan],
                                              [-1.072604e-24,np.nan,np.nan,np.nan],
                                              [7.979064e-31,np.nan,np.nan,np.nan],
                                              [-5.356076e-37,np.nan,np.nan,np.nan],
                                              [2.703689e-43,np.nan,np.nan,np.nan],
                                              [-9.004790e-50,np.nan,np.nan,np.nan],
                                              [1.725962e-56,np.nan,np.nan,np.nan],
                                              [-1.429411e-63,np.nan,np.nan,np.nan]]),
                                            columns = ['V','Delta','A','B'])    
            
        pc = -1.00170e6
        
        ################## FONCTION SI CONDITION REMPLIE #####################
        
        sommeV = 0
        for i in range(10):
            sommeV = sommeV+Coefficients.V[i]*Pression**i
            
        sommeA = (Coefficients.A[0]/((Pression-pc)**2)+Coefficients.A[1]/((Pression-pc)**(5/3)))*Temperature**4/4
          
        sommeB = Coefficients.B[0]+Coefficients.B[1]*Pression
        
        sommeDelta = 0
        for i in range(3):
            sommeDelta = sommeDelta+Coefficients.Delta[i]*Pression**i  
        
        return sommeV*(1+sommeA-sommeB*erfc((sommeDelta/Temperature)**0.5))

    else:
        print('Erreur: la fonction Helium4.VolumeMolaire est invalide pour cette valeur.')
        return np.nan    

#%% Masse Molaire - Vérifiée
def MasseMolaire():
    
    """
    ========== DESCRIPTION ==========
    
    Cette fonction permet de déterminer la masse molaire de l'Helium 4

    ========== VALIDITE ==========
    
    Toujours

    ========== SOURCE ==========
    
    Wikipedia - https://en.wikipedia.org/wiki/Helium
    
    ========== ENTREE ==========
         
    ========== SORTIE ==========
    
    [MasseMolaire]
        La masse molaire de l'Helium 4 en [g/mol]
    
    ========== STATUS ==========     
    
    Status : Vérifiée

    ========== MISE A JOUR ==========     

    """
    
    ################## MODULES ###############################################
    
    ################## CONDITION ############################################
    
    ################## INITIALISATION ####################################

    ################## FONCTION SI CONDITION REMPLIE #####################
        
    return 4.002602 


#%% Chaleur Specifique Molaire - Vérifiée
def ChaleurSpecifiqueMolaire(Temperature,Pression):

    """
    ========== DESCRIPTION ==========
    
    Cette fonction permet de déterminer la chaleur spécifique molaire de
    l'Helium 4 en fonction de la température


    ========== VALIDITE ==========
    
    0 < Temperature < 1.8 mK

    ========== SOURCE ==========
    
    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (46)
    
    CHAUDHRY - Thermodynamic properties of liquid 3He-4he mixtures
    between 0.15 K and 1.8 K - Equation (A15)

    ========== ENTREE ==========
    
    [Temperature]
        La température du fluide en K
    [Pression] 
        La pression en Pa
        
    ========== SORTIE ==========
    
    [ChaleurSpecifiqueMolaire]
        La chaleur spécifique molaire de l'Helium 4 en J/K/mol
    
    ========== STATUS ==========     
    
    Status : Vérifiée

    """
    
    ################## MODULES ###############################################

    import numpy as np
    import pandas as pd

    ################## CONDITIONS ############################################

    if Temperature <= 1.8 and Temperature >= 0:
        
        if Temperature <= 0.4 and Temperature >= 0:
            
            ################## INITIALISATION ####################################
            
            result = 0
            Coefficients = pd.DataFrame(np.array([[0.08137],
                                                  [0],
                                                  [-0.0528],
                                                  [0.05089],
                                                  [0.019]]),
                                        columns = ['B'])
            
            ################## FONCTION SI CONDITION REMPLIE #####################
            
            for j in [0,1,2,3,4]:
                result = result + Coefficients.B[j]*Temperature**(j+3)
            return result 
    
            ################## SINON NAN #########################################
        else:
            first = 82.180127 * Temperature**3 - 87.45899 * Temperature**5 + 129.12758 * Temperature**6 - 6.6314726 * Temperature**7
            second = 70198.836 * (8.8955141/Temperature)**(3/2) * np.exp(-8.8955141/Temperature) * (1 + (Temperature/8.8955141) + 0.75*((Temperature/8.8955141)**2))
            third = (10244.198/Temperature) * (22.890183/Temperature)**2 * np.exp(-22.890183/Temperature) * (1 - 2*(Temperature/22.890183))
            value = (first + second + third) * 1e-3
            return value
    else:
        print('Erreur: la fonction Helium4.ChaleurSpecifiqueMolaire est invalide pour cette valeur.')
        return np.nan   

#%% Entalpie Molaire - Vérifiée
def EntalpieMolaire(Temperature,Pression):

    """
    ========== DESCRIPTION ==========
    
    Cette fonction permet de déterminer l'entalpie molaire de
    l'Helium 4 pur en fonction de la température


    ========== VALIDITE ==========
    
    0 < Temperature < 400 mK

    ========== SOURCE ==========
    
    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Table (17)

    ========== ENTREE ==========
    
    [Temperature]
        La température du fluide en K
    [Pression] 
        La pression en Pa
        
    ========== SORTIE ==========
    
    [EntalpieMolaire]
        L'entalpie molaire de l'Helium 4 pur en J/mol
         
    ========== STATUS ==========     
    
    Status : Vérifiée

    """
    
    ################## MODULES ###############################################

    import numpy as np

    ################## CONDITIONS ############################################

    if Temperature <= 0.400 and Temperature >= 0:
        
        ################## INITIALISATION ####################################

        Coefficients = [ 3.19794159e-03, -6.48309258e-03,  2.19933824e-02, -2.09571258e-04,
        1.23491357e-05, -2.67718222e-07,  1.07444578e-09]
        Polynome = np.poly1d(Coefficients)
        
        ################## FONCTION SI CONDITION REMPLIE #####################
        
        return Polynome(Temperature)

        ################## SINON NAN #########################################
        
    else:

        print('Erreur: la fonction Helium4.EntalpieMolaire est invalide pour cette valeur.')
        return np.nan

#%% Entropie Molaire - Vérifiée
def EntropieMolaire(Temperature,Pression):

    """
    ========== DESCRIPTION ==========
    
    Cette fonction permet de déterminer l'entalpie molaire de
    l'Helium 4 pur en fonction de la température


    ========== VALIDITE ==========
    
    0 < Temperature < 400 mK

    ========== SOURCE ==========
    
    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Table (17)

    ========== ENTREE ==========
    
    [Temperature]
        La température du fluide en K
    [Pression] 
        La pression en Pa
        
    ========== SORTIE ==========
    
    [EntropieMolaire]
        L'entropie molaire de l'Helium 4 pur en J/mol/K
         
    ========== STATUS ==========     
    
    Status : Vérifiée

    """
    
    ################## MODULES ###############################################

    import numpy as np

    ################## CONDITIONS ############################################

    if Temperature <= 0.400 and Temperature >= 0:
        
        ################## INITIALISATION ####################################

        Coefficients = [-2.08468571e-03,  2.73347674e-03, -5.46990881e-03,  2.81129291e-02,
       -7.81349812e-05,  2.17304932e-06, -1.05591438e-08]
        Polynome = np.poly1d(Coefficients)
        
        ################## FONCTION SI CONDITION REMPLIE #####################
        
        return Polynome(Temperature)

        ################## SINON NAN #########################################
        
    else:

        print('Erreur: la fonction Helium4.EntropieMolaire est invalide pour cette valeur.')
        return np.nan
    
#%% Potentiel Chimique - Vérifiée
def PotentielChimique(Temperature,Pression):
    
    """
    ========== DESCRIPTION ==========
    
    Cette fonction permet de déterminer le potentiel chimique de 4He pur

    ========== VALIDITE ==========
    
    Toujours

    ========== SOURCE ==========
    
    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (38)

    ========== ENTREE ==========
    
    [Temperature]
        La température du fluide en K
    [Pression] 
        La pression en Pa
        
    ========== SORTIE ==========
    
    [PotentielChimique]
        Le potentiel chimique de l'Helium 4 en J/mol
    
    ========== STATUS ==========     
    
    Status : Vérifiée

    """
    
    ################## MODULES ###############################################

    ################## CONDITIONS ############################################

    ################## INITIALISATION ####################################

    ################## FONCTION SI CONDITION REMPLIE #####################

    return EntalpieMolaire(Temperature,Pression)-Temperature*EntropieMolaire(Temperature,Pression)

        
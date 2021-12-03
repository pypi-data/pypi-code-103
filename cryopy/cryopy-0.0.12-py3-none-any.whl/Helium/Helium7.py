# -*- coding: utf-8 -*-
#%% Chaleur Specifique Molaire - Verifiée
def ChaleurSpecifiqueMolaire(Temperature,Pression,Concentration3He):

    """
    ========== DESCRIPTION ==========

    Cette fonction permet de déterminer la chaleur spécifique molaire du
    mélange Helium3-Helium4 en fonction de la température, de la pression, et 
    de la concentration en Helium 3 du mélange

    ========== VALIDITE ==========

    0 <= Temperature <= 0.250 K
    0 <= Pression <= 0 Pa
    0 <= Concentration3He <= 8 %

    ========== SOURCE ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (6)

    ========== ENTREE ==========

    [Temperature]
        La température du fluide en [K]
    [Concentration3He]
        La concentration de 3He dans le mélange 3He-4He sans unité
    [Pression]
        La pression en [Pa]

    ========== SORTIE ==========

    [ChaleurSpecifiqueMolaire]
        La chaleur spécifique molaire de l'Helium 4 en [J/K/mol]

    ========== STATUS ==========

    Status : Vérifiée
    
    ========== A FAIRE ==========

    Contrainte sur la pression à ajouter

    """

    ################## MODULES ###############################################

    import numpy as np
    import Helium4,Fermi

    ################## CONDITION 1 ############################################
    
    if Temperature <= 0.250 and Temperature >= 0:
        
    ################## CONDITION 2 ############################################
            
        if Pression <= 0 and Pression >= 0:
            
    ################## CONDITION 3 ############################################
        
            if Concentration3He <= 0.08 and Concentration3He >= 0:
        
    ################## INITIALISATION ####################################
        
    ################## FONCTION SI CONDITIONS REMPLIE #####################
        
                return Concentration3He*Fermi.ChaleurSpecifiqueMolaire(Temperature,Pression,Concentration3He)+(1-Concentration3He)*Helium4.ChaleurSpecifiqueMolaire(Temperature,Pression)
        
    ################## SINON NAN #########################################
        
            else:
                print('Erreur: la fonction Helium7.ChaleurSpecifiqueMolaire est invalide pour cette valeur de concentration x = '+str(Concentration3He*100)+' %')
                return np.nan
        else:
            print('Erreur: la fonction Helium7.ChaleurSpecifiqueMolaire est invalide pour cette valeur de pression P = '+str(Pression)+' Pa')
            return np.nan
    else:
        print('Erreur: la fonction Helium7.ChaleurSpecifiqueMolaire est invalide pour cette valeur de température T = '+str(Temperature)+' %')
        return np.nan
    


#%% Volume Molaire - Vérifiée
def VolumeMolaire(Temperature,Pression,Concentration3He):

    """
    ========== DESCRIPTION ==========

    Cette fonction permet de déterminer le volume molaire du mélange
    Helium3-Helium4 en fonction de la temperature, de la pression
    et de la concentration en Helium3 du mélange

    ========== VALIDITE ==========

    0 <= Temperature <= 0.250 K
    0 <= Pression <= 0 Pa
    0 <= Concentration3He <= 8 %

    ========== SOURCE ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (43)

    ========== ENTREE ==========

    [Temperature]
        La température du fluide en [K]
    [Pression]
        La pression en [Pa]
    [Concentration3He]
        La concentration de 3He dans le mélange 3He-4He sans unité

    ========== SORTIE ==========

    [VolumeMolaire]
        Le volume molaire du mélange Helium3-Helium4 en [m3/mol]

    ========== STATUS ==========

    Status : Vérifiée
    
    ========== A FAIRE ==========

    Contrainte sur la pression à ajouter

    """

        ################## MODULES ###############################################

    import numpy as np
    import Helium4

    ################## CONDITION 1 ############################################
    
    if Temperature <= 0.250 and Temperature >= 0:
        
    ################## CONDITION 2 ############################################
            
        if Pression <= 0 and Pression >= 0:
            
    ################## CONDITION 3 ############################################
        
            if Concentration3He <= 0.08 and Concentration3He >= 0:
        
    ################## INITIALISATION ####################################
        
    ################## FONCTION SI CONDITIONS REMPLIE #####################
        
                return Helium4.VolumeMolaire(Temperature,Pression)*(1+0.286*Concentration3He)

    ################## SINON NAN #########################################
        
            else:
                print('Erreur: la fonction Helium7.VolumeMolaire est invalide pour cette valeur de concentration x = '+str(Concentration3He*100)+' %')
                return np.nan
        else:
            print('Erreur: la fonction Helium7.VolumeMolaire est invalide pour cette valeur de pression P = '+str(Pression)+' Pa')
            return np.nan
    else:
        print('Erreur: la fonction Helium7.VolumeMolaire est invalide pour cette valeur de température T = '+str(Temperature)+' K')
        return np.nan
    

#%% Derivee Volume Molaire - Vérifiée
def DeriveeVolumeMolaire(Temperature,Pression,Concentration3He):

    """
    ========== DESCRIPTION ==========

    Cette fonction permet de déterminer la dérivée du volume molaire du mélange
    Helium3-Helium4 par rapport à la concentration en Helium 3 du mélange 
    en fonction de la temperature, de la pression et de la concentration en Helium3
    du mélange.

    ========== VALIDITE ==========

    0 <= Temperature <= 0.250 K
    0 <= Pression <= 0 Pa
    0 <= Concentration3He <= 8 %

    ========== SOURCE ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (43)

    ========== ENTREE ==========

    [Temperature]
        La température du fluide en [K]
    [Pression]
        La pression en [Pa]
    [Concentration3He]
        La concentration de 3He dans le mélange 3He-4He sans unité

    ========== SORTIE ==========

    [DeriveeVolumeMolaire]
        La dérivée du volume molaire du mélange Helium3-Helium4 en [m3/mol]

    ========== STATUS ==========

    Status : Vérifiée

    ========== A FAIRE ==========

    Contrainte sur la pression à ajouter

    """

    ################## MODULES ###############################################

    import numpy as np
    import Helium4

    ################## CONDITION 1 ############################################
    
    if Temperature <= 0.250 and Temperature >= 0:
        
    ################## CONDITION 2 ############################################
            
        if Pression <= 0 and Pression >= 0:
            
    ################## CONDITION 3 ############################################
        
            if Concentration3He <= 0.08 and Concentration3He >= 0:
        
    ################## INITIALISATION ####################################
        
    ################## FONCTION SI CONDITIONS REMPLIE #####################
        
                return Helium4.VolumeMolaire(Temperature,Pression)*0.286

    ################## SINON NAN #########################################
        
            else:
                print('Erreur: la fonction Helium7.DeriveeVolumeMolaire est invalide pour cette valeur de concentration x = '+str(Concentration3He*100)+' %')
                return np.nan
        else:
            print('Erreur: la fonction Helium7.DeriveeVolumeMolaire est invalide pour cette valeur de pression P = '+str(Pression)+' Pa')
            return np.nan
    else:
        print('Erreur: la fonction Helium7.DeriveeVolumeMolaire est invalide pour cette valeur de température T = '+str(Temperature)+' %')
        return np.nan


#%% Pression Osmotique - Vérifiée
def PressionOsmotique(Temperature,Pression,Concentration3He):

    """
    ========== DESCRIPTION ==========

    Cette fonction permet de déterminer la pression osmotique du mélange Helium3-
    Helium4 en fonction de la température, de la pression et de la concentration
    en Helium 3 du mélange.

    ========== VALIDITE ==========

    0 <= Temperature <= 0.250 K
    0 <= Pression <= 0 Pa
    0 <= Concentration3He <= 8 %

    ========== SOURCE ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (24)

    ========== ENTREE ==========

    [Temperature]
        La température du fluide en [K]
    [Pression]
        La pression en [Pa]
    [Concentration3He]
        La concentration de 3He dans le mélange 3He-4He sans unité

    ========== SORTIE ==========

    [PressionOsmotique]
        La pression osmotique en [Pa]

    ========== STATUS ==========

    Status : Vérifiée

    ========== MISE A JOUR ==========

    2020-02-25:
        Modification des valeurs pour T=0 par un polynôme en utilisant les
        valeurs (Table 19) et non l'équation (45)

    ========== A FAIRE ==========

    Contrainte sur la pression à ajouter
    
    """

    ################## MODULES ###############################################

    import numpy as np
    import Helium4,Fermi

    ################## CONDITION 1 ############################################
    
    if Temperature <= 0.250 and Temperature >= 0:
        
    ################## CONDITION 2 ############################################
            
        if Pression <= 0 and Pression >= 0:
            
    ################## CONDITION 3 ############################################
        
            if Concentration3He <= 0.08 and Concentration3He >= 0:
        
    ################## INITIALISATION ####################################

                Coefficients = [ 7.71714007e+09, -2.28854069e+09,  2.80349751e+08, -2.01610697e+07, 7238437e+06,  3.68490992e+03, -4.60897007e-01]
                Polynome = np.poly1d(Coefficients)
        
    ################## FONCTION SI CONDITIONS REMPLIE #####################
    
                if Temperature == 0:
                        return Polynome(Concentration3He)                 
                else:
                    return PressionOsmotique(0,Pression,Concentration3He) + Concentration3He**2/Helium4.VolumeMolaire(Temperature,Pression)*Fermi.DeriveeTemperature(Temperature,Pression,Concentration3He)*Fermi.IntegraleChaleurSpecifiqueMolaire(Temperature,Pression,Concentration3He)

    ################## SINON NAN #########################################
        
            else:
                print('Erreur: la fonction Helium7.PressionOsmotique est invalide pour cette valeur de concentration x = '+str(Concentration3He*100)+' %')
                return np.nan
        else:
            print('Erreur: la fonction Helium7.PressionOsmotique est invalide pour cette valeur de pression P = '+str(Pression)+' Pa')
            return np.nan
    else:
        print('Erreur: la fonction Helium7.PressionOsmotique est invalide pour cette valeur de température T = '+str(Temperature)+' %')
        return np.nan


#%% DeriveePressionOsmotique - Vérifiée
def DeriveePressionOsmotique(Temperature,Pression,Concentration3He):

    """
    ========== DESCRIPTION ==========

    Cette fonction permet de déterminer la dérivée de la pression osmotique du mélange 3He-4He
    par rapport à la concentration en Helium3 du mélange en fonction de la 
    température, de la pression, et de la concentration en Helium3 du mélange

    ========== VALIDITE ==========

    0 <= Temperature <= 0.250 K
    0 <= Pression <= 0 Pa
    0 <= Concentration3He <= 8 %

    ========== SOURCE ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (62)

    ========== ENTREE ==========

    [Temperature]
        La température du fluide en [K]
    [Pression]
        La pression en [Pa]
    [Concentration3He]
        La concentration de 3He dans le mélange 3He-4He sans unité

    ========== SORTIE ==========

    [DérivéePressionOsmotique]
        La dérivée de la pression osmotique en [Pa]

    ========== STATUS ==========

    Status : En cours
    
    ========== A FAIRE ==========

    Contrainte sur la pression à ajouter

    """
    

    ################## MODULES ###############################################

    import numpy as np
    import Helium4,Fermi

    ################## CONDITION 1 ############################################
    
    if Temperature <= 0.250 and Temperature >= 0:
        
    ################## CONDITION 2 ############################################
            
        if Pression <= 0 and Pression >= 0:
            
    ################## CONDITION 3 ############################################
        
            if Concentration3He <= 0.08 and Concentration3He >= 0:
        
    ################## INITIALISATION ####################################

                a = 0.286
        
    ################## FONCTION SI CONDITIONS REMPLIE #####################
    
                if Temperature == 0:
                    return (3.092e5*5*(Concentration3He/(1+a*Concentration3He))**(2/3))/(3*(1+a*Concentration3He)**2) - (1.32e5*2*Concentration3He)/((1+a*Concentration3He)**2*(1+a*Concentration3He)) -(6.91e5*8*(Concentration3He/(1+a*Concentration3He))**(5/3))/(3*(1+a*Concentration3He)**2)
                else:
                    print('Erreur: la fonction Helium7.DeriveePressionOsmotique est invalide pour cette valeur de température T = '+str(Temperature)+' %')
                    return np.nan

    ################## SINON NAN #########################################
        
            else:
                print('Erreur: la fonction Helium7.DeriveePressionOsmotique est invalide pour cette valeur de concentration x = '+str(Concentration3He*100)+' %')
                return np.nan
        else:
            print('Erreur: la fonction Helium7.DeriveePressionOsmotique est invalide pour cette valeur de pression P = '+str(Pression)+' Pa')
            return np.nan
    else:
        print('Erreur: la fonction Helium7.DeriveePressionOsmotique est invalide pour cette valeur de température T = '+str(Temperature)+' %')
        return np.nan
    

#%% Entropie Molaire - Vérifiée
def EntropieMolaire(Temperature,Pression,Concentration3He):

    """
    ========== DESCRIPTION ==========

    Cette fonction permet de déterminer l'entropie molaire du mélange 3He-4He
    en fonction de la température, de la pression et de la concentration 
    en Helium3 dans le mélange.

    ========== VALIDITE ==========

    0 <= Temperature <= 2 K
    0 <= Pression <= 0 Pa
    0 <= Concentration3He <= 100 %

    ========== SOURCE ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (2)

    ========== ENTREE ==========

    [Temperature]
        La température du fluide en [K]
    [Pression]
        La pression en [Pa]
    [Concentration3He]
        La concentration de 3He dans le mélange 3He-4He sans unité

    ========== SORTIE ==========

    [EntropieMolaire]
        L'entropie molaire du mélange 3He-4He en [J/K/mol]

    ========== STATUS ==========

    Status : Vérifiée

    ========== A FAIRE ==========

    Contrainte sur la pression à vérifier
    A verifier pour les prochaines valeurs de l'entropie 3He et 4He

    """

    ################## MODULES ###############################################

    import Helium4,Fermi,Helium3

    ################## CONDITION 1 ####################################
    # Helium 4 est superfluide, Helium 3 assimilable à un liquide de Fermi
    if Temperature < TemperatureTransition(Pression,Concentration3He) or Concentration3He < ConcentrationConcentre(Temperature,Pression):
        return Concentration3He*Fermi.EntropieMolaire(Temperature,Pression,Concentration3He)+(1-Concentration3He)*Helium4.EntropieMolaire(Temperature,Pression)
    
    else:
    # Helium 4 est normal, Helium 3 est normal
        return Concentration3He*Helium3.EntropieMolaire(Temperature,Pression,Concentration3He)+(1-Concentration3He)*Helium4.EntropieMolaire(Temperature,Pression)


#%% PotentielChimique4He - Vérifiée
def PotentielChimique4He(Temperature,Pression,Concentration3He):

    """
    ========== DESCRIPTION ==========

    Cette fonction permet de déterminer le potentiel chimique de l'Helium4 dans
    un mélange 3He-4He en fonction de la température, de la pression et 
    de la concentration en Helium3 dans le mélange.

    ========== VALIDITE ==========

    0 <= Temperature <= 0.250 K
    0 <= Pression <= 0 Pa
    0 <= Concentration3He <= 8 %

    ========== SOURCE ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (19)

    ========== ENTREE ==========

    [Temperature]
        La température du fluide en [K]
    [Pression]
        La pression en [Pa]
    [Concentration3He]
        La concentration de 3He dans le mélange 3He-4He sans unité

    ========== SORTIE ==========

    [PotentielChimique4He]
        le potentiel chimique de l'Helium4 pur en [J/mol]

    ========== STATUS ==========

    Status : Vérifiée

    """

    ################## MODULES ###############################################

    import numpy as np
    import Helium4

    ################## CONDITION 1 ############################################
    
    if Temperature <= 0.250 and Temperature >= 0:
        
    ################## CONDITION 2 ############################################
            
        if Pression <= 0 and Pression >= 0:
            
    ################## CONDITION 3 ############################################
        
            if Concentration3He <= 0.08 and Concentration3He >= 0:
        
    ################## INITIALISATION ####################################
        
    ################## FONCTION SI CONDITIONS REMPLIE #####################
    
                Helium4.PotentielChimique(Temperature,Pression)-Helium4.VolumeMolaire(Temperature,Pression)*PressionOsmotique(Temperature,Pression,Concentration3He)

    ################## SINON NAN #########################################
        
            else:
                print('Erreur: la fonction Helium7.PotentielChimique4He est invalide pour cette valeur de concentration x = '+str(Concentration3He*100)+' %')
                return np.nan
        else:
            print('Erreur: la fonction Helium7.PotentielChimique4He est invalide pour cette valeur de pression P = '+str(Pression)+' Pa')
            return np.nan
    else:
        print('Erreur: la fonction Helium7.PotentielChimique4He est invalide pour cette valeur de température T = '+str(Temperature)+' %')
        return np.nan


#%% Integrale Pression Osmotique - Vérifiée
def IntegralePressionOsmotique(Temperature,Pression,Concentration3He):

    """
    ========== DESCRIPTION ==========

    Cette fonction permet de déterminer l'intégraler de la pression osmotique du mélange 3He-4He
    par rapport à la Concentration d'Helium 3 divisée par x**2 en fonction de 
    la température, de la pression et de la concentration en Helium 3 dans le 
    mélange

    ========== VALIDITE ==========

    0 <= Temperature <= 0.250 K
    0 <= Pression <= 0 Pa
    0 <= Concentration3He <= 8 %

    ========== SOURCE ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (24)

    ========== ENTREE ==========

    [Temperature]
        La température du fluide en [K]
    [Pression]
        La pression en [Pa]
    [Concentration3He]
        La concentration de 3He dans le mélange 3He-4He sans unité


    ========== SORTIE ==========

    [IntegralePressionOsmotique]
        L'intégrale de la pression osmotique en [Pa]

    ========== STATUS ==========

    Status : Vérifiée
    
    ========== A FAIRE ==========

    Contrainte sur la pression à ajouter

    """

    ################## MODULES ###############################################

    import numpy as np

    ################## CONDITION 1 ############################################
    
    if Temperature <= 0.250 and Temperature >= 0:
        
    ################## CONDITION 2 ############################################
            
        if Pression <= 0 and Pression >= 0:
            
    ################## CONDITION 3 ############################################
        
            if Concentration3He <= 0.08 and Concentration3He >= 0:
        
    ################## INITIALISATION ####################################


                Coefficients = [ 1.10244858e+09, -3.81423449e+08,  5.60699503e+07, -5.04026742e+06,
                3.57461458e+05,  1.84245496e+03, -4.60897007e-01,  0.00000000e+00]
                value = 0
                
    ################## FONCTION SI CONDITIONS REMPLIE #####################
    
                if Temperature == 0:
                    for i in range(len(Coefficients)):
                        value = value+Concentration3He**(i-2)*Coefficients[len(Coefficients)-i-1]
                    return value
                
    ################## SINON NAN #########################################
        
            else:
                print('Erreur: la fonction Helium7.DeriveePressionOsmotique est invalide pour cette valeur de concentration x = '+str(Concentration3He*100)+' %')
                return np.nan
        else:
            print('Erreur: la fonction Helium7.DeriveePressionOsmotique est invalide pour cette valeur de pression P = '+str(Pression)+' Pa')
            return np.nan
    else:
        print('Erreur: la fonction Helium7.DeriveePressionOsmotique est invalide pour cette valeur de température T = '+str(Temperature)+' %')
        return np.nan

#%% TemperatureTriCritique - Vérifiée
def TemperatureTriCritique(Pression):

    """
    ========== DESCRIPTION ==========

    Cette fonction permet de déterminer la température du point TriCritique en 
    fonction de la pression

    ========== VALIDITE ==========

    0 <= Pression <= 22e5 Pa

    ========== SOURCE ==========

    CHAUDHRY (2012) - Thermodynamic properties of liquid 3He-4he mixtures
    between 0.15 K and 1.8 K - Equation (A.4)

    ========== ENTREE ==========

    [Pression]
        La pression subit par le mélange en [Pa]

    ========== SORTIE ==========

    [TemperatureTriCritique]
        La température du point TriCritique en [K]

    ========== STATUS ==========

    Status : Verifiée

    """

    ################## MODULES ###############################################

    import numpy as np

    ################## CONDITION 1 ############################################
    
    if Pression <= 22e5 and Pression >= 0:

        ################## INITIALISATION ####################################
    
        Pression = Pression*1e-5
            
        ################## FONCTION SI CONDITION REMPLIE #####################
        
        if Pression == 0:
            return 0.867
    
        elif Pression <= 22e5 and Pression > 0:
            return TemperatureTriCritique(0) - 0.12992576*Pression/(Pression + 2.5967345)-6.457263e-4*Pression
    
       ################## SINON NAN #########################################

    else:
        print('Erreur: la fonction Helium7.TemperatureTriCritique est invalide pour cette valeur de pression P = '+str(Pression)+' Pa')
        return np.nan
    
#%% ConcentrationTriCritique - Vérifiée
def ConcentrationTriCritique(Pression):

    """
    ========== DESCRIPTION ==========

    Cette fonction permet de déterminer la concentration en 3He du point TriCritique en 
    fonction de la pression

    ========== VALIDITE ==========

    0 <= Pression <= 10e5 Pa

    ========== SOURCE ==========

    CHAUDHRY (2012) - Thermodynamic properties of liquid 3He-4he mixtures
    between 0.15 K and 1.8 K - Equation (A.5)

    ========== ENTREE ==========

    [Pression]
        La pression subit par le mélange en [Pa]

    ========== SORTIE ==========

    [ConcentrationTriCritique]
        La concentration en 3He du point TriCritique sans unité

    ========== STATUS ==========

    Status : Vérifiée

    """

    ################## MODULES ###############################################

    import numpy as np

    ################## CONDITION 1 ############################################
    
    if Pression <= 22e5 and Pression >= 0:

        ################## INITIALISATION ####################################
    
        Pression = Pression*1e-5
            
        ################## FONCTION SI CONDITION REMPLIE #####################
        
        if Pression == 0:
            return 0.674
    
        elif Pression <= 22e5 and Pression > 0:
            return ConcentrationTriCritique(0) + 0.3037124*(TemperatureTriCritique(0)-TemperatureTriCritique(Pression))-4.41225e6*(TemperatureTriCritique(0)-TemperatureTriCritique(Pression))**9
    
       ################## SINON NAN #########################################

    else:
        print('Erreur: la fonction Helium7.ConcentrationTriCritique est invalide pour cette valeur de pression P = '+str(Pression)+' Pa')
        return np.nan
    
    
    
#%% TemperatureTransition - Vérifiée
def TemperatureTransition(Pression,Concentration3He):

    """
    ========== DESCRIPTION ==========

    Cette fonction retourne la température de la transition Normal/Superfluide 
    en fonction de la pression et de la concentration en Helium 3

    ========== VALIDITE ==========

    0 <= Pression <= 15e5 Pa
    0 <= Concentration3He <= Helium7.ConcentrationTriCritique(Pression)
    
    ========== SOURCE ==========

    CHAUDHRY - Thermoduynamic properties of liquid 3He-4He mixtures betxeen
    0.150mK and 1.8K - Equation (2.4)

    ========== ENTREE ==========

    [Pression]
        La pression en Pa
    [Concentration3He]
        La concentration en 3He
        
    ========== SORTIE ==========

    [TemperatureTransition]
        La température de transition normal/superfluide de l'Helium 4 dans
        le mélange Helium3/Helium4

    ========== STATUS ==========

    Status : Vérifiée

    """

    ################## MODULES ###############################################

    import numpy as np

        ################## CONDITIONS ############################################

    if Pression<=15e5 and Pression >= 0.0:
        
        ################## INITIALISATION ####################################

        Pression = Pression*1e-5
        
        Coefficients = np.array([[-0.209148,-0.1269791,0.0102283],
                             [0.960222,-0.2165742,0.0169801],
                             [0.549920,-0.1198491,0.0092997],
                             [0.080280,0.02291499,-0.0020886],
                             [-0.746805,0.0173549,-0.0028598],
                             [-0.180743,0.1120251,-0.0152076],
                             [0.316170,0.1723264,-0.0201411],
                             [-2.620259,0.0024823,0.0009255],
                             [-1.023726,0.0013175,0.0009397]])
        

        ################## FONCTION SI CONDITION REMPLIE #####################

        K1 = Coefficients[7][0]+Coefficients[7][1]*Pression + Coefficients[7][2]*Pression**2
        K2 = Coefficients[8][0]+Coefficients[8][1]*Pression + Coefficients[8][2]*Pression**2
        
        return TemperatureTriCritique(Pression)+K1*(Concentration3He-ConcentrationTriCritique(Pression))+K2*(Concentration3He-ConcentrationTriCritique(Pression))**2

        ################## SINON NAN #########################################

    else:

        print('Erreur: la fonction Helium7.TemperatureTransition est invalide pour cette valeur de pression P = '+str(Pression)+' Pa')
        return np.nan
    
    
#%% ConcentrationDilue - Vérifiée
def ConcentrationDilue(Temperature,Pression):

    """
    ========== DESCRIPTION ==========

    Cette fonction retourne la concentration correspondant à la température
    et la pression dans la phase diluée 

    ========== VALIDITE ==========

    0 <= Temperature <= Helium7.TemperatureTriCritique(Pression)
    0 <= Pression <= 15e5 Pa

    ========== SOURCE ==========

    CHAUDHRY - Thermoduynamic properties of liquid 3He-4He mixtures betxeen
    0.150mK and 1.8K - Equation (2.4)

    ========== ENTREE ==========

    [Temperature]
        La température en K

    ========== SORTIE ==========

    [ConcentrationDilue]
        La Concentration d'Helium3 dans la phase diluee

    ========== STATUS ==========

    Status : Vérifiée

    """

    ################## MODULES ###############################################

    import numpy as np

        ################## CONDITIONS ############################################

    if Pression<=15e5 and Pression >= 0.0:
        
        if Temperature >=0 and Temperature <= TemperatureTriCritique(Pression):
        
            ################## INITIALISATION ####################################
            
            Pression = Pression*1e-5
    
            Coefficients = np.array([[-0.209148,-0.1269791,0.0102283],
                                 [0.960222,-0.2165742,0.0169801],
                                 [0.549920,-0.1198491,0.0092997],
                                 [0.080280,0.02291499,-0.0020886],
                                 [-0.746805,0.0173549,-0.0028598],
                                 [-0.180743,0.1120251,-0.0152076],
                                 [0.316170,0.1723264,-0.0201411],
                                 [-2.620259,0.0024823,0.0009255],
                                 [-1.023726,0.0013175,0.0009397]])
            
    
            ################## FONCTION SI CONDITION REMPLIE #####################
    
            K0 = Coefficients[0][0]+Coefficients[0][1]*Pression + Coefficients[0][2]*Pression**2
            K1 = Coefficients[1][0]+Coefficients[1][1]*Pression + Coefficients[1][2]*Pression**2
            K2 = Coefficients[2][0]+Coefficients[2][1]*Pression + Coefficients[2][2]*Pression**2
            Ka = Coefficients[3][0]+Coefficients[3][1]*Pression + Coefficients[3][2]*Pression**2
            
            return ConcentrationTriCritique(Pression) + K0*(Temperature-TemperatureTriCritique(Pression))/((Temperature-TemperatureTriCritique(Pression))-Ka) + K1*(Temperature-TemperatureTriCritique(Pression))+K2*(Temperature-TemperatureTriCritique(Pression))**2
     
        else: 
            print('Erreur: la fonction Helium7.ConcentrationDiluee est invalide pour cette valeur de température T = '+str(Temperature)+' K.')
            return np.nan
    
            ################## SINON NAN #########################################

    else:

        print('Erreur: la fonction Helium7.ConcentrationDiluee est invalide pour cette valeur de pression P = '+str(Pression*1e5)+' Pa.')
        return np.nan
    
#%% ConcentrationConcentre - 
def ConcentrationConcentre(Temperature,Pression):

    """
    ========== DESCRIPTION ==========

    Cette fonction retourne la concentration correspondant à la température
    et la pression dans la phase concentrée

    ========== VALIDITE ==========

    0 <= Temperature <= Helium7.TemperatureTriCritique(Pression)
    0 <= Pression <= 15e5 Pa

    ========== SOURCE ==========

    CHAUDHRY - Thermoduynamic properties of liquid 3He-4He mixtures betxeen
    0.150mK and 1.8K - Equation (A.8)

    ========== ENTREE ==========

    [Temperature]
        La température en K
    [Pression]
        La pression en Pa

    ========== SORTIE ==========

    [ConcentrationConcentre]
        La concentration d'Helium3 dans la phase concentre

    ========== STATUS ==========

    Status : 

    """

    ################## MODULES ###############################################

    import numpy as np

        ################## CONDITIONS ############################################

    if Pression<=10e5 and Pression >= 0.0:
        
        if Temperature >= DeriveeConcentrationConcentre(Pression) and Temperature <= TemperatureTriCritique(Pression):
        
            ################## INITIALISATION ####################################
            
            Pression = Pression*1e-5
    
            Coefficients = np.array([[-0.209148,-0.1269791,0.0102283],
                                 [0.960222,-0.2165742,0.0169801],
                                 [0.549920,-0.1198491,0.0092997],
                                 [0.080280,0.02291499,-0.0020886],
                                 [-0.746805,0.0173549,-0.0028598],
                                 [-0.180743,0.1120251,-0.0152076],
                                 [0.316170,0.1723264,-0.0201411],
                                 [-2.620259,0.0024823,0.0009255],
                                 [-1.023726,0.0013175,0.0009397]])
            
    
            ################## FONCTION SI CONDITION REMPLIE #####################
    
            K1 = Coefficients[4][0]+Coefficients[4][1]*Pression + Coefficients[4][2]*Pression**2
            K2 = Coefficients[5][0]+Coefficients[5][1]*Pression + Coefficients[5][2]*Pression**2
            K3 = Coefficients[6][0]+Coefficients[6][1]*Pression + Coefficients[6][2]*Pression**2
            
            return ConcentrationTriCritique(Pression) + K1*(Temperature-TemperatureTriCritique(Pression))+K2*(Temperature-TemperatureTriCritique(Pression))**2+K3*(Temperature-TemperatureTriCritique(Pression))**3
                     
        if Temperature < DeriveeConcentrationConcentre(Pression) and Temperature >=0:
            return ConcentrationConcentre(DeriveeConcentrationConcentre(Pression),Pression)
        
        else:
            print('Erreur: la fonction Helium7.ConcentrationConcentre est invalide pour cette valeur de température T = '+str(Temperature)+' K.')
            return np.nan
    
            ################## SINON NAN #########################################

    else:

        print('Erreur: la fonction Helium7.ConcentrationConcentre est invalide pour cette valeur de pression P = '+str(Pression*1e5)+' Pa.')
        return np.nan

#%% DeriveeConcentrationConcentre - 
def DeriveeConcentrationConcentre(Pression):

    """
    ========== DESCRIPTION ==========

    Cette fonction retourne la dérivée par rapport à la température
    de la concentration correspondant à la température et la pression 
    dans la phase concentrée

    ========== VALIDITE ==========

    0 <= Pression <= 15e5 Pa

    ========== SOURCE ==========

    CHAUDHRY - Thermoduynamic properties of liquid 3He-4He mixtures betxeen
    0.150mK and 1.8K - Equation (A.8)

    ========== ENTREE ==========

    [Pression]
        La pression en Pa

    ========== SORTIE ==========

    [ConcentrationConcentre]
        La concentration d'Helium3 dans la phase concentrée  

    ========== STATUS ==========

    Status : 

    """

    ################## MODULES ###############################################

    import numpy as np

        ################## CONDITIONS ############################################

    if Pression<=10e5 and Pression >= 0.0:

            ################## INITIALISATION ####################################
            
            Pression = Pression*1e-5
    
            Coefficients = np.array([[-0.209148,-0.1269791,0.0102283],
                                 [0.960222,-0.2165742,0.0169801],
                                 [0.549920,-0.1198491,0.0092997],
                                 [0.080280,0.02291499,-0.0020886],
                                 [-0.746805,0.0173549,-0.0028598],
                                 [-0.180743,0.1120251,-0.0152076],
                                 [0.316170,0.1723264,-0.0201411],
                                 [-2.620259,0.0024823,0.0009255],
                                 [-1.023726,0.0013175,0.0009397]])
            
    
            ################## FONCTION SI CONDITION REMPLIE #####################
    
            K1 = Coefficients[4][0]+Coefficients[4][1]*Pression + Coefficients[4][2]*Pression**2
            K2 = Coefficients[5][0]+Coefficients[5][1]*Pression + Coefficients[5][2]*Pression**2
            K3 = Coefficients[6][0]+Coefficients[6][1]*Pression + Coefficients[6][2]*Pression**2
            
            
            a = 3*K3
            b = 2*K2 - 6*K3*TemperatureTriCritique(Pression)
            c = K1 + 3*TemperatureTriCritique(Pression)**2*K3-2*TemperatureTriCritique(Pression)*K2
            
            return min(np.roots([a,b,c]))
    
            ################## SINON NAN #########################################

    else:

        print('Erreur: la fonction Helium7.ConcentrationDiluee est invalide pour cette valeur de pression P = '+str(Pression*1e5)+' Pa.')
        return np.nan
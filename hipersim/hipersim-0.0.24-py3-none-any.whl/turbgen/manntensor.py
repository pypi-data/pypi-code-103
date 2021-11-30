# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 09:57:06 2021

@author: nkdi
"""
import numpy as np
def manntensor(k1,k2,k3,gamma_par,L,alphaepsilon,LifetimeModel,ElementChoice = None):
    ksquare = k1**2 + k2**2 + k3**2
    k = np.sqrt( ksquare )
    kL = np.asarray(k*L)
    k1square = k1**2
    k2square = k2**2

    if LifetimeModel == 2: # efficient approximation to the hypergeometric function
        kL[kL < 0.005] = 0.005
        kLsquare = kL**2
        LifeTime = (((1 + kLsquare)**(1/6))/kL)* \
        ( ( 1.2050983316598936 - 0.04079766636961979*kL + 1.1050803451576134*kLsquare)/ \
        ( 1 - 0.04103886513006046*kL + 1.1050902034670118*kLsquare))
        Beta = gamma_par*LifeTime
    elif LifetimeModel == 1:
        Beta = gamma_par/ (kL**(2/3))
    elif LifetimeModel == 0:
    # Numerical evaluation of the hypergeometric function
    # NB!! Not implemented in the Python version yet
        Beta = gamma_par/( (kL**(2/3)) * np.sqrt( HypergeometricFunction(1/3,17/6,4/3,-(kL**(-2)),1,50) ) )

    k30 = k3 + Beta*k1
    k30square = k30**2
    k0square = k1square + k2square + k30square
    k0 = np.sqrt(k0square)
    kL0 = k0*L
    
    with np.errstate(divide='ignore', invalid='ignore'):
        C1 = Beta * k1square * (k0square - 2*k30square + Beta * k1 * k30) / ( (ksquare)*(k1square + k2square) )
        
        C2 = (k2*(k0square)*( (k1square + k2square)**(-3/2) ))* \
            np.arctan2( Beta*k1*np.sqrt( k1square + k2square),( (k0square) - k30*k1*Beta ) )
        
        Ek0 = alphaepsilon*(L**(5/3))*(kL0**4)/((1 + kL0**2)**(17/6))
        
        zeta1 = np.asarray(C1 - (k2/k1)*C2)
        zeta2 = np.asarray((k2/k1)*C1 + C2)
        
        zeta1[k1 == 0] = -Beta[k1 == 0]
        zeta2[k1 == 0] = 0
    
    if ElementChoice == None:
        
        Phi11 = np.asarray((Ek0/(4*np.pi*(k0**4)))*( k0square - k1square - 2*k1*k30*zeta1 + (k1square + k2square)*(zeta1**2)))
        Phi22 = np.asarray((Ek0/(4*np.pi*(k0**4)))*( k0square - k2square - 2*k2*k30*zeta2 + (k1square + k2square)*(zeta2**2)))
        Phi33 = np.asarray((Ek0/(4*np.pi*(k**4)))*(k1square + k2square))
    
        Phi12 = np.asarray((Ek0/(4*np.pi*(k0**4)))*( -k1*k2 - k1*k30*zeta2 - k2*k30*zeta1 + (k1square + k2square)*zeta1*zeta2))
        Phi13 = np.asarray((Ek0/(4*np.pi*(k0square)*(ksquare)))*( -k1*k30 + (k1square + k2square)*zeta1))
        Phi23 = np.asarray((Ek0/(4*np.pi*(k0square)*(ksquare)))*( -k2*k30 + (k1square + k2square)*zeta2))
        
        Phi11[ksquare==0] = 0
        Phi22[ksquare==0] = 0
        Phi33[ksquare==0] = 0
        Phi12[ksquare==0] = 0
        Phi13[ksquare==0] = 0
        Phi23[ksquare==0] = 0
        
        if np.asarray(k1).size == 1:
            Phi = np.array([[Phi11, Phi12, Phi13],[Phi12, Phi22, Phi23],[Phi13,Phi23,Phi33]])
        else:
            Phi = np.array([Phi11,Phi22,Phi33,Phi12,Phi13,Phi23])
            
    else:
        
        if ElementChoice == 11:
            Phi = np.asarray((Ek0/(4*np.pi*(k0**4)))*( k0square - k1square - 2*k1*k30*zeta1 + (k1square + k2square)*(zeta1**2)))
            Phi[ksquare==0] = 0
        elif ElementChoice == 22:
            Phi = np.asarray((Ek0/(4*np.pi*(k0**4)))*( k0square - k2square - 2*k2*k30*zeta2 + (k1square + k2square)*(zeta2**2)))
            Phi[ksquare==0] = 0
        elif ElementChoice == 33:
            Phi = np.asarray((Ek0/(4*np.pi*(k**4)))*(k1square + k2square))
            Phi[ksquare==0] = 0
        elif ElementChoice == 12:
            Phi = np.asarray((Ek0/(4*np.pi*(k0**4)))*( -k1*k2 - k1*k30*zeta2 - k2*k30*zeta1 + (k1square + k2square)*zeta1*zeta2))
            Phi[ksquare==0] = 0
        elif ElementChoice == 13:
            Phi = np.asarray((Ek0/(4*np.pi*(k0square)*(ksquare)))*( -k1*k30 + (k1square + k2square)*zeta1))
            Phi[ksquare==0] = 0
        elif ElementChoice == 23:
            Phi = np.asarray((Ek0/(4*np.pi*(k0square)*(ksquare)))*( -k2*k30 + (k1square + k2square)*zeta2))
            Phi[ksquare==0] = 0
        
    return Phi

def manntensorcomponents(k1,k2,k3,gamma_par,L,alphaepsilon,LifetimeModel,ElementChoice = None):
    ksquare = k1**2 + k2**2 + k3**2
    k = np.sqrt( ksquare )
    kL = np.asarray(k*L)
    k1square = k1**2
    k2square = k2**2

    if LifetimeModel == 2: # efficient approximation to the hypergeometric function
        kL[kL < 0.005] = 0.005
        kLsquare = kL**2
        LifeTime = (((1 + kLsquare)**(1/6))/kL)* \
        ( ( 1.2050983316598936 - 0.04079766636961979*kL + 1.1050803451576134*kLsquare)/ \
        ( 1 - 0.04103886513006046*kL + 1.1050902034670118*kLsquare))
        Beta = gamma_par*LifeTime
    elif LifetimeModel == 1:
        Beta = gamma_par/ (kL**(2/3))
    elif LifetimeModel == 0:
        # Numerical evaluation of the hypergeometric function
        # NB!! Not implemented in the Python version yet
        Beta = gamma_par/( (kL**(2/3))  * np.sqrt( HypergeometricFunction(1/3,17/6,4/3,-(kL**(-2)),1,50) ) )

    k30 = k3 + Beta*k1
    k30square = k30**2
    k0square = k1square + k2square + k30square
    k0 = np.sqrt(k0square)
    kL0 = k0*L
    
    with np.errstate(divide='ignore', invalid='ignore'):
        C1 = Beta * k1square * (k0square - 2*k30square + Beta * k1 * k30) / ( (ksquare)*(k1square + k2square) )
        
        C2 = (k2*(k0square)*( (k1square + k2square)**(-3/2) ))* \
            np.arctan2( Beta*k1*np.sqrt( k1square + k2square),( (k0square) - k30*k1*Beta ) )
    
        Ek0 = alphaepsilon*(L**(5/3))*(kL0**4)/((1 + kL0**2)**(17/6))
        
        zeta1 = np.asarray(C1 - (k2/k1)*C2)
        zeta2 = np.asarray((k2/k1)*C1 + C2)
    
        zeta1[k1 == 0] = -Beta[k1 == 0]
        zeta2[k1 == 0] = 0
            
        Phi11 = np.asarray((Ek0/(4*np.pi*(k0**4)))*( k0square - k1square - 2*k1*k30*zeta1 + (k1square + k2square)*(zeta1**2)))
        Phi22 = np.asarray((Ek0/(4*np.pi*(k0**4)))*( k0square - k2square - 2*k2*k30*zeta2 + (k1square + k2square)*(zeta2**2)))
        Phi33 = np.asarray((Ek0/(4*np.pi*(k**4)))*(k1square + k2square))
    
        Phi12 = np.asarray((Ek0/(4*np.pi*(k0**4)))*( -k1*k2 - k1*k30*zeta2 - k2*k30*zeta1 + (k1square + k2square)*zeta1*zeta2))
        Phi13 = np.asarray((Ek0/(4*np.pi*k0square*ksquare))*( -k1*k30 + (k1square + k2square)*zeta1))
        Phi23 = np.asarray((Ek0/(4*np.pi*k0square*ksquare))*( -k2*k30 + (k1square + k2square)*zeta2))
        
        Phi11[ksquare==0] = 0
        Phi22[ksquare==0] = 0
        Phi33[ksquare==0] = 0
        Phi12[ksquare==0] = 0
        Phi13[ksquare==0] = 0
        Phi23[ksquare==0] = 0
    
    return Phi11,Phi22,Phi33,Phi12,Phi13,Phi23

def manntensor1component(k1,k2,k3,gamma_par,L,alphaepsilon,LifetimeModel,ElementChoice = None):
    ksquare = k1**2 + k2**2 + k3**2
    k = np.sqrt( ksquare )
    kL = np.asarray(k*L)
    k1square = k1**2
    k2square = k2**2

    if LifetimeModel == 2: # efficient approximation to the hypergeometric function
        kL[kL < 0.005] = 0.005
        kLsquare = kL**2
        LifeTime = (((1 + kLsquare)**(1/6))/kL)* \
        ( ( 1.2050983316598936 - 0.04079766636961979*kL + 1.1050803451576134*kLsquare)/ \
        ( 1 - 0.04103886513006046*kL + 1.1050902034670118*kLsquare))
        Beta = gamma_par*LifeTime
    elif LifetimeModel == 1:
        Beta = gamma_par/ (kL**(2/3))
    elif LifetimeModel == 0:
        # Numerical evaluation of the hypergeometric function
        # NB!! Not implemented in the Python version yet
        Beta = gamma_par/( (kL**(2/3))  * np.sqrt( HypergeometricFunction(1/3,17/6,4/3,-(kL**(-2)),1,50) ) )

    k30 = k3 + Beta*k1
    k30square = k30**2
    k0square = k1square + k2square + k30square
    k0 = np.sqrt(k0square)
    kL0 = k0*L
    
    with np.errstate(divide='ignore', invalid='ignore'):
        Ek0 = alphaepsilon*(L**(5/3))*(kL0**4)/((1 + kL0**2)**(17/6))
        if ElementChoice == 11:
            C1 = Beta * k1square * (k0square - 2*k30square + Beta * k1 * k30) / ( (ksquare)*(k1square + k2square) )           
            C2 = (k2*(k0square)*( (k1square + k2square)**(-3/2) ))* \
                np.arctan2( Beta*k1*np.sqrt( k1square + k2square),( (k0square) - k30*k1*Beta ) )
            zeta1 = np.asarray(C1 - (k2/k1)*C2)
            zeta1[k1 == 0] = -Beta[k1 == 0]
            Phi = np.asarray((Ek0/(4*np.pi*(k0**4)))*( k0square - k1square - 2*k1*k30*zeta1 + (k1square + k2square)*(zeta1**2)))
        elif ElementChoice == 22:
            C1 = Beta * k1square * (k0square - 2*k30square + Beta * k1 * k30) / ( (ksquare)*(k1square + k2square) )            
            C2 = (k2*(k0square)*( (k1square + k2square)**(-3/2) ))* \
                np.arctan2( Beta*k1*np.sqrt( k1square + k2square),( (k0square) - k30*k1*Beta ) )
            zeta2 = np.asarray((k2/k1)*C1 + C2)
            zeta2[k1 == 0] = 0
            Phi = np.asarray((Ek0/(4*np.pi*(k0**4)))*( k0square - k2square - 2*k2*k30*zeta2 + (k1square + k2square)*(zeta2**2)))
        elif ElementChoice == 33:
            Phi = np.asarray((Ek0/(4*np.pi*(k**4)))*(k1square + k2square))
        elif ElementChoice == 12:
            C1 = Beta * k1square * (k0square - 2*k30square + Beta * k1 * k30) / ( (ksquare)*(k1square + k2square) )            
            C2 = (k2*(k0square)*( (k1square + k2square)**(-3/2) ))* \
                np.arctan2( Beta*k1*np.sqrt( k1square + k2square),( (k0square) - k30*k1*Beta ) )
            zeta1 = np.asarray(C1 - (k2/k1)*C2)
            zeta2 = np.asarray((k2/k1)*C1 + C2)
            zeta1[k1 == 0] = -Beta[k1 == 0]
            zeta2[k1 == 0] = 0
            Phi = np.asarray((Ek0/(4*np.pi*(k0**4)))*( -k1*k2 - k1*k30*zeta2 - k2*k30*zeta1 + (k1square + k2square)*zeta1*zeta2))
        elif ElementChoice == 13:
            C1 = Beta * k1square * (k0square - 2*k30square + Beta * k1 * k30) / ( (ksquare)*(k1square + k2square) )
            
            C2 = (k2*(k0square)*( (k1square + k2square)**(-3/2) ))* \
                np.arctan2( Beta*k1*np.sqrt( k1square + k2square),( (k0square) - k30*k1*Beta ) )
            zeta1 = np.asarray(C1 - (k2/k1)*C2)
            zeta1[k1 == 0] = -Beta[k1 == 0]
            Phi = np.asarray((Ek0/(4*np.pi*(k0square)*(ksquare)))*( -k1*k30 + (k1square + k2square)*zeta1))
        elif ElementChoice == 23:
            C1 = Beta * k1square * (k0square - 2*k30square + Beta * k1 * k30) / ( (ksquare)*(k1square + k2square) )
            
            C2 = (k2*(k0square)*( (k1square + k2square)**(-3/2) ))* \
                np.arctan2( Beta*k1*np.sqrt( k1square + k2square),( (k0square) - k30*k1*Beta ) )
            zeta2 = np.asarray((k2/k1)*C1 + C2)
            zeta2[k1 == 0] = 0
            Phi = np.asarray((Ek0/(4*np.pi*(k0square)*(ksquare)))*( -k2*k30 + (k1square + k2square)*zeta2))
            
    Phi[ksquare==0] = 0
    return Phi

def manntensor_scalark(k1,k2,k3,gamma_par,L,alphaepsilon,LifetimeModel):
    ksquare = k1**2 + k2**2 + k3**2
    k = np.sqrt( ksquare )
    
    if k==0:
        Phi = np.zeros(3,3)
    else:
        kL = k*L
        k1square = k1**2
        k2square = k2**2

        if LifetimeModel == 2: # efficient approximation to the hypergeometric function
            if kL < 0.005:
                kL = 0.005
            kLsquare = kL**2
            LifeTime = (((1 + kLsquare)**(1/6))/kL)* \
            ( ( 1.2050983316598936 - 0.04079766636961979*kL + 1.1050803451576134*kLsquare)/ \
            ( 1 - 0.04103886513006046*kL + 1.1050902034670118*kLsquare))
            Beta = gamma_par*LifeTime
        elif LifetimeModel == 1:
            Beta = gamma_par/ (kL**(2/3))
        elif LifetimeModel == 0:
        # Numerical evaluation of the hypergeometric function
        # NB!! Not implemented in the Python version yet
            Beta = gamma_par/( (kL**(2/3)) * np.sqrt( HypergeometricFunction(1/3,17/6,4/3,-(kL**(-2)),1,50) ) )

        k30 = k3 + Beta*k1
        k30square = k30**2
        k0square = k1square + k2square + k30square
        k0 = np.sqrt(k0square)
        kL0 = k0*L
        
        C1 = Beta * k1square * (k0square - 2*k30square + Beta * k1 * k30) / ( (ksquare)*(k1square + k2square) )
        
        C2 = (k2*(k0square)*( (k1square + k2square)**(-3/2) ))* \
            np.arctan2( Beta*k1*np.sqrt( k1square + k2square),( (k0square) - k30*k1*Beta ) )
        
        Ek0 = alphaepsilon*(L**(5/3))*(kL0**4)/((1 + kL0**2)**(17/6))
        if k1 == 0:
            zeta1 = -Beta
            zeta2 = 0
        else:
            zeta1 = C1 - (k2/k1)*C2
            zeta2 = (k2/k1)*C1 + C2
        
        Phi11 = (Ek0/(4*np.pi*(k0**4)))*( k0square - k1square - 2*k1*k30*zeta1 + (k1square + k2square)*(zeta1**2))
        Phi22 = (Ek0/(4*np.pi*(k0**4)))*( k0square - k2square - 2*k2*k30*zeta2 + (k1square + k2square)*(zeta2**2))
        Phi33 = (Ek0/(4*np.pi*(k**4)))*(k1square + k2square)
    
        Phi12 = (Ek0/(4*np.pi*(k0**4)))*( -k1*k2 - k1*k30*zeta2 - k2*k30*zeta1 + (k1square + k2square)*zeta1*zeta2)
        Phi13 = (Ek0/(4*np.pi*(k0square)*(ksquare)))*( -k1*k30 + (k1square + k2square)*zeta1)
        Phi23 = (Ek0/(4*np.pi*(k0square)*(ksquare)))*( -k2*k30 + (k1square + k2square)*zeta2)
        
        Phi = np.array([[Phi11, Phi12, Phi13],[Phi12, Phi22, Phi23],[Phi13,Phi23,Phi33]])
        
    return Phi

def manntensorsqrt(k1,k2,k3,gamma_par,L,alphaepsilon,LifetimeModel,ElementChoice = None):
    ksquare = k1**2 + k2**2 + k3**2
    k = np.sqrt( ksquare )
    kL = np.asarray(k*L)
    k1square = k1**2
    k2square = k2**2

    if LifetimeModel == 2: # efficient approximation to the hypergeometric function
        kL[kL < 0.005] = 0.005
        kLsquare = kL**2
        LifeTime = (((1 + kLsquare)**(1/6))/kL)* \
        ( ( 1.2050983316598936 - 0.04079766636961979*kL + 1.1050803451576134*kLsquare)/ \
        ( 1 - 0.04103886513006046*kL + 1.1050902034670118*kLsquare))
        Beta = gamma_par*LifeTime
    elif LifetimeModel == 1:
        Beta = gamma_par/ (kL**(2/3))
    elif LifetimeModel == 0:
    # Numerical evaluation of the hypergeometric function
    # NB!! Not implemented in the Python version yet
        Beta = gamma_par/( (kL**(2/3)) * np.sqrt( HypergeometricFunction(1/3,17/6,4/3,-(kL**(-2)),1,50) ) )

    k30 = k3 + Beta*k1
    k30square = k30**2
    k0square = k1square + k2square + k30square
    k0 = np.sqrt(k0square)
    kL0 = k0*L
    
    C1 = Beta * k1square * (k0square - 2*k30square + Beta * k1 * k30) / ( (ksquare)*(k1square + k2square) )
    
    C2 = (k2*(k0square)*( (k1square + k2square)**(-3/2) ))* \
        np.arctan2( Beta*k1*np.sqrt( k1square + k2square),( (k0square) - k30*k1*Beta ) )
    
    Ek0 = alphaepsilon*(L**(5/3))*(kL0**4)/((1 + kL0**2)**(17/6))
    
    zeta1 = np.asarray(C1 - (k2/k1)*C2)
    zeta2 = np.asarray((k2/k1)*C1 + C2)
    
    zeta1[k1 == 0] = -Beta[k1 == 0]
    zeta2[k1 == 0] = 0
    
    kL0 = k0*L
    Ek0 = alphaepsilon*(L**(5/3))*(kL0**4)/((1 + kL0**2)**(17/6))
    Ek4 = np.sqrt(Ek0/(4*np.pi*(k0**4)))
    kk = (k0**2)/(k**2)
    
    Phi11 = Ek4*zeta1*k2
    Phi12 = Ek4*(k30 - zeta1*k1)
    Phi13 = Ek4*(-k2)
    Phi21 = Ek4*(-k30 + zeta2*k2)
    Phi22 = Ek4*(-zeta2*k1)
    Phi23 = Ek4*(k1)
    Phi31 = Ek4*(k2*kk)
    Phi32 = Ek4*(-k1*kk)
    Phi33 = k1*0
    if np.asarray(k1).size == 1:
        if k == 0:
            Phi = np.zeros(3,3)
        else:
            Phi = np.array([[Phi11,Phi12,Phi13],[Phi21,Phi22,Phi23],[Phi31,Phi32,Phi33]])
    else:
        Phi = np.array([Phi11,Phi12,Phi13,Phi21,Phi22,Phi23,Phi31,Phi32,Phi33])
    
    return Phi

def manntensorsqrtcomponents(k1,k2,k3,gamma_par,L,alphaepsilon,LifetimeModel,ElementChoice = None,VarianceRatios = None):
    ksquare = k1**2 + k2**2 + k3**2
    k = np.sqrt( ksquare )
    kL = np.asarray(k*L)
    k1square = k1**2
    k2square = k2**2

    if LifetimeModel == 2: # efficient approximation to the hypergeometric function
        kL[kL < 0.005] = 0.005
        kLsquare = kL**2
        LifeTime = (((1 + kLsquare)**(1/6))/kL)* \
        ( ( 1.2050983316598936 - 0.04079766636961979*kL + 1.1050803451576134*kLsquare)/ \
        ( 1 - 0.04103886513006046*kL + 1.1050902034670118*kLsquare))
        Beta = gamma_par*LifeTime
    elif LifetimeModel == 1:
        Beta = gamma_par/ (kL**(2/3))
    elif LifetimeModel == 0:
    # Numerical evaluation of the hypergeometric function
    # NB!! Not implemented in the Python version yet
        Beta = gamma_par/( (kL**(2/3)) * np.sqrt( HypergeometricFunction(1/3,17/6,4/3,-(kL**(-2)),1,50) ) )

    k30 = k3 + Beta*k1
    k30square = k30**2
    k0square = k1square + k2square + k30square
    k0 = np.sqrt(k0square)
    
    with np.errstate(divide='ignore', invalid='ignore'):

    
        C1 = Beta * k1square * (k0square - 2*k30square + Beta * k1 * k30) / ( (ksquare)*(k1square + k2square) )
        
        C2 = (k2*(k0square)*( (k1square + k2square)**(-3/2) ))* \
            np.arctan2( Beta*k1*np.sqrt( k1square + k2square),( (k0square) - k30*k1*Beta ) )
                
        zeta1 = np.asarray(C1 - (k2/k1)*C2)
        zeta2 = np.asarray((k2/k1)*C1 + C2)
        
        zeta1[k1 == 0] = -Beta[k1 == 0]
        zeta2[k1 == 0] = 0
        
        kL0 = k0*L
        Ek0 = alphaepsilon*(L**(5/3))*(kL0**4)/((1 + kL0**2)**(17/6))
        Ek4 = np.sqrt(Ek0/(4*np.pi*(k0**4)))
        kk = (k0**2)/(k**2)
        
    if VarianceRatios is None:
        Phi11 = Ek4*zeta1*k2
        Phi12 = Ek4*(k30 - zeta1*k1)
        Phi13 = Ek4*(-k2)
        Phi21 = Ek4*(-k30 + zeta2*k2)
        Phi22 = Ek4*(-zeta2*k1)
        Phi23 = Ek4*(k1)
        Phi31 = Ek4*(k2*kk)
        Phi32 = Ek4*(-k1*kk)
        Phi33 = k1*0        
    else:
        Phi11 = Ek4*zeta1*k2
        Phi12 = Ek4*(k30*VarianceRatios[0] - zeta1*k1)
        Phi13 = Ek4*(-k2*VarianceRatios[0])
        Phi21 = Ek4*(-k30*VarianceRatios[1] + zeta2*k2)
        Phi22 = Ek4*(-zeta2*k1)
        Phi23 = Ek4*(k1*VarianceRatios[1])
        Phi31 = Ek4*(k2*kk*VarianceRatios[2])
        Phi32 = Ek4*(-k1*kk*VarianceRatios[2])
        Phi33 = k1*0               

        
    
    Phi11[ksquare==0] = 0
    Phi12[ksquare==0] = 0
    Phi13[ksquare==0] = 0
    Phi21[ksquare==0] = 0
    Phi22[ksquare==0] = 0    
    Phi23[ksquare==0] = 0
    Phi31[ksquare==0] = 0
    Phi32[ksquare==0] = 0
    Phi33[ksquare==0] = 0
    
    return Phi11,Phi12,Phi13,Phi21,Phi22,Phi23,Phi31,Phi32,Phi33

def manntensorsqrt_scalark(k1,k2,k3,gamma_par,L,alphaepsilon,LifetimeModel,Phi = None):
    ksquare = k1**2 + k2**2 + k3**2
    k = np.sqrt( ksquare )
    if Phi is None:
        Phi = np.zeros(3,3)
    
    if k==0:
        Phi = np.zeros(3,3)
    else:
        kL = k*L
        k1square = k1**2
        k2square = k2**2

        if LifetimeModel == 2: # efficient approximation to the hypergeometric function
            if kL < 0.005:
                kL = 0.005
            kLsquare = kL**2
            LifeTime = (((1 + kLsquare)**(1/6))/kL)* \
            ( ( 1.2050983316598936 - 0.04079766636961979*kL + 1.1050803451576134*kLsquare)/ \
            ( 1 - 0.04103886513006046*kL + 1.1050902034670118*kLsquare))
            Beta = gamma_par*LifeTime
        elif LifetimeModel == 1:
            Beta = gamma_par/ (kL**(2/3))
        elif LifetimeModel == 0:
        # Numerical evaluation of the hypergeometric function
        # NB!! Not implemented in the Python version yet
            Beta = gamma_par/( (kL**(2/3)) * np.sqrt( HypergeometricFunction(1/3,17/6,4/3,-(kL**(-2)),1,50) ) )

        k30 = k3 + Beta*k1
        k30square = k30**2
        k0square = k1square + k2square + k30square
        k0 = np.sqrt(k0square)
        kL0 = k0*L
        with np.errstate(divide='ignore', invalid='ignore'):
            C1 = Beta * k1square * (k0square - 2*k30square + Beta * k1 * k30) / ( (ksquare)*(k1square + k2square) )
            
            C2 = (k2*(k0square)*( (k1square + k2square)**(-3/2) ))* \
                np.arctan2( Beta*k1*np.sqrt( k1square + k2square),( (k0square) - k30*k1*Beta ) )
            
            Ek0 = alphaepsilon*(L**(5/3))*(kL0**4)/((1 + kL0**2)**(17/6))
            if k1 == 0:
                zeta1 = -Beta
                zeta2 = 0
            else:
                zeta1 = C1 - (k2/k1)*C2
                zeta2 = (k2/k1)*C1 + C2
    
        kL0 = k0*L
        Ek0 = alphaepsilon*(L**(5/3))*(kL0**4)/((1 + kL0**2)**(17/6))
        Ek4 = np.sqrt(Ek0/(4*np.pi*(k0**4)))
        kk = (k0**2)/(k**2)
        
        Phi11 = Ek4*zeta1*k2
        Phi12 = Ek4*(k30 - zeta1*k1)
        Phi13 = Ek4*(-k2)
        Phi21 = Ek4*(-k30 + zeta2*k2)
        Phi22 = Ek4*(-zeta2*k1)
        Phi23 = Ek4*(k1)
        Phi31 = Ek4*(k2*kk)
        Phi32 = Ek4*(-k1*kk)
        Phi33 = k1*0
        
        Phi[0,0] = Phi11
        Phi[0,1] = Phi12
        Phi[0,2] = Phi13
        Phi[1,0] = Phi21
        Phi[1,1] = Phi22
        Phi[1,2] = Phi23
        Phi[2,0] = Phi31
        Phi[2,1] = Phi32
        Phi[2,2] = Phi33

        #Phi = np.array([[Phi11,Phi12,Phi13],[Phi21,Phi22,Phi23],[Phi31,Phi32,Phi33]])
        
    return Phi

def manntensorsqrt1component(k1,k2,k3,gamma_par,L,alphaepsilon,LifetimeModel,ElementChoice = None):
    ksquare = k1**2 + k2**2 + k3**2
    k = np.sqrt( ksquare )
    kL = np.asarray(k*L)
    k1square = k1**2
    k2square = k2**2

    if LifetimeModel == 2: # efficient approximation to the hypergeometric function
        kL[kL < 0.005] = 0.005
        kLsquare = kL**2
        LifeTime = (((1 + kLsquare)**(1/6))/kL)* \
        ( ( 1.2050983316598936 - 0.04079766636961979*kL + 1.1050803451576134*kLsquare)/ \
        ( 1 - 0.04103886513006046*kL + 1.1050902034670118*kLsquare))
        Beta = gamma_par*LifeTime
    elif LifetimeModel == 1:
        Beta = gamma_par/ (kL**(2/3))
    elif LifetimeModel == 0:
    # Numerical evaluation of the hypergeometric function
    # NB!! Not implemented in the Python version yet
        Beta = gamma_par/( (kL**(2/3)) * np.sqrt( HypergeometricFunction(1/3,17/6,4/3,-(kL**(-2)),1,50) ) )

    k30 = k3 + Beta*k1
    k30square = k30**2
    k0square = k1square + k2square + k30square
    k0 = np.sqrt(k0square)
    kL0 = k0*L
    
    with np.errstate(divide='ignore', invalid='ignore'):
        Ek0 = alphaepsilon*(L**(5/3))*(kL0**4)/((1 + kL0**2)**(17/6))
        Ek4 = np.sqrt(Ek0/(4*np.pi*(k0**4)))

        if ElementChoice == 11:
    
            C1 = Beta * k1square * (k0square - 2*k30square + Beta * k1 * k30) / ( (ksquare)*(k1square + k2square) )            
            C2 = (k2*(k0square)*( (k1square + k2square)**(-3/2) ))* \
                np.arctan2( Beta*k1*np.sqrt( k1square + k2square),( (k0square) - k30*k1*Beta ) )            
            zeta1 = np.asarray(C1 - (k2/k1)*C2)            
            zeta1[k1 == 0] = -Beta[k1 == 0]            
            Phi = Ek4*zeta1*k2                                    
        elif ElementChoice == 12:
            C1 = Beta * k1square * (k0square - 2*k30square + Beta * k1 * k30) / ( (ksquare)*(k1square + k2square) )            
            C2 = (k2*(k0square)*( (k1square + k2square)**(-3/2) ))* \
                np.arctan2( Beta*k1*np.sqrt( k1square + k2square),( (k0square) - k30*k1*Beta ) )
            zeta1 = np.asarray(C1 - (k2/k1)*C2)
            zeta1[k1 == 0] = -Beta[k1 == 0]
            Phi = Ek4*(k30 - zeta1*k1)            
        elif ElementChoice == 13:
            Phi = Ek4*(-k2)
        elif ElementChoice == 21:
            C1 = Beta * k1square * (k0square - 2*k30square + Beta * k1 * k30) / ( (ksquare)*(k1square + k2square) )           
            C2 = (k2*(k0square)*( (k1square + k2square)**(-3/2) ))* \
                np.arctan2( Beta*k1*np.sqrt( k1square + k2square),( (k0square) - k30*k1*Beta ) )
            zeta2 = np.asarray((k2/k1)*C1 + C2)
            zeta2[k1 == 0] = 0            
            Phi = Ek4*(-k30 + zeta2*k2)
        elif ElementChoice == 22:
            C1 = Beta * k1square * (k0square - 2*k30square + Beta * k1 * k30) / ( (ksquare)*(k1square + k2square) )           
            C2 = (k2*(k0square)*( (k1square + k2square)**(-3/2) ))* \
                np.arctan2( Beta*k1*np.sqrt( k1square + k2square),( (k0square) - k30*k1*Beta ) )
            zeta2 = np.asarray((k2/k1)*C1 + C2)
            zeta2[k1 == 0] = 0
            Phi = Ek4*(-zeta2*k1)            
        elif ElementChoice == 23:            
            Phi = Ek4*(k1)
        elif ElementChoice == 31:
            kk = (k0**2)/(k**2)
            Phi = Ek4*(k2*kk)
        elif ElementChoice == 32:
            kk = (k0**2)/(k**2)
            Phi = Ek4*(-k1*kk)
        elif ElementChoice == 33:
            Phi = k1*0
    Phi[ksquare==0] = 0
    return Phi

def HypergeometricFunction(a,b,c,z):
    # Not implemented yet
    return 0

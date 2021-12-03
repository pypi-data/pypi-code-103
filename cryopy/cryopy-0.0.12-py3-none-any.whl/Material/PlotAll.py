#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 14:05:48 2021

@author: valentinsauvage
"""



def ThermalConductivity():
    
    """
    ========== DESCRIPTION ==========

    This function plot the thermal conductivity of cryopy referenced materials 

    ========== STATUS ==========

    Status : Checked

    """
    
    import matplotlib.pyplot as plt
    import numpy as np
    
    Legend = []
    plt.figure()
    
    # Teflon
    import Teflon
    Temperature = np.arange(4,300,0.1)
    ThermalConductivity = [Teflon.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('Teflon')
    
    # Al6061-T6
    import Al6061T6
    Temperature = np.arange(4,300,0.1)
    ThermalConductivity = [Al6061T6.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('Al6061-T6')
    
    # G10norm
    import G10norm
    Temperature = np.arange(10,300,0.1)
    ThermalConductivity = [G10norm.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('G-10 (norm)')

    # G10warp
    import G10warp
    Temperature = np.arange(12,300,0.1)
    ThermalConductivity = [G10warp.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('G-10 (warp)')
    
    # G10
    import SS304
    Temperature = np.arange(4,300,0.1)
    ThermalConductivity = [SS304.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('SS 304')
    
    # Inconel718
    import Inconel718
    Temperature = np.arange(4,300,0.1)
    ThermalConductivity = [Inconel718.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('Inconel 718')
    
    
    # CuBe
    import CuBe
    Temperature = np.arange(4,300,0.1)
    ThermalConductivity = [CuBe.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('Copper Beryllium')
    
    # CuBe
    import Ti90Al6V4
    Temperature = np.arange(20,300,0.1)
    ThermalConductivity = [Ti90Al6V4.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('Ti-6Al-4V') 
    
    # CuOFHC
    import CuOFHC
    Temperature = np.arange(4,300,0.1)
    ThermalConductivity = [CuOFHC.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('OFHC Copper')   
    
    # Nylon
    import Nylon
    Temperature = np.arange(4,300,0.1)
    ThermalConductivity = [Nylon.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('Nylon')   
    
    # Kapton 
    import Kapton
    Temperature = np.arange(4,300,0.1)
    ThermalConductivity = [Kapton.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('Kapton')   
    
    # Al1100 
    import Al1100
    Temperature = np.arange(4,300,0.1)
    ThermalConductivity = [Al1100.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('Al1100') 
    
    # Al3003F 
    import Al3003F
    Temperature = np.arange(4,300,0.1)
    ThermalConductivity = [Al3003F.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('Al3003-F')   
  
    # Al5083O 
    import Al5083O
    Temperature = np.arange(4,300,0.1)
    ThermalConductivity = [Al5083O.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('Al5083-O') 
    
    # Al6063T5 
    import Al6063T5
    Temperature = np.arange(4,295,0.1)
    ThermalConductivity = [Al6063T5.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('Al6063-T5') 
    
    # Brass 
    import Brass
    Temperature = np.arange(5,110,0.1)
    ThermalConductivity = [Brass.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('Brass') 
    
    # Cu64Ni16Zn20 
    import Cu64Ni16Zn20
    Temperature = np.arange(2,20,0.1)
    ThermalConductivity = [Cu64Ni16Zn20.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('Cu64Ni16Zn20') 
    
    # Cu46Ni13Zn41 
    import Cu46Ni13Zn41
    Temperature = np.arange(2,20,0.1)
    ThermalConductivity = [Cu46Ni13Zn41.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('Cu46Ni13Zn41') 
    
    # Ni60Cr15Fe16Mo7 
    import Ni60Cr15Fe16Mo7
    Temperature = np.arange(2,20,0.1)
    ThermalConductivity = [Ni60Cr15Fe16Mo7.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('Ni60Cr15Fe16Mo7')
    
    
    # Cu80Ni20 
    import Cu80Ni20
    Temperature = np.arange(2,20,0.1)
    ThermalConductivity = [Cu80Ni20.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('Cu80Ni20') 
    
    # Cu70Ni30 
    import Cu70Ni30
    Temperature = np.arange(0.05,4,0.1)
    ThermalConductivity = [Cu70Ni30.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('Cu70Ni30') 
    
    
    # NiTi 
    import NiTi
    Temperature = np.arange(0.1,9,0.1)
    ThermalConductivity = [NiTi.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('NiTi') 
    
    # Manganin 
    import Manganin
    Temperature = np.arange(1,4,0.1)
    ThermalConductivity = [Manganin.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('Manganin') 
    
    # Kevlar29 
    import Kevlar29
    Temperature = np.arange(1.8,40,0.1)
    ThermalConductivity = [Kevlar29.ThermalConductivity(T) for T in Temperature]
    plt.loglog(Temperature,ThermalConductivity)
    Legend.append('Kevlar29') 
    
    
    plt.xlabel('Temperature [K]')
    plt.ylabel(r'Thermal Conductivity $[W.m^{-1}.K^{-1}]$')
    plt.grid()
    plt.legend(Legend)
    plt.title(r'Thermal Conductivity of some materials from $cryopy$')
    
#%%
def SpecificHeat():
    
    """
    ========== DESCRIPTION ==========

    This function plot the specific heat of cryopy referenced materials 

    ========== STATUS ==========

    Status : Checked

    """
    
    import matplotlib.pyplot as plt
    import numpy as np
    
    Legend = []
    plt.figure()
    
    # Al6061-T6
    import Al6061T6
    Temperature = np.arange(4,300,0.1)
    SpecificHeat = [Al6061T6.SpecificHeat(T) for T in Temperature]
    plt.loglog(Temperature,SpecificHeat)
    Legend.append('Al6061-T6')
 
    # OFHC Copper
    import CuOFHC
    Temperature = np.arange(3,300,0.1)
    SpecificHeat = [CuOFHC.SpecificHeat(T) for T in Temperature]
    plt.loglog(Temperature,SpecificHeat)
    Legend.append('OHFC copper')
    
    # SS304
    import SS304
    Temperature = np.arange(3,300,0.1)
    SpecificHeat = [SS304.SpecificHeat(T) for T in Temperature]
    plt.loglog(Temperature,SpecificHeat)
    Legend.append('SS 304')
    
    # SS304L
    import SS304L
    Temperature = np.arange(4,20,0.1)
    SpecificHeat = [SS304L.SpecificHeat(T) for T in Temperature]
    plt.loglog(Temperature,SpecificHeat)
    Legend.append('SS 304L')
    
    # G10
    import G10norm
    Temperature = np.arange(3,300,0.1)
    SpecificHeat = [G10norm.SpecificHeat(T) for T in Temperature]
    plt.loglog(Temperature,SpecificHeat)
    Legend.append('G-10')

    # Teflon
    import Teflon
    Temperature = np.arange(3,300,0.1)
    SpecificHeat = [Teflon.SpecificHeat(T) for T in Temperature]
    plt.loglog(Temperature,SpecificHeat)
    Legend.append('Teflon')
    
    # Al3003F
    import Al3003F
    Temperature = np.arange(3,300,0.1)
    SpecificHeat = [Al3003F.SpecificHeat(T) for T in Temperature]
    plt.loglog(Temperature,SpecificHeat)
    Legend.append('Al3003-F')
    
    # Al5083O
    import Al5083O
    Temperature = np.arange(4,300,0.1)
    SpecificHeat = [Al5083O.SpecificHeat(T) for T in Temperature]
    plt.loglog(Temperature,SpecificHeat)
    Legend.append('Al5083-O')
    
    # ApiezonN
    import ApiezonN
    Temperature = np.arange(2,200,0.1)
    SpecificHeat = [ApiezonN.SpecificHeat(T) for T in Temperature]
    plt.loglog(Temperature,SpecificHeat)
    Legend.append('Apiezon N grease')
    
    # Be
    import Be
    Temperature = np.arange(14,284,0.1)
    SpecificHeat = [Be.SpecificHeat(T) for T in Temperature]
    plt.loglog(Temperature,SpecificHeat)
    Legend.append('Beryllium')
    
    plt.xlabel('Temperature [K]')
    plt.ylabel(r'Specific heat $[J.kg^{-1}.K^{-1}]$')
    plt.grid()
    plt.legend(Legend)
    plt.title(r'Specific heat of some materials from $cryopy$')
    
#%%
def LinearThermalExpansion():
    
    """
    ========== DESCRIPTION ==========

    This function plot the specific heat of cryopy referenced materials 

    ========== STATUS ==========

    Status : Checked

    """
    
    import matplotlib.pyplot as plt
    import numpy as np
    
    Legend = []
    plt.figure()
    
    # Al6061-T6
    import Al6061T6
    Temperature = np.arange(4,300,0.1)
    LinearThermalExpansion = [Al6061T6.LinearThermalExpansion(T) for T in Temperature]
    plt.plot(Temperature,LinearThermalExpansion)
    Legend.append('Al6061-T6')
    
    # SS304
    import SS304
    Temperature = np.arange(4,300,0.1)
    LinearThermalExpansion = [SS304.LinearThermalExpansion(T) for T in Temperature]
    plt.plot(Temperature,LinearThermalExpansion)
    Legend.append('SS 304')   

    # Inconel718
    import Inconel718
    Temperature = np.arange(4,300,0.1)
    LinearThermalExpansion = [Inconel718.LinearThermalExpansion(T) for T in Temperature]
    plt.plot(Temperature,LinearThermalExpansion)
    Legend.append('Inconel 718')   
    
    # CuBe
    import CuBe
    Temperature = np.arange(4,300,0.1)
    LinearThermalExpansion = [CuBe.LinearThermalExpansion(T) for T in Temperature]
    plt.plot(Temperature,LinearThermalExpansion)
    Legend.append('Copper Beryllium')  
    
    # Ti90Al6V4
    import Ti90Al6V4
    Temperature = np.arange(4,300,0.1)
    LinearThermalExpansion = [Ti90Al6V4.LinearThermalExpansion(T) for T in Temperature]
    plt.plot(Temperature,LinearThermalExpansion)
    Legend.append('Ti-6Al-4V')  

    # NiTi
    import NiTi
    Temperature = np.arange(4,300,0.1)
    LinearThermalExpansion = [NiTi.LinearThermalExpansion(T) for T in Temperature]
    plt.plot(Temperature,LinearThermalExpansion)
    Legend.append('NiTi')  
    
    # Teflon
    import Teflon
    Temperature = np.arange(4,300,0.1)
    LinearThermalExpansion = [Teflon.LinearThermalExpansion(T) for T in Temperature]
    plt.plot(Temperature,LinearThermalExpansion)
    Legend.append('Teflon')          
    
    # Nylon
    import Nylon
    Temperature = np.arange(4,300,0.1)
    LinearThermalExpansion = [Nylon.LinearThermalExpansion(T) for T in Temperature]
    plt.plot(Temperature,LinearThermalExpansion)
    Legend.append('Nylon')   
    
    # G10norm
    import G10norm
    Temperature = np.arange(4,300,0.1)
    LinearThermalExpansion = [G10norm.LinearThermalExpansion(T) for T in Temperature]
    plt.plot(Temperature,LinearThermalExpansion)
    Legend.append('G-10 (norm)')   
    
    # G10warp
    import G10warp
    Temperature = np.arange(4,300,0.1)
    LinearThermalExpansion = [G10warp.LinearThermalExpansion(T) for T in Temperature]
    plt.plot(Temperature,LinearThermalExpansion)
    Legend.append('G-10 (warp)')  
    
    # Al3003F
    import Al3003F
    Temperature = np.arange(4,300,0.1)
    LinearThermalExpansion = [Al3003F.LinearThermalExpansion(T) for T in Temperature]
    plt.plot(Temperature,LinearThermalExpansion)
    Legend.append('AL3003-F')  
    
    # Al5083O
    import Al5083O
    Temperature = np.arange(4,300,0.1)
    LinearThermalExpansion = [Al5083O.LinearThermalExpansion(T) for T in Temperature]
    plt.plot(Temperature,LinearThermalExpansion)
    Legend.append('Al5083-O')
    
    # Al6061T6
    import Al6061T6
    Temperature = np.arange(4,300,0.1)
    LinearThermalExpansion = [Al6061T6.LinearThermalExpansion(T) for T in Temperature]
    plt.plot(Temperature,LinearThermalExpansion)
    Legend.append('Al6061-T6')  
    
    plt.xlabel('Temperature [K]')
    plt.ylabel(r'Linear thermal expansion $[\%]$')
    plt.grid()
    plt.legend(Legend)
    plt.title(r'The linear thermal expansion of some materials from $cryopy$')
    
    
#%%
def YoungsModulus():
    
    """
    ========== DESCRIPTION ==========

    This function plot the specific heat of cryopy referenced materials 

    ========== STATUS ==========

    Status : Checked

    """
    
    import matplotlib.pyplot as plt
    import numpy as np
    
    Legend = []
    plt.figure()
    
    # SS304
    import SS304
    Temperature = np.arange(5,293,0.1)
    YoungsModulus = [SS304.YoungsModulus(T) for T in Temperature]
    plt.plot(Temperature,YoungsModulus)
    Legend.append('SS 304')
    
    # Al5083O
    import Al5083O
    Temperature = np.arange(2,295,0.1)
    YoungsModulus = [Al5083O.YoungsModulus(T) for T in Temperature]
    plt.plot(Temperature,YoungsModulus)
    Legend.append('Al5083-O')

    # Al6061T6
    import Al6061T6
    Temperature = np.arange(2,295,0.1)
    YoungsModulus = [Al6061T6.YoungsModulus(T) for T in Temperature]
    plt.plot(Temperature,YoungsModulus)
    Legend.append('Al6061-T6')

    
    plt.xlabel('Temperature [K]')
    plt.ylabel(r'Youngs Modulus $[Pa]$')
    plt.grid()
    plt.legend(Legend)
    plt.title(r'The Youngs modulus of some materials from $cryopy$')
    
    



ThermalConductivity()
SpecificHeat()
LinearThermalExpansion()
YoungsModulus()


# from PC
def AU_PC(pc): return 206265*pc
def KM_PC(pc): return 3.086*(10**13)*pc
def LY_PC(pc): return 3.26*pc
# from LY
def AU_LY(ly): return (6.324*(10**4))*ly
def KM_LY(ly): return (9.46*(10**12))*ly
def PC_LY(ly): return 0.307*ly
# from AU
def PC_AU(au): return au/206265
def LY_AU(au): return au/(6.324*(10**4))
def KM_AU(au): return 1.498*(10**8)*au
def M_AU(au):  return M_KM(KM_AU(au))
# fromd KM
def PC_KM(km): return km/3.086*(10**13)
def LY_KM(km): return km/(9.46*(10**12))
def AU_KM(km): return km/(1.498*(10**8))
# from M
def KM_M(m): return m/1000
def AU_M(m): return AU_KM(KM_M(m))
# from KM
def M_KM(km): return km*1000

# from Sidereal Year
def Y_SY(sy): return 356.36*sy
def S_SY(sy): return (3.16*(10**7))*sy
# from year
def SY_Y(y): return y/356.36
# from sec
def SY_S(s): return s/(3.16*(10**7))
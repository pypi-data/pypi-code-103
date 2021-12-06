import math
import util, dimension, const, earth

class visViva: #Vis-Viva Equation
    def __init__(self):
        # print(sys._getframe().f_back.f_code.co_name)
        print("Vis-Viva Equation: v according to a m r")
    def set(self, str):
        strArray = str.split()
        if ( strArray.__len__()!=3 ): self.error(); self.ans=None; return 0
        a, m, r = float(strArray[0])*1.5*(10**11), float(strArray[1]), float(strArray[2])*1.5*(10**11)
        self.ans = math.sqrt(const.G*m*((2/r)-(1/a))*(10**(-6)))
    def get(self):
        return self.ans
    def error(self):
        # print(sys._getframe().f_back.f_code.co_name)
        print("Vis-Viva Error Occured!")

class meetingCycle: # meeting cycle calculation
    def __init__(self):
        # print(sys._getframe().f_back.f_code.co_name)
        print("meetingCycle: innerCycle outerCycle meetingCycle")
    def set(self, str):
        strArray = str.split()
        if ( strArray.__len__()!=3 or (not util.checkOnly(str,"_")) ): self.error(); self.ans=None; return 0
        innerT, outerT, meetT = strArray[0], strArray[1], strArray[2]
        if ( innerT=="_"  ): self.ans = 1/((1/float(outerT))+(1/float(meetT)))
        if ( outerT=="_"  ): self.ans = 1/((1/float(innerT))-(1/float(meetT)))
        if ( meetT =="_"  ): self.ans = 1/((1/float(innerT))+(1/float(outerT)))
    def get(self):
        return self.ans
    def error(self):
        # print(sys._getframe().f_back.f_code.co_name)
        print("Meeting Cycle Error Occured!")

class kepler3: # harmonic equation
    def __init__(self):
        # print(sys._getframe().f_back.f_code.co_name)
        print("Kepler3 = harminic equation: a r")
    def set(self, str):
        strArray = str.split()
        if ( strArray.__len__()!=2 or (not util.checkOnly(str,"_")) ): self.error(); self.ans=None; return 0
        a, T = strArray[0], strArray[1]
        if ( a=="_"  ): self.ans = float(T)**(2/3)
        if ( T=="_"  ): self.ans = float(a)**(3/2)
    def get(self):
        return self.ans
    def error(self):
        # print(sys._getframe().f_back.f_code.co_name)
        print("Meeting Cycle Error Occured!")
import math
import util

class pogson: #Pogson's equation
    def __init__(self):
        # print(sys._getframe().f_back.f_code.co_name)
        print("Pogson: M1-M2=-log(L1/L2)")
    def set(self, str):
        strArray = str.split()
        if ( strArray.__len__()!=4 or (not util.checkOnly(str,"_")) ): self.error(); self.ans=None; return 0
        M1, M2, L1, L3 = strArray[0], strArray[1], strArray[2], strArray[3]
        if ( M1=="_" ): M2, L1, L2 = float(strArray[1]), float(strArray[2]), float(strArray[3]); self.ans = M2-math.log10(L1/L2)
        if ( M2=="_" ): M1, L1, L2 = float(strArray[0]), float(strArray[2]), float(strArray[3]); self.ans = M1+math.log10(L1/L2)
        if ( L1=="_" ): M1, M2, L2 = float(strArray[0]), float(strArray[1]), float(strArray[3]); self.ans = L2*math.pow(10, M2-M1)
        if ( L2=="_" ): M1, M2, L1 = float(strArray[0]), float(strArray[1]), float(strArray[2]); self.ans = L1*math.pow(10, M1-M2)
    def get(self):
        return self.ans
    def error(self):
        # print(sys._getframe().f_back.f_code.co_name)
        print("Pogson Error Occured!")

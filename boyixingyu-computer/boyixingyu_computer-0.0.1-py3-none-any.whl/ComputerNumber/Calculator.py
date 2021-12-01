class ComputerNum:

    def __init__(self):
        self.a = 1
        self.b = 1

    def AddNum(self, a, b):
        return a+b

    def ReduceNum(self, a, b):
        return a-b

    def MultiNum(self, a, b):
        return a*b

    def DivideNum(self, a, b):
        return  a/b

    def PrintNum(self):
        print("a = " + str(self.a) + ",b = " + str(self.b))

if __name__=="__main__":
    obj = ComputerNum()
    obj.PrintNum()
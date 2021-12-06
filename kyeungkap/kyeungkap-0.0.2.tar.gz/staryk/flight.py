import tkinter

class hohmann:
    def __inti__(self):
        print("two Radius is needed")
        pass
    def set(self, a1, a2):
        self.a1 = a1
        self.a2 = a2
    def radius(self):
        self.a = (self.a1+self.a2)/2
        print("Hohmann Radius from radius "+str(self.a1)+" to radius "+str(self.a2)+" is "+str(self.a))
        return self.a
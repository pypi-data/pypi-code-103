from pydesy.gmath import *

def perpenToBaseline(s, basis, b):
    if basis < 0:
        raise Exception("The basis with cannot be negative or equal to zero")
    g = asin(s / basis * sin(b))
    x = s * cos(180 - (b + g))
    y = s * sin(180 - (b + g)) * cot(g)
    d = y * tan(g)
    
    return {"x" : x, "y" : y, "d" : d, "g" : g}
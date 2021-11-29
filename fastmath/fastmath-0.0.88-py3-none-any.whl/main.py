from .lib import *
from .trig import *
# importing complex math formulas
# basic formulas will be in the main.py file
import math
from .lib import *

def add(num1, num2):
    return num1 + num2 


def sub(num1, num2):
    return num1 - num2


def mul(num1, num2):
    return num1 * num2


def div(num1, num2):
    return num1 / num2




def fac(n):
	return 1 if (n==1 or n==0) else n * fac(n - 1);

def sqrt(num1):
    assert num1 >= 0, "Can't take the square root of negative numbers"
    def f(guess):
        if(guess == num1/guess):
            return guess
        else:
            return f((num1/guess + guess)/2)
    return f(1)

def pi():
    total = 4.0
    d = 3.0
    toAdd = False
    while 4/d > pow(10, -5):
        if(toAdd):
            total += 4 / d
        else:
            total -= 4 / d
        toAdd = not toAdd
        d += 2
    return total

def circle_area(radius):
    return math.pi * pow(radius, 2)

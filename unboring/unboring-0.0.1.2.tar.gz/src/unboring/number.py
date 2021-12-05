import random

#Multiplies 2 numbers
def multiply(one, two):
    return one * two

#Increments values
def increment(num, increment=1):
    num += increment
    return num

#Checks if bigger
def bigger(one, two):
    if one > two:
        return one
    else:
        return two

#Checks if smaller
def smaller(one, two):
    if one < two:
        return one
    else:
        return two

#Returns a random number 
def randomnum(one, two):
    return random.randint(one,two)
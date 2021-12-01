import random
import string

def randomString(lenght: int):
    return "".join(string.ascii_lowercase + string.ascii_uppercase, k = lenght)
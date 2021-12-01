import random
import string

def randomString(lenght: int):
    return "".join(random.choices(string.ascii_lowercase + string.ascii_uppercase + "0123456789", k = lenght))
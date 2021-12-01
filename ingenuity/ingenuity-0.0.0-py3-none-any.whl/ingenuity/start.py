import numpy as np
from collections import Counter

def mul() -> np.ndarray:
    x = np.random.rand(7,7)
    for i in range(0,7):
        x*np.random.rand(7,7)
    return x

def roll(count = 3) -> list:
    ret = []
    for i in range(0, count):
        ret.append(abs(np.linalg.det(mul())))

    return ret

def check(list) -> bool:
    l = len(list)
    for i in list:
        if i < 1/(2.236*l) or i > 2.236/l:
            return False
    return True

def generate(count = 3) -> list:
    while True:
        t = Probability(roll(count))
        if check(t) is True:
            break
    return t

def Probability(list) -> list:
    sum = np.sum(list)
    ret = [(i/sum) for i in list]

    return ret

def Output(probability=None) -> list:
    play = [0, 1, 2, 3, 4, 5]
    if probability is None:
        probability = generate(len(play))
    rr = []
    for i in range(0,10):
        rr.append(np.random.choice(play, p = probability))

    ret = Counter(rr).most_common(3)
    return ret
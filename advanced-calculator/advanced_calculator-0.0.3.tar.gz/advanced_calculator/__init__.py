from functools import lru_cache


@lru_cache()
def fibonacci(idx: int) -> int:
    """
    idx: which (int) index in the fibonacci sequence
    returns the idx-th fibonacci number, an integer
    e.g. idx = 1, 2, 3, 4 returns 1, 1, 2, 3, respectively.
    """
    if idx < 2:
        return idx
    return fibonacci(idx - 1) + fibonacci(idx - 2)


@lru_cache
def factorial(num: int) -> int:
    """
    num: which (int) number you would like the factorial of
    returns num!, an integer
    e.g. factorial(3) returns 3! = 3*2*1
    factorial(0) returns 0
    factorial of a negative returns 0
    """
    if num <= 0:
        return 0
    if num < 3:
        return num
    return num * factorial(num - 1)


def sqrt(num: float, decimal_places: int = 16) -> int:
    """
    num: the (float) number to take the square root of
    returns the square root of num, a float
    """
    guess = num
    epsilon = 10 ** (-1 * decimal_places)
    while guess * guess > num + epsilon:
        guess = (guess + (num / guess)) / 2
    return guess

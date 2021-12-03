import numpy as np

def is_prime(n: int) -> bool:
    """
    Check if a given integer is prime. Returns boolean
    Arguments:
    n: int - The number to check
    """
    if n < 1:
        raise ValueError(f"""The argument to is_prime must be a positive
                integer. You supplied {n}.""")
    elif n == 1:
        return False
    elif n == 2:
        return True

    for i in range(2, int(np.ceil(np.sqrt(n))) + 1):
            if n % i == 0:
                return False
    return True

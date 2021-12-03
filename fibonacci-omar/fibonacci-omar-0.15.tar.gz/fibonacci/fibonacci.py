def generate_fibonacci_list(size):
    result = []
    while len(result) < size:
        if len(result) == 0:
            result.append(0)
        elif len(result) == 1:
            result.append(1)
        else:
            result.append(result[-1] + result[-2])
    return result


def generate_fibonacci_list_with_upperbound(upper):
    result = []
    if upper == 0:
        result.append(0)
    elif upper >= 1:
        result.extend([0, 1])
        while result[-1] < upper:
            result.append(result[-1] + result[-2])
    return result


def get_next_fibonacci(start):
    result = generate_fibonacci_list_with_upperbound(start)
    return result[-1] + result[-2]

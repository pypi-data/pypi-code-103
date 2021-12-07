def clamp(x, lower=0.0, upper=1.0):
    if x < lower:
        return lower
    elif x > upper:
        return upper
    else:
        return x


def normalize(x, lower=0.0, upper=1.0):
    return (x - lower) / (upper - lower)
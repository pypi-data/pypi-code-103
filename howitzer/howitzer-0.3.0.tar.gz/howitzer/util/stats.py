import math

def average(_list):
    return sum(_list)/(len(_list))

def stddev(_list):
    avg = average(_list)
    total = 0
    for l in _list:
        total += (l-avg)**2
    
    avg_sqred_diff = total/len(_list)

    return math.sqrt(avg_sqred_diff)

def zscore(_observered, _mean, _standard_deviation):
    return (_observered-_mean)/_standard_deviation

def corolation(x, y):
    x_hat = average(x)
    y_hat = average(y)

    x_sd = stddev(x)
    y_sd = stddev(y)

    zxzy = []
    for i in range(len(x)):
        zxzy.append(zscore(x[i], x_hat, x_sd) * zscore(y[i], y_hat, y_sd))
    
    return average(zxzy)



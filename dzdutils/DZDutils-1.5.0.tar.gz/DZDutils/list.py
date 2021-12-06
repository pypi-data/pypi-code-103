import numpy, math
from typing import List


def chunks(lst: List, n: int):
    """Yield successive n-sized chunks from lst."""
    # https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def divide(lst: List, n: int):
    """divide a list into n buckets"""
    # https://stackoverflow.com/a/2135920/12438690
    k, m = divmod(len(lst), n)
    return (lst[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n))


def _cust_range(*args, rtol=1e-05, atol=1e-08, include=[True, False]):
    # https://stackoverflow.com/questions/50299172/python-range-or-numpy-arange-with-end-limit-include
    """
    Combines numpy.arange and numpy.isclose to mimic
    open, half-open and closed intervals.
    Avoids also floating point rounding errors as with
    >>> numpy.arange(1, 1.3, 0.1)
    array([1. , 1.1, 1.2, 1.3])

    args: [start, ]stop, [step, ]
        as in numpy.arange
    rtol, atol: floats
        floating point tolerance as in numpy.isclose
    include: boolean list-like, length 2
        if start and end point are included
    """
    # process arguments
    if len(args) == 1:
        start = 0
        stop = args[0]
        step = 1
    elif len(args) == 2:
        start, stop = args
        step = 1
    else:
        assert len(args) == 3
        start, stop, step = tuple(args)

    # determine number of segments
    n = (stop - start) / step + 1

    # do rounding for n
    if numpy.isclose(n, numpy.round(n), rtol=rtol, atol=atol):
        n = numpy.round(n)

    # correct for start/end is exluded
    if not include[0]:
        n -= 1
        start += step
    if not include[1]:
        n -= 1
        stop -= step

    return numpy.linspace(start, stop, int(n))


def crange(*args, **kwargs):
    return _cust_range(*args, **kwargs, include=[True, True])


def orange(*args, **kwargs):
    return _cust_range(*args, **kwargs, include=[True, False])


def trend(data: List[int]) -> float:
    """Return the trend of a number list in degree.
    0 = no trend
    postive number (max 90) = numbers go upwarts
    negative number (min -90) = numbers trending downwards

    Args:
        data (list of int): e.g. [1,34,564,1,23]

    Returns:
        int: trend as a degree number between -90 to 90
    """
    if len(data) > 1:
        # generate x-axis data based on the max value to get relative trends compared to the amount of data

        x_axis = list(numpy.arange(0, max(data), max(data) / len(data)))
        # dirty fix to avoid rounding errors
        # TODO: try to use orange from above
        if len(x_axis) > len(data):
            data.insert(data[0], 0)
        elif len(x_axis) < len(data):
            data.pop(0)
        coeffs = numpy.polynomial.polynomial.Polynomial.fit(
            x_axis,
            list(data),
            1,
        )
        coeffs_convert = coeffs.convert().coef
        try:
            slope = list(coeffs_convert)[1]
        except:
            slope = 0
        angle_rad = math.atan(slope)
        angle_deg = math.degrees(angle_rad)
        return round(float(angle_deg), 2)
    else:
        return 0

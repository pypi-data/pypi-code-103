from autodiff.dualnumber import Dualnumber
import numpy as np
from typing import Union


def sin(x: Union[float, Dualnumber]) -> Dualnumber:
    """
    Implements the sin elementary operation, with dualnumber support.
    
    :param x: Performs sin operation on float or dualnumber.
    """
    try:
        return Dualnumber(np.sin(x.val), der=np.cos(x.val) * x.der)
    except AttributeError as e:
        sin_x = Dualnumber(np.sin(x))
        sin_x.set_dual(0)
        return sin_x


def cos(x: Union[float, Dualnumber]) -> Dualnumber:
    """
    Implements the cos elementary operation, with dualnumber support.

    :param x: Performs cos operation on float or dualnumber.
    """
    try:
        cos_x = Dualnumber(np.cos(x.val))
        cos_x.set_dual(-np.sin(x.val) * x.der)
        return cos_x
    except AttributeError as e:
        cos_x = Dualnumber(np.cos(x))
        cos_x.set_dual(0)
        return cos_x


def tan(x: Union[float, Dualnumber]) -> Dualnumber:
    """
    Implements the tan elementary operation, with dualnumber support.

    :param x: Performs cos operation on float or dualnumber.
    """
    tan_x = sin(x) / cos(x)
    return tan_x


def exp(x: Union[float, Dualnumber]) -> Dualnumber:
    """
    Implements the exp elementary operation, with dualnumber support.

    :param x: Performs exp operation on float or dualnumber.
    """
    # this is specifically euler's number?
    # try:
    #     exp_x = Dualnumber(np.exp(x.val))
    #     exp_x.set_dual((x.val - 1) * np.exp(x.val) * x.der)
    #     return exp_x
    # except AttributeError as e:
    #     exp_x = Dualnumber(np.exp(x))
    #     exp_x.set_dual(0)
    #     return exp_x
    try:
        x.der
        return np.exp(1) ** x
    except AttributeError as e:
        return Dualnumber(np.exp(1) ** x, der=0)


def log(x: Union[float, Dualnumber]) -> Dualnumber:
    """
    Implements the log elementary operation, with dualnumber support.

    :param x: Performs log operation on float or dualnumber.
    """
    try:
        log_x = Dualnumber(np.log(x.val), der=(1 / x.val) * x.der)
        return log_x
    except AttributeError as e:
        log_x = Dualnumber(np.log(x),der=0)
        return log_x


if __name__ == '__main__':
    # sin test passing in a float
    x = np.pi
    sin_x = sin(x)
    assert np.isclose(sin_x.val, 0)
    assert sin_x.der == 0

    # sin test passing in a dualnumber
    x = Dualnumber(np.pi)
    x.set_dual(np.pi / 2)
    sin_x = sin(x)
    assert np.isclose(sin_x.val, 0)
    assert sin_x.der == - np.pi / 2

    # cos test passing in a float
    x = np.pi
    cos_x = cos(x)
    assert np.isclose(cos_x.val, -1)
    assert cos_x.der == 0

    # cos test passing in a dualnumber
    x = Dualnumber(np.pi)
    x.set_dual(np.pi / 2)
    cos_x = cos(x)
    assert np.isclose(cos_x.val, -1)
    assert np.isclose(cos_x.der, 0)

    # tan test passing in a float
    x = np.pi / 4
    tan_x = tan(x)
    assert np.isclose(tan_x.val, 1)
    assert tan_x.der == 0

    # tan test passing in a dualnumber
    x = Dualnumber(np.pi / 4)
    x.set_dual(np.pi)
    tan_x = tan(x)
    assert np.isclose(tan_x.val, 1)
    assert np.isclose(tan_x.der, 2 * np.pi)

    # exp test passing in a float
    x = 2
    exp_x = exp(x)
    assert np.isclose(np.exp(2), exp_x.val)
    assert exp_x.der == 0

    # exp test passing in a dualnumber
    x = Dualnumber(2)
    x.set_dual(1)
    exp_x = exp(x)
    assert np.isclose(np.exp(2), exp_x.val)
    assert np.isclose(np.exp(2), exp_x.der)

    # log test  for float
    x = np.exp(1)
    log_x = log(x)
    assert np.isclose(1, log_x.val)
    assert np.isclose(0, log_x.der)

    # log test for Dual number
    x = Dualnumber(np.exp(1), 2)
    log_x = log(x)
    assert np.isclose(1, log_x.val)
    assert np.isclose(np.exp(-1)*2, log_x.der)

    # complex function 1
    x = Dualnumber(2, der = 1)
    f = sin(x**2+x) - log(x)
    assert np.isclose(-0.9725626, f.val)
    assert np.isclose(4.300851433251, f.der)

    # complex function 2
    x = Dualnumber(np.pi, der = 1)
    f = (tan(x)) - 2**x * exp(x)
    assert np.isclose(-204.2160993, f.val)
    assert np.isclose(-344.76791290283, f.der)

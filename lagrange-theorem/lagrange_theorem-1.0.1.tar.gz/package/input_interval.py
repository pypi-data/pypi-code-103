"""
Module sets the interval of numbers
"""


def set_interval() -> tuple:
    left_border_default, right_border_default = 1, 11
    left_border, right_border = None, None
    try:
        interval = list(map(int, input().split()))
    except ValueError:
        print('Input wrong value!')
        return left_border, right_border

    if len(interval) == 1:
        left_border = 0
        right_border = interval[0]
    elif len(interval) > 2:
        print('Input many values!')
        return left_border, right_border
    elif interval[0] < 0 or interval[1] < 0:
        print('Input values cannot be negative')
        return left_border, right_border
    elif len(interval) == 0:
        left_border = left_border_default
        right_border = right_border_default
    elif interval[0] >= interval[1]:
        print('The second number cannot be less than the first!')
        return left_border, right_border
    elif len(interval) == 2:
        left_border = interval[0]
        right_border = interval[1]

    return left_border, right_border

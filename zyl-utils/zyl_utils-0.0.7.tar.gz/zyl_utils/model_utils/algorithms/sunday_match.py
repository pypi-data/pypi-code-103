# encoding: utf-8
"""
@author: zyl
@file: sundat_match.py
@time: 2021/11/29 9:33
@desc:
"""

def sunday_match(target, pattern):
    """

    Args:
        target:
        pattern:

    Returns:

    """
    len_target = len(target)
    len_pattern = len(pattern)

    if len_pattern > len_target:
        return list()

    index = 0
    starts = []
    while index < len_target:
        if pattern == target[index:index + len_pattern]:
            starts.append(index)
            index += 1
        else:
            if (index+len(pattern)) >= len_target:
                return starts
            else:
                if target[index + len(pattern)] not in pattern:
                    index += (len_pattern + 1)
                else:
                    index += 1
    return starts

if __name__ == '__main__':
    t = "this is an apple , apple app app is app not app"
    t = t.split()
    p = "app not"
    p = p.split()
    print(t)
    print(p)
    print(sunday_match(target=t, pattern=p))

# -*- coding: utf-8 -*-


def index_to_column_letter(index):
    num = index
    sequence = list(map(lambda x: chr(x), range(ord('A'), ord('Z') + 1)))
    L = []
    if num > 25:
        while True:
            d = int(num / 26)
            remainder = num % 26
            if d <= 25:
                L.insert(0, sequence[remainder])
                L.insert(0, sequence[d - 1])
                break
            else:
                L.insert(0, sequence[remainder])
                num = d - 1
    else:
        L.append(sequence[num])
    return ''.join(L)
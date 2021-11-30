# -*- coding: utf-8 -*-

import datetime
import math
import random


def get_random_chars(char_length):
    """
    获取随机数 [a-f & 0-9]
    :param char_length:
    :return:
    """
    chars = 'abcdef0123456789'
    i = 0
    res = ''
    while i < char_length:
        idx = math.floor(1 + random.random() * 16)
        res += chars[idx - 1:idx]
        i += 1
    return res


def seq_id():
    """
    获取有序GUID与 db中fn_newSeqId 算法保持一致
    :return str: xxxxxxxx_xxxx_xxxx_xxxx_xxxxxxxxxxxx
    """
    now = datetime.datetime.utcnow().timestamp()
    ticks = hex(round(now * 1000000))[2:]
    old_ticks = hex(round(now * 1000 + 62135625600000))[2:]
    return '%s-%s-%s%s-%s-%s' % (
        old_ticks[:8], old_ticks[8:12], ticks[10:13], get_random_chars(1), get_random_chars(4), get_random_chars(12))

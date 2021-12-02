# encoding: utf-8
"""
@author: zyl
@file: data_processing.py
@time: 2021/11/25 14:15
@desc:
"""

import re


class DTProcesser:
    def __init__(self):
        pass

    @staticmethod
    def cut_train_eval(all_df,max_sample_num=2000):
        from sklearn.utils import resample
        raw_df = resample(all_df, replace=False)
        cut_point = min(max_sample_num, int(0.2 * len(raw_df)))
        eval_df = raw_df[0:cut_point]
        train_df = raw_df[cut_point:]
        return train_df, eval_df

    @staticmethod
    def remove_illegal_chars(text):
        ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
        return ILLEGAL_CHARACTERS_RE.sub(r'', str(text))  # 非法字符

    @staticmethod
    def _remove_invisible_chars(s, including_char=('\t', '\n', '\r')):
        """移除所有不可见字符，除'\t', '\n', '\r'外"""
        str = ''
        for x in s:
            if (x not in including_char) and (not x.isprintable()):
                str += ' '
            else:
                str += x
        return str

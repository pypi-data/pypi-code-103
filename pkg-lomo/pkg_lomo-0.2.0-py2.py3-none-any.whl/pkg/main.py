# -*- coding: utf-8 -*-

# @File  : main.py
# @Author: Lomo
# @Site  : lomo.space
# @Date  : 2021-11-20
# @Desc  : main

import itertools


class CartesianProduct(object):
    def __init__(self, case_list, value_list):
        self.items = case_list
        self.values = value_list

    def generate_cases(self):
        if self.items and self.values:
            n = 0
            for i in itertools.product(self.items, self.values):
                print(' 输入 '.join(i))
                n += 1
            print("共生成 {0} 组结果".format(n))
        else:
            return None


# single function
def get_sum(m, n):
    if isinstance(m, int) and isinstance(n, int):
        return m + n
    else:
        print("m: {0}, n: {1} is not int number...".format(m, n))
        return None


if __name__ == '__main__':
    # items = ['用户名', '密码']
    items = ['我', '你', '他', '她', '它']
    # values = ['正确', '不正确', '特殊符号', '超过最大长度']
    values = ['1', '2', '5', '11', '100']
    cd = CartesianProduct(items, values)
    cd.generate_cases()

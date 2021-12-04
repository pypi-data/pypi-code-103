"""
 * @file   : CollectionHelper.py
 * @time   : 12:40
 * @date   : 2021/12/4
 * @mail   : 9727005@qq.com
 * @creator: ShanDong Xiedali
 * @company: HiLand & RainyTop
"""


class CollectionHelper:
    """
    对集合类型的常用方法进行整合
    """

    @staticmethod
    def sort(iterable, key=None, reverse=False):
        """
        调用系统的sorted方法对可以迭代对象进行排序
        :param iterable:
        :param key:
        :param reverse:
        :return:
        """
        return sorted(iterable, key, reverse)


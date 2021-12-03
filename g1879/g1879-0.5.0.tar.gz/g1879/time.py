# -*- coding:utf-8 -*-
from time import perf_counter


class Timer(object):
    """用于记录时间间隔的工具"""

    def __init__(self, pin: bool = True, show_everytime: bool = False) -> None:
        """初始化                                       \n
        :param pin: 初始化时是否记录一个时间点
        :param show_everytime: 是否每次记录时打印时间差
        """
        self.times = []
        self.show_everytime = show_everytime
        if pin:
            self.pin('起始点', show_everytime)

    def pin(self, text: str = '', show: bool = False) -> None:
        """记录一个时间点                             \n
        :param show: 是否打印与上一个时间点的差
        :param text: 记录点说明文本
        :return: None
        """
        self.times.append((perf_counter(), text))
        if self.show_everytime or show:
            len_times = len(self.times)
            text = f'{text}：' if text else ''
            print(f'{text}{self.times[-1][0] - self.times[len_times - 2][0]}')

    def show(self, pin: bool = True, text: str = '') -> None:
        """打印所有时间差                           \n
        :param pin: 打印前是否记录记录一个时间点
        :param text: 记录时间点的文本
        :return: None
        """
        if pin:
            self.pin(text, False)

        for k in range(1, len(self.times)):
            txt = self.times[k][1] or f't{k - 1}->t{k}'
            print(f'{txt}: {self.times[k][0] - self.times[k - 1][0]}')

    def clear(self) -> None:
        """清空已保存的时间点"""
        self.times = []

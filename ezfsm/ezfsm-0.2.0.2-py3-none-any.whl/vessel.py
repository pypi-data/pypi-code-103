class Vessel(object):
    def __init__(self, *args):
        self.__min, self.__current, self.__max = 0, 100, 100
        self.__delta_cb, self.__full_cb, self.__empty_cb = None, None, None
        _len = len(args)
        if _len == 1:  # max
            self.RawSetValues(0, args[0], args[0])
        elif _len == 2:  # min max
            self.RawSetValues(args[0], args[1], args[1])
        elif _len == 3:  # min, current, max
            self.RawSetValues(*args)

    def RawSetValues(self, min, current, max):
        """
        不会触发回调函数, 不会触发检测
        :param min: double
        :param current: double
        :param max: double
        :return:
        """
        self.__min, self.__current, self.__max = min, current, max

    def SetWhenEmpty(self, empty_func: callable):
        """
        当容器为空时执行的操作
        :param empty_func: 形参: empty_func(vessel), None表示不作任何操作
        :return:
        """
        self.__empty_cb = empty_func

    def SetWhenFull(self, full_func: callable):
        """
        当容器为满时执行的操作
        :param full_func: 形参: full_func(vessel), None表示不作任何操作
        :return:
        """
        self.__full_cb = full_func

    def SetWhenDelta(self, delta_func: callable):
        """
        当容器余量改变时执行的操作
        :param delta_func: 形参: delta_func(vessel, delta:int|float), None表示不作任何操作
        :return:
        """
        self.__delta_cb = delta_func

    def DoDelta(self, delta):
        """
        更新current的值，并依据最后情况调用回调函数
        :param delta: 变化值
        :return:
        """
        last = self.__current
        self.__current += delta
        if self.__max < self.__current:
            self.__current = self.__max
        if self.__current < self.__min:
            self.__current = self.__min

        if self.__delta_cb:
            delta = self.__current - last
            if abs(delta) > 1e-8:
                self.__delta_cb(self, delta)
        if self.__full_cb and self.__max == self.__current:
            self.__full_cb(self)
        if self.__empty_cb and self.__min == self.__current:
            self.__empty_cb(self)

    def Max(self, max = None):
        """
        修改或获取max
        :param max:
        :return:
        """
        if max is not None:
            self.__max = max
            if self.__max < self.__min:
                self.__min = self.__max
            if self.__current > self.__max:
                DoDelta(self.__max - self.__current)
        else:
            return self.__max

    def Min(self, min = None):
        """
        修改或获取min
        :param min:
        :return:
        """
        if min is not None:
            self.__min = min
            if self.__max < self.__min:
                self.__max = self.__min
            if self.__current < self.__min:
                DoDelta(self.__min - self.__current)
        else:
            return self.__min

    def Now(self, now = None):
        """
        修改或获取current
        :param now:
        :return:
        """
        if now is not None:
            DoDelta(now - self.__current)
        else:
            return self.__current

    def Percent(self, per = None):
        """
        修改或获取percent
        :param per:
        :return:
        """
        if per is not None:
            self.DoDelta(self.__min + (self.__max - self.__min) * per - self.__current)
        else:
            return (self.__current - self.__min) / (self.__max - self.__min)

    def IsEmpty(self):
        return self.__min >= self.__current  # 一般情况下min不会小于current， 但是不排除用户使用RawSet的情况

    def IsFull(self):
        return self.__max <= self.__current

    def Full(self):
        self.DoDelta(self.__max - self.__current)

    def Empty(self):
        self.DoDelta(self.__min - self.__current)

    def __add__(self, other):
        return self.__current + other

    def __iadd__(self, other):
        self.DoDelta(other)

    def __sub__(self, other):
        return self.__current - other

    def __isub__(self, other):
        self.DoDelta(-other)

    def __int__(self):
        return int(self.__current)

    def __float__(self):
        return float(self.__current)

    def __str__(self):
        return """Vessel{
            .min: {}
            .current: {}
            .max: {}
            percent: {}
        }
        """.foramt(self.__min, self.__current, self.__max, self.Percent())

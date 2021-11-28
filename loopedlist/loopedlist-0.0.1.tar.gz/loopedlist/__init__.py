class looplist(list):
    """
    looplist[x] == list[x % len(list)]
    Making mutable sequence with finite item quantity and infinite possible item number.
    Equivalent to list sequence.

    If no argument is given, the constructor creates a new empty list.
    The argument must be an iterable if specified.
    """
    def __init__(self, value, length=0):
        super(looplist, self).__init__()
        self.t = list(value)
        self.length = length
        self += self.t
        self.length += len(self.t)

    def __getitem__(self, item):
        if self.length > 0:
            item %= self.length
        else:
            item = 0
        return self.t[item]


    def __setitem__(self, key, value):
        if self.length > 0:
            key %= self.length
        else:
            key = 0
        self[key] = value

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __len__(self):
        return self.length

    def append(self, value, *args, **kwargs):
        super(looplist, self).append(value)
        self.t.append(value)
        self.length += 1


class looptuple(tuple):
    """
    looptuple[x] == list[x % len(list)]
    Making immutable sequence with finite item quantity and infinite possible item number.
    Equivalent to tuple sequence.

    If no argument is given, the constructor creates a new empty list.
    The argument must be an iterable if specified.
    """
    def __init__(self, value, length=0):
        super(looptuple, self).__init__()
        self.t = tuple(value)
        self.length = length
        self += self.t
        # self.length += len(self.t)

    def __getitem__(self, item):
        if len(self) > 0:
            item %= len(self)
        else:
            item = 0
        return self.t[item]

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]


__name__ = 'loopedlist'

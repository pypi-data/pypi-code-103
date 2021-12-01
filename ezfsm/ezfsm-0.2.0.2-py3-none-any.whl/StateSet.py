class UnsupportedStateSet(Exception):
    def __init__(self, ss):
        super(UnsupportedStateSet, self).__init__("\n\n[Error]:State sets with type<%s> is not a valid State-Set." % str(type(ss)))


class StateSet(object):  # 状态集
    inst = None

    def __init__(self, names=()):
        self.sets = list(names)
        self.state = None

    def Enable(self, inst):
        self.inst = inst

    def Add(self, name, ignore=False):
        if name in self.sets:
            if ignore: return
            raise Exception("[Error]: 重复的状态<{}>.".format(name))
        self.sets += [name]

    def Remove(self, name, ignore=False):
        if name not in self.sets:
            if ignore: return
            raise Exception("[Error]: 待删除的状态<{}>不存在.".format(name))
        self.sets.remove(name)

    def __iter__(self):
        return iter(self.sets)

    def __len__(self):
        return len(self.sets)

    def __getattr__(self, item):
        return getattr(self.sets, item)

    def __getitem__(self, item):
        return self.sets[item]

    def __setitem__(self, key, value):
        self.sets[key] = value

    Del = Remove
    add = Add
    remove = Remove

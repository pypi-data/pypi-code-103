
class DataArea(object):
    def iadd(self, attr, value):
        new = getattr(self, attr) + value
        setattr(self, attr, new)
        return new

    def isub(self, attr, value):
        new = getattr(self, attr) - value
        setattr(self, attr, new)
        return new

    def set(self, attr, value):
        setattr(self, attr, value)



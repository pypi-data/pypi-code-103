# This file is placed in the Public Domain.


from .obj import Object


class BusError(Exception):

    pass


class Bus(Object):

    def __init__(self):
        super().__init__()
        self.objs = []

    def __iter__(self):
        return iter(self.objs)

    def add(self, obj):
        self.objs.append(obj)

    def announce(self, txt):
        for h in self.objs:
            if "announce" in dir(h):
                h.announce(txt)

    def byorig(self, orig):
        for o in self:
            if repr(o) == orig:
                return o
        raise BusError(orig)

    def byfd(self, fd):
        for o in self:
            if o.fd and o.fd == fd:
                return o
        return None

    def bytype(self, typ):
        for o in self:
            if isinstance(o, typ):
                return o
        return None

    def first(self, otype=None):
        if self.objs:
            if not otype:
                return self.objs[0]
            for o in self:
                if otype in str(type(o)):
                    return o
        return None

    def resume(self):
        for o in self:
            o.resume()

    def say(self, orig, channel, txt):
        for o in self:
            if repr(o) == orig:
                o.say(channel, txt)

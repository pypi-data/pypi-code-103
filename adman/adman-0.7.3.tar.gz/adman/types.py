from .util import int_from_bytes

class SID:
    revision = 1

    def __init__(self, idauth, *subauths):
        # Identifier-Authority
        self.idauth = idauth

        # Subauthority values
        self.subauths = list(subauths)


    @property
    def rid(self):
        return self.subauths[-1]

    @rid.setter
    def rid(self, value):
        self.subauths[-1] = value


    def __str__(self):
        components = ["S", self.revision, self.idauth] + self.subauths
        return "-".join(str(c) for c in components)


    @classmethod
    def from_bytes(cls, sid):
        # Inspired by https://gist.github.com/miromannino/04be6a64ea0b5f4d4254bb321e09d628
        revision = sid[0]
        if revision != cls.revision:
            raise ValueError("SID revision must be {}".format(cls.revision))

        subauth_count = sid[1]

        idauth = int_from_bytes(sid, 2, 6, 'big')

        subauths = []
        for i in range(subauth_count):
            off = 8 + 4*i
            sa = int_from_bytes(sid, off, 4, 'little')
            subauths.append(sa)

        return cls(idauth, *subauths)


    def to_bytes(self):
        result = bytes([self.revision, len(self.subauths)])
        result += self.idauth.to_bytes(6, 'big')
        for sa in self.subauths:
            result += sa.to_bytes(4, 'little')
        return result


    @classmethod
    def from_str(cls, s):
        parts = s.split('-')

        if parts[0] != 'S':
            raise ValueError("SID must start with 'S-'")

        revision = int(parts[1])
        if revision != cls.revision:
            raise ValueError("SID revision must be {}".format(cls.revision))

        idauth = int(parts[2])
        subauths = [int(p) for p in parts[3:]]

        return cls(idauth, *subauths)

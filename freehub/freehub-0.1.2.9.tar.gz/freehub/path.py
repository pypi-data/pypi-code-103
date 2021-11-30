
class NoValue:
    pass
class Path(str):
    __no_value__ = '<__no_value__>'

    def __init__(self, *args, **kwargs):
        super().__init__()

    def __getattr__(self, item):
        return self / item

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __truediv__(self, other):
        return Path(self + '/' + other)

    def __call__(self, s=NoValue):
        if s is NoValue: return None
        return self / s

    def relative_path(self, path):
        assert path.startswith(self)
        if self == '':
            pass
        else:
            if path.startswith(self):
                path = path[len(self):]
            path = path.lstrip('/')
        return self.__class__(path)

class StrictPath:
    def __init__(self, s):
        self.__value__ = Path(self.__strict__(s))

    def __strict__(self, s):
        prefix = '/' if s.startswith('/') or s.startswith("\\") else ''

        def remove_all(lis, item):
            if item in lis:
                lis2 = lis.copy()
                for i in lis:
                    if i == item:
                        lis2.remove(i)
                return lis2

            else:
                return lis

        lis = s.split('/')
        lis2 = []
        for i in lis:
            lis2 += i.split('\\')
        lis = lis2
        lis = remove_all(lis, '/')
        lis = remove_all(lis, "\\")
        lis = remove_all(lis, '')
        return prefix + '/'.join(lis)

    def __getattr__(self, item):
        return self / item

    def __truediv__(self, other):
        return StrictPath(self.__value__ / other).__value__

    def __call__(self, s=''):
        if s == '': return self.__value__
        return StrictPath(self.__value__ / s)

    def __repr__(self):
        return "<StrictPath:'%s'>" % (self.__value__)

    def __str__(self):
        return self.__value__


def join_path(*args):
    path = StrictPath('/'.join(args))()
    path = standard_path(path)
    return path


def standard_path(p, check=False):
    assert len(p)
    # if (len(p)<=4 and p[1:]=='://') or (len(p)==3 and p[1:]==':/'):return p[:3]
    # print(p)
    p = str(StrictPath(p))
    # print(p)
    # if not '/' in p:return p
    p = p.split('/')
    assert len(p)
    res = []
    p.reverse()
    while True:
        if not len(p):
            if len(res) > 1 and '.' in res:
                for char in res:
                    if char == '.':
                        res.remove(char)
            path = '/'.join(res)
            if len(path) == 2 and path[1] == ':':
                path = path + '/'
            return path
        i = p.pop()
        if i == '':
            res.append('')
            continue
        elif i == '.':
            if not len(res): res.append('.')
        elif i == '..':
            if check: return False
            if not len(res) or res[-1] == '.':
                raise Exception('Error,path has reached the top when another ".." shew up.')
            else:
                res.pop()
                if not len(res): res.append('.')
        else:
            res.append(i)

def get_relative_path(root, child):
    path = child
    path = standard_path(path)
    root = standard_path(root)
    assert path.startswith(root)
    return path[len(root):]
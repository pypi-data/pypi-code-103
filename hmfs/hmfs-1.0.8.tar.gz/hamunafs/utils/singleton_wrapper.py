class Singleton(object):
    _instance_ = {}
    def __new__(cls, *args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cls._instance_:
            cls._instance_[key] = super().__new__(cls)
        return cls._instance_[key]

    def __init__(self, *args, **kwargs):
        pass
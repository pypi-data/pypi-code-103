class Sanka:

    def __init__(self, func):
        self.func = func
        self.call_count = 0

    def __call__(self, *args, **kwargs):
        # TODO (withtwoemms) -- match type instead of string
        if Sanka.YaDead in args:
            return self.call_count
        self.call_count += 1
        return self.func(*args, **kwargs)

    class YaDead:
        pass


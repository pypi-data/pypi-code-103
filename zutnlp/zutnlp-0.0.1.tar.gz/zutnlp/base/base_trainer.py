class BaseTrainer(object):
    def __init__(self):
        pass

    def train(self, *args, **kwargs):
        raise NotImplementedError

    def valid(self, *args, **kwargs):
        raise NotImplementedError

    def test(self, *args, **kwargs):
        raise NotImplementedError

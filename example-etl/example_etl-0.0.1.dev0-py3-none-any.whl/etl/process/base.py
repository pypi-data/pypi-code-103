class BaseProcess:
    """"""

    def __init__(self, settings):
        self.settings = settings

    def process(self, data: str) -> str:
        raise NotImplementedError()

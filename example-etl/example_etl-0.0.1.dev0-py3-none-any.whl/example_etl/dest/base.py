class BaseDest:
    def __init__(self, settings):
        self.settings = settings
        self.setup()

    def setup(self):
        """"""

    def write(self, data: str):
        raise NotImplementedError()

    def close(self):
        """"""

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __enter__(self):
        return self

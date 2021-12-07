from typing import Iterable


class BaseSource:

    def __init__(self, settings):
        self.settings = settings
        self.setup()

    def setup(self):
        """"""

    def read(self) -> Iterable[str]:
        raise NotImplementedError()

    def close(self):
        """"""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

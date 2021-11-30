from os.path import expanduser


class Tools:
    @classmethod
    def extend_path(cls, path: str):
        return expanduser(path)

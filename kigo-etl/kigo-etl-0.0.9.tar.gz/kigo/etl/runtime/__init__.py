__all__ = []


def init():
    __import__("kigo.etl.extractors.slicers", globals(), locals())
    __import__("kigo.etl.file.readers", globals(), locals())
    __import__("kigo.etl.mapper", globals(), locals())


init()

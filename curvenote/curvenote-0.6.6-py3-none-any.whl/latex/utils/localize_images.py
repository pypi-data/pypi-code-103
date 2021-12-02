from collections import namedtuple

# TODO these should be somewhere else and an enums or pydantic models?
ImageFormats = {"image/png": "png", "image/jpeg": "jpg", "image/gif": "gif"}
ImageSummary = namedtuple("ImageSummary", ["content", "remote_paths", "local_paths"])

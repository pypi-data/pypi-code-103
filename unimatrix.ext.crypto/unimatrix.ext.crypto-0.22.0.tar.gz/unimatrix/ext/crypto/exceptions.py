"""Declares common exceptions."""


class UnsupportedBackend(LookupError):
    pass


class MissingDependencies(ImportError):
    pass

# coding=utf-8


class Command:
    TAB_LENGTH = '<15'

    @classmethod
    def description(cls):
        return ''

    @classmethod
    def name(cls):
        return ''

    @classmethod
    def class_name(cls):
        return cls.__name__

    @classmethod
    def long_description(cls):
        return f'{cls.name():{Command.TAB_LENGTH}}{cls.description()}'


class CommandOption:

    def __init__(self, options):
        self._options = options

    def __getattr__(self, name):
        cls = type(self)
        if name in self._options:
            return self._options[name]
        else:
            raise AttributeError(
                f'{cls.__name__!r} object has no attribute {name!r}')

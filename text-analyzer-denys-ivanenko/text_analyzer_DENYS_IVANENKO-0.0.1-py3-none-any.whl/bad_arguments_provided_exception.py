from text_analyzer.constants import BAD_ARGUMENTS


class BadArgumentsProvidedException(Exception):
    def __init__(self, message):
        message = ' '.join([BAD_ARGUMENTS, message])
        super().__init__(message)

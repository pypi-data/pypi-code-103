from unconcealment.secret_pattern import SecretPattern


class Result:
    """ Convert object to json """
    file: str
    pattern: str
    value: str

    def __init__(self, file: str, pattern: SecretPattern, value: str):
        self.file = file
        self.pattern = str(pattern).replace('SecretPattern.', '')
        self.value = value

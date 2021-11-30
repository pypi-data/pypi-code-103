class TokenRequestFailed(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f'Google get token load failed ...{self.value}'


class NotFoundIDToken(Exception):

    def __str__(self):
        return 'Not Found Google ID Token ...'

from enum import IntEnum

class UserLevel(IntEnum):
    '''Authorization level of a user.
    '''

    NO_LOGIN = 0
    USER = 1
    ADMIN = 2
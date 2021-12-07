from enum import Enum


class Operations(Enum):
    """
    This enum is the distribute all possible operations globally in this app.
    """
    REGISTER = "register"
    LOGIN = "login"
    LOGOUT = "logout"

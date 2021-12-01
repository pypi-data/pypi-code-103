from Configs import ConfigBase

# define different classes per environment


class DEFAULT(ConfigBase):
    # Always create a DEFAULT class and use it as the base class for other environments classes

    # DEFAULT must have all config variables / class attributes that are used in the other classes
    MY_CONFIG_VALUE = 1
    MY_OVERRIDE_VALUE = "DEFAULT"
    MY_JSON = None
    MY_JSON2 = None
    JSON = None


class DEV(DEFAULT):
    MY_CONFIG_VALUE = 2


class PROD(DEFAULT):
    MY_CONFIG_VALUE = 3

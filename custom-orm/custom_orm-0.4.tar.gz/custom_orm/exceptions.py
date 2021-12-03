class ArgException(Exception):
    message: str

    def __init__(self, arg_name: str, class_name: str):
        raise NotImplementedError('__init__(arg_name, class_name) must be defined by subclasses')

    def __str__(self):
        return self.message


class RequiredArgException(ArgException):
    def __init__(self, arg_name: str, class_name: str):
        super(Exception, self).__init__()
        self.message = f'Argument {arg_name} must be passed for {class_name}!'


class ExtraArgException(ArgException):
    def __init__(self, arg_name: str, class_name: str):
        super(Exception, self).__init__()
        self.message = f'Argument {arg_name} must not be passed for {class_name}!'


class ManyPrimaryKeysException(Exception):
    def __str__(self):
        return 'More than 1 primary key was passed!'


class NoPrimaryKeysException(Exception):
    def __str__(self):
        return 'No primary key was passed!'

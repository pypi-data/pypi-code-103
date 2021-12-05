from flask import render_template

class CatchableException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __repr__(self):
        return self.message

def exception_to_error(app, template):
    def exception_to_error_2(func):
        def exception_to_error_3(*args, **kwargs):
            try:
                ret = func(*args, **kwargs)
            except CatchableException as e:
                return render_template(template, error_message=repr(e))
            else:
                return ret
        exception_to_error_3.__name__ = func.__name__
        return exception_to_error_3
    return exception_to_error_2

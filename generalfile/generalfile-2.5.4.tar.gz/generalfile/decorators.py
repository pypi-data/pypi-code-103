
from generallibrary.functions import wrapper_transfer


def deco_require_state(is_file=None, is_folder=None, exists=None, quick_exists=None):
    """ Decorator to easily configure and see which state to require. """
    def _decorator(function):
        def _wrapper(self, *args, **kwargs):
            """:param generalfile.Path self:"""
            if is_file is not None:
                if self.is_file() != is_file:
                    raise AttributeError(f"Path {self} is_file check didn't match ({is_file}).")
            elif is_folder is not None:
                if self.is_folder() != is_folder:
                    raise AttributeError(f"Path {self} is_folder check didn't match ({is_folder}).")
            elif exists is not None:
                if self.exists() != exists:
                    raise AttributeError(f"Path {self} exists check didn't match ({exists}).")
            elif quick_exists is not None:
                if self.exists() is not quick_exists:
                    raise AttributeError(f"Path {self} quick exists check didn't match ({quick_exists}).")
            return function(self, *args, **kwargs)
        return wrapper_transfer(function, _wrapper)
    return _decorator


def deco_preserve_working_dir(function):
    """ Decorator to preserve working dir if given function changes it somehow. """
    def _wrapper(*args, **kwargs):
        working_dir_path = args[0].Path.get_working_dir()
        result = function(*args, **kwargs)
        if working_dir_path != args[0].Path.get_working_dir():
            working_dir_path.set_working_dir()
        return result
    return wrapper_transfer(function, _wrapper)


def deco_return_if_removed(content):
    """ Decorator to return whether path exists to be removed or not. """
    def _decorator(function):
        def _wrapper(*args, **kwargs):
            path = args[0]
            if not path.exists():
                return False

            if content and path.empty():
                return False

            function(*args, **kwargs)
            return True
        return wrapper_transfer(function, _wrapper)
    return _decorator


from directoryhandler import DirectoryHandler
import importlib.util
import inspect

STANDARD_FILTER = [
    "__all__",
    "__builtins__",
    "__cached__",
    "__doc__",
    "__file__",
    "__loader__",
    "__name__",
    "__package__",
    "__spec__",
]


def get_members(module, filters=STANDARD_FILTER):
    return sorted(
        [name for name, obj in inspect.getmembers(module) if name not in filters]
    )

class AllMaker:
    def __init__(self):
        self.dh = DirectoryHandler(ext_filters=[])

    def print_all(self, file_name):
        print(self.make_all(file_name))

    def __verify_is_python_file(self, file):
        # Convert to file object if is file path
        if isinstance(file, str):
            file = self.dh.find_files_by_name(file, return_first_found=True)
            
            if file:
                if file.ext == "py":
                    return file
        return None

    def gather_from_object(self, obj):
        file = self.__verify_is_python_file(obj)
        if file:
            spec = importlib.util.spec_from_file_location(file.name, file.path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        else:
            module = dir(obj)
            
        return get_members(module)
        

    def make_all(self, type_or_file_path):
        variable_and_functions = self.gather_from_object(type_or_file_path)
        s = "__all__ = ["
        for i, v_f in enumerate(variable_and_functions):
            s = s + "\n\t" + v_f
            if not i == len(variable_and_functions) - 1:
                s = s + ","
            else:
                s = s + "\n]"
        return s
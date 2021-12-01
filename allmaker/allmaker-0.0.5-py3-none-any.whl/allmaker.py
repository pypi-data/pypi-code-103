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
            print(file)
        if file.ext == "py":
            return file
        return None

    def read_from_file(self, file):
        file = self.__verify_is_python_file(file)
        spec = importlib.util.spec_from_file_location(file.name, file.path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return get_members(module)

    def make_all(self, file_name):
        variable_and_functions = self.read_from_file(file_name)
        s = "__all__ = ["
        for i, v_f in enumerate(variable_and_functions):
            s = s + "\n\t" + v_f
            if not i == len(variable_and_functions) - 1:
                s = s + ","
            else:
                s = s + "\n]"

        return s


if __name__ == "__main__":
    file_name = "globals"
    AllMaker().print_all(file_name)
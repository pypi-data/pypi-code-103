

class _Context:
    def __init__(self, path):
        self.path = path
        self.temp_path = self.path.with_suffix(".tmp")
        self.lock = self.path.lock()

    def __enter__(self):
        self.lock.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.__exit__(exc_type, exc_val, exc_tb)


class WriteContext(_Context):
    """ A context manager used for every write method. """
    def __init__(self, path, overwrite=False):
        super().__init__(path)
        self.overwrite = overwrite

    def __enter__(self):
        """ :rtype: generalfile.Path """
        if not self.overwrite and self.path.exists():
            raise FileExistsError(f"Path '{self.path}' already exists and overwrite is 'False'.")
        super().__enter__()
        self.path.get_parent().create_folder()
        return self.temp_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.temp_path.rename(self.path.name(), overwrite=True)
        super().__exit__(exc_type, exc_val, exc_tb)


class ReadContext(_Context):
    """ A context manager used for every read method. """
    def __init__(self, path):
        super().__init__(path)

    def __enter__(self):
        super().__enter__()
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)


class AppendContext(_Context):
    """ A context manager used for every append method. """
    def __init__(self, path):
        super().__init__(path)

    def __enter__(self):
        super().__enter__()
        if self.path.exists():
            self.path.copy(self.temp_path)
        return self.temp_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.temp_path.rename(self.path.name(), overwrite=True)
        super().__exit__(exc_type, exc_val, exc_tb)


class _Extension:
    WriteContext = WriteContext
    ReadContext = ReadContext
    AppendContext = AppendContext

    def __init__(self, path):
        self.path = path



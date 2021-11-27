
from generallibrary import Timer, EmptyContext


class _Lock:
    """ A one-time-use lock used by Path.lock.
        Creates a lock for folder or path with these steps:
            Wait until unlocked.
            Create lock.
            Make sure only locked by self.
        A lock is inactive if it can be removed, as there's no Lock holding it's file stream.
        Todo: Lock the optional extra paths.
        """
    def __init__(self, abs_path, *other_paths):
        self.path = abs_path
        self.lock_file_stream = None

    def __enter__(self):
        self._attempt_lock_creation()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close_and_remove_lock()

    def _delete_if_dead(self, lock_path):
        try:
            seconds_since_creation = lock_path.seconds_since_modified()
        except (AttributeError, FileNotFoundError):
            pass
        else:
            if seconds_since_creation > lock_path.dead_lock_seconds:
                lock_path.delete(error=False)

    def _attempt_lock_creation(self):
        timer = Timer()
        while timer.seconds() < self.path.timeout_seconds:
            affecting_locks = list(self._affecting_locks())
            if self._is_locked_externally(affecting_locks=affecting_locks):
                for locked_path in affecting_locks:
                    self._delete_if_dead(locked_path.get_lock_path())
            else:
                if not self._open_and_create_lock():
                    continue  # If lock failed creating

                affecting_locks = list(self._affecting_locks())
                if self.path in affecting_locks:
                    if self._is_locked_externally(affecting_locks=affecting_locks):
                        self._close_and_remove_lock()  # Remove and try again to respect other locks
                    else:
                        return  # Success
                else:
                    raise FileNotFoundError(f"Lock '{self.path}' failed to create.")
        raise TimeoutError(f"Couldn't lock '{self.path}' in time.")

    def _open_and_create_lock(self):
        if self.lock_file_stream is not None:
            raise AttributeError(f"A file stream is already opened for '{self.path}'.")

        try:
            self.lock_file_stream = open(self.path.get_lock_path(), "x")
        except FileExistsError:
            return False

        self.lock_file_stream.write("foo")

        self.path.locked_paths.append(self.path)
        return True

    def _close_and_remove_lock(self):
        if self.lock_file_stream is None:
            raise AttributeError(f"A file stream is not opened for '{self.path}'.")

        self.path.locked_paths.remove(self.path)

        self.lock_file_stream.close()
        self.lock_file_stream = None

        self.path.get_lock_path().delete(error=False)

    def _affecting_locks(self):
        """ Returns absolute paths in list pointing to path it's locking.
            Use `get_alternative_path()` or 'get_lock_path()' if actual lock path is wanted.

            :rtype: tuple[generalfile.Path] """
        # print(len(self.path.get_lock_dir().get_children()))
        for alternative_path in self.path.get_lock_dir().get_children(gen=True):
            path = alternative_path.from_alternative()
            if self.path.startswith(path) or path.startswith(self.path):
                yield path

    def _is_locked_externally(self, affecting_locks=None):
        """ See if this lock's path is locked by an external process. """
        if affecting_locks is None:
            affecting_locks = self._affecting_locks()

        for path in affecting_locks:
            if path not in self.path.locked_paths:
                return True
        return False


class Path_ContextManager:
    """ Context manager methods for Path. """
    locked_paths = []

    @staticmethod
    def _create_context_manager(path, *other_paths):
        """ :param generalfile.Path path: """
        path_is_lock = path.startswith(path.get_lock_dir())
        path_already_locked_by_this_process = path in path.locked_paths
        if path_is_lock or path_already_locked_by_this_process:
            return EmptyContext()  # Create fake lock
        else:
            return _Lock(path, *other_paths)  # Create real lock

    def lock(self, *other_paths):
        """ Create a lock for this path unless path is inside `lock dir`.
            Optionally supply additional paths to create locks for them too.
            Locks are stored in a list Path's cls, so only locks outside of this scope are respected.
            That allows us to automatically create fake recursive locks, where all obey the first outer lock.

            :param generalfile.Path self: """
        return self._create_context_manager(self.absolute(), *other_paths)

    def as_working_dir(self):
        """ Temporarily set working dir.

            :param generalfile.Path self: """
        return TempWorkingDir(self)


class TempWorkingDir:
    """ Temporarily set working dir. """
    def __init__(self, path):
        self.path = path
        self.original_working_dir = path.get_working_dir()

    def __enter__(self):
        self.path.set_working_dir()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.original_working_dir.set_working_dir()




























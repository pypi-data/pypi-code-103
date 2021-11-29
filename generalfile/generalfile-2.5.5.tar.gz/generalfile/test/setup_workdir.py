

def setup_workdir(use_working_dir=False):
    """ Class to set up working dir for tests, File extensions import this class.
        Set working dir and clear it after it's made sure it's correct path."""
    path = Path.get_working_dir() if use_working_dir else Path(__file__).get_parent()

    if path.endswith("test"):
        path /= "tests"
    else:
        path /= "test/tests"

    path.set_working_dir()

    if not Path.get_working_dir().endswith("test/tests"):
        raise EnvironmentError(f"Failed setting correct working dir, should be ..test/tests but it's {path}")
    path.delete_folder_content()


from generalfile.path import Path

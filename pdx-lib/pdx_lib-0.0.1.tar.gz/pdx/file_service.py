from pdx import Session
from pdx import Console
from pdx import Executor
import os
import fileinput
import fnmatch

out = Console.get()


def get_file_content_string(file_path):
    """Get file content as one string"""
    if not os.path.exists(file_path):
        out.put_warning("Given file does not exist: {0}".format(file_path))
        return None

    content = None
    try:
        with open(file_path, 'r') as f_in:
            content = f_in.read()
    except Exception as ee:
        out.unexpected_error(ee, "Error opening file: {0}".format(file_path))

    return content


def get_file_content_lines(file_path):
    """Get file content as a list of lines"""
    try:
        return get_file_content_string(file_path).splitlines()
    except AttributeError:
        # If get_file_content_string returned None, an error was already printed
        return None


def replace_line(file_path, line_starts_with, new_text, strip_test_line=True):
    """Replace a given line in a file with a given string"""
    out.trace("replace_line", [file_path, line_starts_with, new_text, strip_test_line])
    content_updated = False
    try:
        file_obj = fileinput.FileInput(file_path, inplace=True, backup='.bak')
        for line in file_obj:
            if line.startswith(line_starts_with):
                # Print new content. Add a new-line character
                out.put("{0}".format(new_text))
                content_updated = True
            else:
                # Write current line back to file (already contains a new-line character)
                out.put(line, end='')
        file_obj.close()
        os.unlink("{0}.bak".format(file_path))
    except Exception as ee:
        out.unexpected_error(ee, "Could not modify file: {0}".format(file_path))

    return content_updated


def find_git_repos(base_directory=None):
    """
    Find files whose name matches a given pattern
    returns: List of matching file paths
    """
    out.trace("find_file_pattern", [base_directory])

    # If no base directory specified, search user's home directory
    if base_directory is None:
        base_directory = Session.user_home

    result = []
    for root, dirs, files in os.walk(base_directory, topdown=True):
        dirs[:] = [dd for dd in dirs if dd == '.git' or not dd.startswith('.')]
        if '.git' in dirs:
            result.append(root)

    return result


def find_file_pattern(pattern, base_directory=None, include_hidden_dirs=False, include_links=False):
    """
    Find files whose name matches a given pattern
    returns: List of matching file paths
    """
    out.trace("find_file_pattern", [pattern, include_hidden_dirs, include_links])

    # If no base directory specified, search user's home directory
    if base_directory is None:
        base_directory = Session.user_home

    result = []
    for root, dirs, files in os.walk(base_directory, topdown=True):
        dirs[:] = [dd for dd in dirs if include_hidden_dirs or not dd.startswith('.')]
        for name in fnmatch.filter(files, pattern):
            path = os.path.join(root, name)
            # If this is not a link, or we are including links
            if include_links or not os.path.islink(path):
                result.append(os.path.join(root, name))

    return result


def find_banner_repository():
    """
    Get the path to the Banner repository on this machine
    :return: String
    """
    exe = Executor.Executor("locate twbkwbis.sql")
    if exe.return_code == 0:
        for path in exe.get_output().splitlines():
            dir = path.replace("/wtlweb/dbprocs/twbkwbis.sql", "")
            if os.path.isdir(dir):
                return dir

    return None

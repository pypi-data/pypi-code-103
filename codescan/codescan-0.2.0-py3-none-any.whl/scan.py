import os
from pathlib import Path
from codescan.file import  get_files_from_git, get_files_from_dir, open_file
from codescan.patterns import check_security_pattern, check_leaks_in_comments
from codescan.print import error
from progress.bar import Bar
from progress.spinner import Spinner

def return_results(completed: bool, results: list):
    result_to_return = {
        "completed": completed,
        "with_leaks": False,
        "results": results
    }

    if len(results) > 0:
        result_to_return['with_leaks'] = True

    return result_to_return


def leak_is_valid(leaks_array):
    if leaks_array and len(leaks_array[0]) >= 3:
        return str(leaks_array[0][0]) and str(leaks_array[0][1]) and str(leaks_array[0][2])
    return None


def check_line_security_leaks(line: str):
    leak = check_security_pattern(line)

    if leak_is_valid(leak):
        return leak[0][0]

    else:
        leak = check_leaks_in_comments(line)
        if leak_is_valid(leak):
            return leak[0][0]


def check_content_security_leaks(file_name: str):
    content = open_file(file_name)
    results = []
    if content:
        for index, line in enumerate(content):
            leak = check_line_security_leaks(line)
            if leak:
                results.append([file_name, index + 1, leak])

    return results


def check_files_security_leaks(files: list[str]):
    scan_results = []
    bar = Bar('Scanning Files ', max=len(files))
    for file_name in files:
        results = check_content_security_leaks(file_name)
        if len(results) > 0:
            scan_results += results
        bar.next()

    bar.finish()
    return scan_results


def full_scan(path: Path, exclude_file: str):
    """
    codescan all the files in path
    ...

    Parameters
    ----------
    path: Path
        path of the directory where the files are located

    exclude_file : str
        a file that contains the list of files to be excluded

    Returns
    -------
    results of the codescan

    """

    files = get_files_from_dir(path, exclude_file)

    return check_files_security_leaks(files)


def git_scan():
    cwd = Path(os.getcwd())

    if not os.path.isdir(cwd / ".git"):
        error("Error: Not a git repository")
        exit()

    files = get_files_from_git()

    return check_files_security_leaks(files)

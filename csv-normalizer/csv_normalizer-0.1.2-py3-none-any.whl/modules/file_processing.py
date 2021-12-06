from pathlib import Path

def get_file_list(directory, extension='*.csv'):
    """
    return: files list found in directory using absolut path 
    """
    path_obj = Path(directory) # type string
    file_list = [] # type list

    if path_obj.is_dir():
        for filename in path_obj.glob(extension):
            file_list.append(str(filename.resolve()))
    else:
        raise SystemExit(f"ERROR: import_folder is not a directory: {directory} \n"
                         "Ensure you use slashes / to separate folders")
    
    return file_list

def rename_file(file, target):
    """
    param file: file to rename
    param target: target path
    return: PosixPath('target') rename operation
    """
    path_obj = Path(file)
    target = Path(target)
    return path_obj.rename(target)

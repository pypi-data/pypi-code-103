import json
import os
import sys
from collections import OrderedDict
from pathlib import Path

import requests
import yaml
from tqdm import tqdm


class ModifiedFileState:
    NO_CHANGE = '[Content already existed]'
    HAS_APPENDED = '[New content appended]'
    HAS_CREATED_NEW = '[New content generated]'


def download_to_file(url: str, file_path: str):
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024
    *_, file_name = os.path.split(file_path)
    progress_bar = tqdm(
        total=total_size_in_bytes,
        desc=f'Downloading {file_name}',
        bar_format='{desc:50} {bar:30} {percentage:3.0f}% [{n_fmt}/{total_fmt}, {rate_fmt}]',
        unit='iB',
        unit_scale=True,
        colour='blue'
    )
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print('ERROR, something went wrong')
        return None
    return file_path


def create_file(content,
                file_name,
                file_extension,
                folder=None,
                append_to_file=False,
                fixed_header: str = None,
                fixed_footer: str = None):
    if folder:
        if file_extension:
            file_path = '{}/{}.{}'.format(folder, file_name, file_extension)
        else:
            file_path = '{}/{}'.format(folder, file_name)
    else:
        if file_extension:
            file_path = '{}.{}'.format(file_name, file_extension)
        else:
            file_path = '{}'.format(file_name)
    # write to file
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        content_file = ''
        additional_info = ''
        if Path(file_path).exists():
            with open(file_path, 'r') as file:
                content_file = file.read()
            if append_to_file is True and content in content_file:
                additional_info = ModifiedFileState.NO_CHANGE
                return file_path, additional_info
        with open(file_path, 'wb') as file:
            header = fixed_header or ''
            footer = fixed_footer or ''
            if append_to_file is not True:
                content = header + content + footer
                additional_info = ModifiedFileState.HAS_CREATED_NEW
            else:
                if header not in content_file:
                    content = header + content
                content_file = content_file.replace(footer, '')
                content = content_file + content + footer
                additional_info = ModifiedFileState.HAS_APPENDED
            file.write(content.encode('utf8'))
    except Exception as e:
        print(e)
    return file_path, additional_info


def create_json_file(json_dict: dict,
                     file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf8') as json_file:
        json.dump(json_dict,
                  json_file,
                  ensure_ascii=False,
                  indent=2)
    return file_path, ModifiedFileState.HAS_CREATED_NEW


def create_yaml_file(yaml_dict: dict,
                     file_path):
    # Enable PyYAML support for OrderedDict
    yaml.add_representer(
        OrderedDict,
        lambda dumper, data: dumper.represent_dict(
            getattr(data,
                    "viewitems" if sys.version_info < (3,) else "items")()),
        Dumper=yaml.SafeDumper)
    # Start dumping dict into yaml
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf8') as yaml_file:
        yaml.safe_dump(yaml_dict,
                       yaml_file,
                       default_flow_style=False,
                       sort_keys=False)
    return file_path, ModifiedFileState.HAS_CREATED_NEW


def make_dirs(path, output_path):
    current_directory = os.getcwd() if output_path == '.' else output_path
    make_dir(current_directory, path)


def make_dir(current_directory, new_directory_name):
    directory = os.path.join(current_directory,
                             r'{}'.format(new_directory_name))
    try:
        os.makedirs(directory)
    except Exception as e:
        print(e)
        pass
    return directory


def validate_json_content(content_file: str):
    try:
        json.loads(content_file)
        return True
    except ValueError:
        return False


def validate_yaml_content(content_file: str):
    try:
        yaml.safe_load(content_file)
        return True
    except yaml.YAMLError:
        return False


def get_flutter_project_package():
    try:
        infile = open('pubspec.yaml', 'r')
        return infile.readline().replace('name:', '').strip()
    except (IOError, OSError):
        print('Please run this command in flutter folder.')
        exit(1)


def make_content_output_file(file_path: str, additional_info: str = None):
    sub_info = additional_info or ''
    return f'   └──{file_path:54}{sub_info:>34}'

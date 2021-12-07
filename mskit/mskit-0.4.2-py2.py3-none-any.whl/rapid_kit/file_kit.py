import io
import os
import pickle
import time
import typing

import numpy as np
import pandas as pd

from .data_struc_kit import sum_list


def split_file_nparts(
        filepath: os.PathLike,
        expected_nparts: int = 10,
        required_part_idx: tuple = None,
        start_pos: int = 0,
        openmode: str = 'r',
        writemode: str = 'w',
        identifier_pos: str = 'before_suffix',
):
    dir_name = os.path.dirname(filepath)
    basename, suffix = os.path.splitext(os.path.basename(filepath))
    with open(filepath, openmode) as f:
        size = f.seek(0, 2)
        part_size = int(np.ceil(size / expected_nparts))
        curr_pos = start_pos
        f.seek(curr_pos)
        for idx, end in enumerate([*list(range(part_size, size, part_size)), size], 1):
            if required_part_idx is not None and idx not in required_part_idx:
                continue
            if identifier_pos == 'before_suffix':
                new_file = os.path.join(dir_name, f'{basename}-Part{idx}_{end}.{suffix}')
            elif identifier_pos == 'after_file':
                new_file = f'{filepath}-Part{idx}_{end}'
            else:
                raise ValueError
            with open(new_file, writemode) as f2:
                while curr_pos <= end:
                    f2.write(f.readline())
                    curr_pos = f.tell()


def adjust_file_block_pos(
        f: io.TextIOWrapper,
        start_pos: int,
        end_pos: int,
        split_symbol: str = '\n',
        adjust_direct: str = 'forward'
):
    """
    adjust_direct: 'forward' or 'backward'

    """
    # TODO
    if start_pos != 0:
        f.seek(start_pos - 1)
        if f.read(1) != '\n':
            line = f.readline()
            start_pos = f.tell()
    f.seek(start_pos)
    while (start_pos <= end_pos):
        line = f.readline()
        start_pos = f.tell()


def split_file_block(
        file: typing.Union[str, io.TextIOWrapper],
        mode='rb',
        block_num: int = None,
        block_adjust_symbol=None,
):
    if block_num is None:
        block_num = os.cpu_count()
    if isinstance(file, io.TextIOWrapper):
        file = file.name

    with open(file, mode) as f:
        file_size = f.seek(0, 2)
        if file_size < block_num:
            raise ValueError(f'Input file size is smaller than block number: {block_num} blocks for file {file}')
        block_size = int(file_size / block_num)

        # TODO check \n or other defined symbol in loop and adjust position
        #  `If block_adjust_symbol is not None: adjust_file_block_pos...`
        pos_list = []
        start_pos = 0
        for i in range(block_num):
            if i == block_num - 1:
                end_pos = file_size - 1
                pos_list.append((start_pos, end_pos))
                break
            end_pos = start_pos + block_size - 1
            if end_pos >= file_size:
                end_pos = file_size - 1
            if start_pos >= file_size:
                break
            pos_list.append((start_pos, end_pos))
            start_pos = end_pos + 1

    return pos_list


def file_prefix_time(with_dash=False):
    curr_time = time.strftime('%Y%m%d', time.localtime())
    prefix = curr_time + '-' if with_dash else curr_time
    return prefix


def pd_read_csv_skip_row(file, comment=None, **kwargs):
    if os.stat(file).st_size == 0:
        raise ValueError("File is empty")
    with open(file, 'r') as f:
        pos = 0
        cur_line = f.readline()
        while cur_line.startswith(comment):
            pos = f.tell()
            cur_line = f.readline()
            f.seek(pos)
    return pd.read_csv(f, **kwargs)


def read_one_col_file(file, skiprows=None):
    with open(file, 'r') as f:
        one_col_list = [row.strip('\n') for row in f.readlines()]
        one_col_list = one_col_list[skiprows:] if skiprows is not None else one_col_list
        while '' in one_col_list:
            one_col_list.remove('')
    return one_col_list


def flatten_two_headers_file(
        file,
        header_num=2,
        sep=',',
        method=None
) -> pd.DataFrame:
    """

    method: stack headers or cross-insert or lower-first

    Headle file with two headers like

    Peptide_Order	Peptide	Peptide_Mass	Modifications	Proteins
        Spectrum_Order	Title	Charge	Precursor_Mass
    1	AAAAAAAAAAAAAAAAAA	2000	Carbamidomethyl[C](9)	PAK
        1	T1	3	1999
        2	T2	3	1999
        3	T3	3	1999
        4	T1	3	1999
        5	T5	3	1999
    2	CCCCCCCCCCCCCCC	3000	Carbamidomethyl[C](15)	PBK
        1	T2	3	2999
    3	DDDDDDDDDDDDDDDD	4000	null	PCK
        1	T3	3	3999
        2	T1	3	3999
        3	T2	3	3999

    """
    if isinstance(file, str):
        if len(file) < 500 and os.path.exists(file):
            with open(file, 'r') as f:
                file = f.readlines()
        else:
            file = file.split('\n')

    headers = [file[i].rstrip(f'\n{sep}').split(sep) for i in range(header_num)]
    headers_used_col_idx = [[idx for idx, value in enumerate(header) if value != ''] for header in headers]
    headers_used_col_num = [len(idx) for idx in headers_used_col_idx]

    if method is None or method == 'stack':
        flatten_text_used_col_idx = []
        for idx, num in enumerate([0, *headers_used_col_num][:-1]):
            flatten_text_used_col_idx.append(np.arange(num, num + headers_used_col_num[idx]))
    elif method == 'cross-insert':
        flatten_text_used_col_idx = []
    elif method == 'lower-first':
        flatten_text_used_col_idx = []
    else:
        raise

    flatten_header = sum_list([[value for value in header if value != ''] for header in headers])
    flatten_col_num = len(flatten_header)
    flatten_text = []

    header_level = 1
    consensus_text = ['' for i in range(flatten_col_num)]
    for row in file[header_num:]:
        row = row.rstrip(f'\n{sep}').split(sep)
        for idx, value in enumerate(row, 1):
            if value != '':
                header_level = idx
                break
        if header_level == 1:
            consensus_text = ['' for i in range(flatten_col_num)]

        for value_idx, raw_idx in enumerate(headers_used_col_idx[header_level - 1]):
            consensus_text[flatten_text_used_col_idx[header_level - 1][value_idx]] = row[raw_idx]

        if header_level == header_num:
            flatten_text.append(consensus_text.copy())

    return pd.DataFrame(flatten_text, columns=flatten_header)


def process_list_or_file(x):
    if isinstance(x, list) or isinstance(x, set):
        target_list = x
    else:
        if os.path.isfile(x):
            target_list = read_one_col_file(x)
        else:
            raise
    return target_list


def print_path_basename_in_dict(path_dict: dict):
    for name, path in path_dict.items():
        print(f'{name}: {os.path.basename(path)}')


def print_path_exist():
    try:
        print(check_path)
    except FileNotFoundError:
        ...


def check_path(
        path: str,
        name: str = None,
        shown_path_right_idx: typing.Union[None, int, list, tuple] = 1,
        show_all_after_idx: bool = True,
        raise_error: bool = False,
        verbose: bool = False
):
    if shown_path_right_idx is None:
        shown_filepath = path
    elif isinstance(shown_path_right_idx, int):
        if shown_path_right_idx < 0:
            shown_filepath = path
        elif shown_path_right_idx == 0:
            shown_filepath = os.path.basename(path)
        else:
            split_path = path.split(os.path.sep)
            shown_filepath = os.path.sep.join(split_path[-shown_path_right_idx:]) if show_all_after_idx else split_path[-shown_path_right_idx]
    elif isinstance(shown_path_right_idx, (list, tuple)):
        # TODO join selected idx
        for idx in shown_path_right_idx:
            pass
    else:
        raise ValueError(f'Param `shown_path_right_idx` must be None or integer or list/tuple of integet. Now {shown_path_right_idx}')
    if name is not None:
        print(f'{os.path.exists(path)} - {name}: {shown_filepath}')
    else:
        print(f'{os.path.exists(path)} - {shown_filepath}')


def check_path_in_dict(path_dict: dict, shown_filename_right_idx: int = None):
    # TODO 显示的文件名称可以是多个 idx 对应 substring 的组合
    """
    :param path_dict:
    :param shown_filename_right_idx: None or int. None: use full path (raw value in dict). int: use idx part of file path (right count with 1st-first idx)
    """
    print(f'Total {len(path_dict)} files')
    for name, path in path_dict.items():
        if shown_filename_right_idx is None or (isinstance(shown_filename_right_idx, int) and shown_filename_right_idx == 0):
            shown_filename = path
        elif isinstance(shown_filename_right_idx, int) and shown_filename_right_idx > 0:
            used_path = path
            for _ in range(shown_filename_right_idx):
                used_path = os.path.dirname(used_path)
            shown_filename = os.path.basename(used_path)
        else:
            raise ValueError(f'Param `shown_filename_right_idx` must be None or any positive integer. Now {shown_filename_right_idx}')
        print(f'{os.path.exists(path)} - {name}: {os.path.basename(shown_filename)}')


def check_input_df(data, *args) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        df = data
    else:
        if os.path.exists(data):
            df = pd.read_csv(data, *args)
        else:
            raise FileNotFoundError
    return df


def fill_path_dict(path_to_fill: str, fill_string: dict, exist_path_dict: dict = None):
    if exist_path_dict is None:
        path_dict = dict()
    else:
        path_dict = exist_path_dict.copy()

    for k, file_name in fill_string.items():
        file_name = [file_name] if isinstance(file_name, str) else file_name
        path_dict[k] = path_to_fill.format(*file_name)
    return path_dict


def join_path(path, *paths, create=False):
    pass


def write_inten_to_json(prec_inten: dict, file_path):
    total_prec = len(prec_inten)
    with open(file_path, 'w') as f:
        f.write('{\n')

        for prec_idx, (prec, inten_dict) in enumerate(prec_inten.items(), 1):
            f.write('    "%s": {\n' % prec)
            frag_num = len(inten_dict)
            for frag_idx, (frag, i) in enumerate(inten_dict.items(), 1):
                if frag_idx != frag_num:
                    f.write(f'        "{frag}": {i},\n')
                else:
                    f.write(f'        "{frag}": {i}\n')

            if prec_idx != total_prec:
                f.write('    },\n')
            else:
                f.write('    }\n')

        f.write('}')


def data_dump_load_skip(file_path, data=None, cover_data=False, update_file=False):
    if not os.path.exists(file_path):
        if data is not None:  # Here use 'is not None' because some thing will be wrong when the data is a pd.DataFrame. (Truth value is ambiguous error)
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
        else:
            raise FileNotFoundError('No existing file and no input data')
    else:
        if data is not None:
            if update_file:
                with open(file_path, 'wb') as f:
                    pickle.dump(data, f)
            elif cover_data:
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
            else:
                pass
        else:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
    return data


def xlsx_sheets_to_text_files(
        xlsx_path,
        output_folder,
        sheet_name_trans_func=lambda x: x.replace(' ', '_'),
        skipped_row_idx=None,
):
    try:
        import openpyxl
    except ModuleNotFoundError:
        raise ModuleNotFoundError('Need module `openpyxl` to parse xlsx file and sheets')

    wb = openpyxl.open(xlsx_path)
    for sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]
        used_name = sheet_name_trans_func(sheet_name)
        with open(os.path.join(output_folder, f'{used_name}.txt'), 'w') as f:
            for row_idx, row in enumerate(sheet.iter_rows(values_only=True)):
                if isinstance(skipped_row_idx, (tuple, list)):
                    if row_idx in skipped_row_idx:
                        continue
                row = '\t'.join([(str(_) if _ is not None else '') for _ in row])
                f.write(row + '\n')

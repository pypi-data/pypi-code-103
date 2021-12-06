#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .error import Error
from .file import should_exists
from .form import Form


def load_form_from_csv_file(err: Error, file_path='', do_strip=True, splitter: str = ','):
    if err.has_error():
        return None

    if not should_exists(err, file_path):
        return None

    data = Form(err)
    with open(file_path, "rt") as f:
        line_no = 1
        for line in f:
            cells = split_line(line, do_strip, splitter)
            if len(cells) > 0:
                if data.title_row.is_inited():
                    data.append_data_row(line_no, cells, do_strip)
                else:
                    data.set_title_row(line_no, cells, do_strip)

            line_no += 1

    if err.has_error():
        return None
    return data


def split_line(line: str, do_strip=True, splitter: str = ','):
    parts = line.split(splitter)
    res = []
    tmp_part = ''
    in_double_quotation_mark = False
    for part in parts:
        part_has_even_double_quotation_marks = part.count('"') % 2 == 0
        if in_double_quotation_mark:
            tmp_part = tmp_part + ',' + part
            if not part_has_even_double_quotation_marks:
                in_double_quotation_mark = False
                res.append(remove_double_quotation_marks(tmp_part))
        else:
            tmp_part = part
            if part_has_even_double_quotation_marks:
                res.append(remove_double_quotation_marks(tmp_part))
            else:
                in_double_quotation_mark = True

    if do_strip:
        return list(map(lambda x: x.strip(), res))


def remove_double_quotation_marks(part: str):
    part_len = len(part)
    if part_len > 1 and part[0] == '"' and part[part_len - 1] == '"':
        return part[1:part_len-1]
    return part

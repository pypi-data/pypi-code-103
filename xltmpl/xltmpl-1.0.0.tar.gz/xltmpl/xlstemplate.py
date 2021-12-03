# -*- coding: utf-8 -*-
import xlrd_
from xlwt import Workbook, Worksheet

from xltmpl.utils import index_to_column_letter
from xlutils_.copy import copy
from xltmpl.xltemplatefactory import XLSheetBehaviorFactory
import pandas as pd


class XlsTemplate(Workbook, XLSheetBehaviorFactory):
    def __init__(self, tmpl_path, save_path=None, apply_styles=True, place_holder='{{}}'):
        super().__init__()
        self._tmpl_wb: xlrd_.Book = None
        self.wb: Workbook = None
        self.tmpl_path = tmpl_path
        self._copy_template_attr()

        self.save_path = save_path
        self.apply_styles = apply_styles
        self.place_holder = place_holder
        self.sheet_headers: dict = {}

    def _copy_template_attr(self):
        wb = xlrd_.open_workbook(self.tmpl_path, formatting_info=True)
        self._tmpl_wb = wb
        self.wb = copy(wb)

    def _get_styles(self):
        styles = {}
        try:
            for sheet_index in range(256):
                sheet = self.wb.get_sheet(sheet_index)

        except Exception as e:
            pass

    @staticmethod
    def get_cell(sheet, colIndex, rowIndex):
        """ HACK: Extract the internal xlwt cell representation. """
        row = sheet._Worksheet__rows.get(rowIndex)

        if not row:
            return None

        cell = row._Row__cells.get(colIndex)
        return cell

    def set_cell(self, sheet, col, row, value, style_row: int = None):
        """ Change cell value without changing formatting. """
        if style_row is not None:
            tmpl_cell = self.get_cell(sheet, col, style_row - 1)
        else:
            tmpl_cell = self.get_cell(sheet, col, row)

        if tmpl_cell is not None:
            xf_idx = tmpl_cell.xf_idx
            sheet.write(row, col, value)
            if style_row is not None and sheet.name in self._tmpl_wb.sheet_names():
                cell = self.get_cell(sheet, col, row)
                cell.xf_idx = xf_idx
        else:
            sheet.write(row, col, value)

    def ensure_sheet_exist(self, sheet_name):
        try:
            sheet: Worksheet = None
            try:
                if isinstance(sheet_name, int):
                    if sheet_name >= 1:
                        sheet = self.wb.get_sheet(sheet_name - 1)
                    else:
                        sheet = self.wb.add_sheet(str(sheet_name))
                else:
                    sheet = self.wb.get_sheet(str(sheet_name))
            except Exception as e:
                sheet = self.wb.add_sheet(str(sheet_name))
            return sheet
        except Exception as e:
            raise Exception(e)

    def _is_new_sheet(self, sheet):
        if sheet.name in self._tmpl_wb.sheet_names():
            return True
        else:
            return False

    def _append(self, sheet_name, row, style_row: int = None):
        try:
            sheet: Worksheet = self.ensure_sheet_exist(sheet_name)
            lstr = sheet.last_used_row
            lstc = sheet.last_used_col
            if lstr > 0:
                pass
            else:
                isEmptyFirstRow = True
                for col in range(256):
                    if self.get_cell(sheet, col, 0):
                        isEmptyFirstRow = False
                        break
                if isEmptyFirstRow:
                    lstr = 0

            if hasattr(sheet, 'is_not_first_write'):
                next_row = lstr + 1
            else:
                if style_row is not None:
                    next_row = style_row - 1
                else:
                    next_row = lstr + 1
            for col, value in enumerate(row):
                self.set_cell(sheet, col, next_row, value, style_row)
            if not hasattr(sheet, 'is_not_first_write'):
                for col in range(len(row), 256):
                    self.set_cell(sheet, col, next_row, None, style_row)
            sheet.is_not_first_write = True
        except Exception as e:
            raise Exception(e)

    def append(self, sheet_name, row, style_row: int = None):
        self._append(sheet_name, row, style_row)

    def append_row(self, sheet_name, row, style_row: int = None):
        self._append(sheet_name, row, style_row)

    def append_rows(self, sheet_name, rows, style_row: int = None):
        try:
            sheet: Worksheet = self.ensure_sheet_exist(sheet_name)
            for row in rows:
                lstr = sheet.last_used_row
                lstc = sheet.last_used_col
                if lstr > 0:
                    pass
                else:
                    isEmptyFirstRow = True
                    for col in range(256):
                        if self.get_cell(sheet, col, 0):
                            isEmptyFirstRow = False
                            break
                    if isEmptyFirstRow:
                        lstr = 0

                if hasattr(sheet, 'is_not_first_write'):
                    next_row = lstr + 1
                else:
                    if style_row is not None:
                        next_row = style_row - 1
                    else:
                        next_row = lstr + 1
                for col, value in enumerate(row):
                    self.set_cell(sheet, col, next_row, value, style_row)
                if not hasattr(sheet, 'is_not_first_write'):
                    for col in range(len(row), 256):
                        self.set_cell(sheet, col, next_row, None, style_row)
                sheet.is_not_first_write = True
        except Exception as e:
            raise Exception(e)

    def append_dict(self, sheet_name, dict_: dict, header_row=None, style_row: int = None):
        self._append_dict(sheet_name, dict_, header_row, style_row)

    def _append_dict(self, sheet_name, dict_: dict, header_row=None, style_row: int = None):
        try:
            sheet: Worksheet = self.ensure_sheet_exist(sheet_name)
            lstc = sheet.last_used_col
            lstr = sheet.last_used_row
            header: list = []
            if sheet.name in self._tmpl_wb.sheet_names():
                if sheet.name in self.sheet_headers:
                    header = self.sheet_headers[sheet.name]
                else:
                    header_cells = self._tmpl_wb.sheet_by_name(sheet.name).row(header_row-1)
                    header = [index_to_column_letter(idx)
                              if any([isinstance(cell.value, (int, float, bool)), cell.value in ['']])
                              else str(cell.value).strip().replace('\n', '')
                              for idx, cell in enumerate(header_cells)]
                    self.sheet_headers[sheet.name] = header
            else:
                raise ValueError('can not use this method to new sheet')
            if hasattr(sheet, 'is_not_first_write'):
                next_row = lstr + 1
            else:
                if style_row is not None:
                    next_row = lstr
                else:
                    next_row = lstr + 1
                for colIndex in range(256):
                    self.set_cell(sheet, colIndex, next_row, None, style_row)
            for key in dict_:
                if key not in header:
                    continue
                if isinstance(dict_[key], (list, tuple, set)):
                    colIndex = header.index(key)
                    for offset_y, value in enumerate(dict_[key]):
                        self.set_cell(sheet, colIndex, next_row+offset_y, value, style_row)
                else:
                    colIndex = header.index(key)
                    value = dict_[key]
                    self.set_cell(sheet, colIndex, next_row, value, style_row)
            sheet.is_not_first_write = False
        except Exception as e:
            raise Exception(e)

    def append_dataframe(self, sheet_name, df: pd.DataFrame, keep_headers=False, header_row: int = None, style_row: int = None):
        try:
            if keep_headers:
                raise Exception('keep_headers not be implemented')
            sheet: Worksheet = self.ensure_sheet_exist(sheet_name)
            for idx, row in df.iterrows():
                dict_ = row.to_dict()
                lstc = sheet.last_used_col
                lstr = sheet.last_used_row
                header: list = []
                if sheet.name in self._tmpl_wb.sheet_names():
                    if sheet.name in self.sheet_headers:
                        header = self.sheet_headers[sheet.name]
                    else:
                        header_cells = self._tmpl_wb.sheet_by_name(sheet.name).row(header_row - 1)
                        header = [index_to_column_letter(idx)
                                  if any([isinstance(cell.value, (int, float, bool)), cell.value in ['']])
                                  else str(cell.value).strip().replace('\n', '')
                                  for idx, cell in enumerate(header_cells)]
                        self.sheet_headers[sheet.name] = header
                else:
                    raise ValueError('can not use this method to new sheet')
                if hasattr(sheet, 'is_not_first_write'):
                    next_row = lstr + 1
                else:
                    if style_row is not None:
                        next_row = lstr
                    else:
                        next_row = lstr + 1
                    for colIndex in range(256):
                        self.set_cell(sheet, colIndex, next_row, None, style_row)
                for key in dict_:
                    if key not in header:
                        continue
                    if isinstance(dict_[key], (list, tuple, set)):
                        colIndex = header.index(key)
                        for offset_y, value in enumerate(dict_[key]):
                            self.set_cell(sheet, colIndex, next_row + offset_y, value, style_row)
                    else:
                        colIndex = header.index(key)
                        value = dict_[key]
                        self.set_cell(sheet, colIndex, next_row, value, style_row)
                sheet.is_not_first_write = False
        except Exception as e:
            raise Exception(e)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wb.save(self.save_path)


if __name__ == '__main__':
    xl_path = '../test.xls'
    xl_save = 'save.xls'
    with XlsTemplate(tmpl_path=xl_path, save_path=xl_save) as tmpl:
        data = {
            '浦发订单号': ['蔡文姬', '甄姬'],
            '派送地址': ['辅助', '法师']
        }
        df = pd.DataFrame(data)
        tmpl.append_dataframe(0, df, header_row=1)

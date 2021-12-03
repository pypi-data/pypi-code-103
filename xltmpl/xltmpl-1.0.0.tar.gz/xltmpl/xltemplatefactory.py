# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
import pandas as pd


class XLSheetBehaviorFactory:
    @abstractmethod
    def ensure_sheet_exist(self, sheet_name):
        pass

    @abstractmethod
    def append(self, sheet_name, row, style_row: int = None):
        pass

    @abstractmethod
    def append_row(self, sheet_name, row, style_row: int = None):
        pass

    @abstractmethod
    def append_rows(self, sheet_name, rows, style_row: int = None):
        pass

    @abstractmethod
    def append_dataframe(self, sheet_name, df: pd.DataFrame, keep_headers=False, header_row: int = None, style_row: int = None):
        pass

    @abstractmethod
    def append_dict(self, sheet_name, dict_: dict, header_row=None, style_row: int = None):
        pass


# Copyright (c) 2010-2021 openpyxl_


from openpyxl_.compat.numbers import NUMPY
from openpyxl_.xml import DEFUSEDXML, LXML
from openpyxl_.workbook import Workbook
from openpyxl_.reader.excel import load_workbook as open
from openpyxl_.reader.excel import load_workbook
import openpyxl_._constants as constants


# Expose constants especially the version number

__author__ = constants.__author__
__author_email__ = constants.__author_email__
__license__ = constants.__license__
__maintainer_email__ = constants.__maintainer_email__
__url__ = constants.__url__
__version__ = constants.__version__

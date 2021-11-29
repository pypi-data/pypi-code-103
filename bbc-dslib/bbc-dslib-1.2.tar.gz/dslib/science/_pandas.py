import pandas as pd

from dslib.utils import log


def configure_pandas(max_rows=None, max_columns=None, max_width=None, max_colwidth=None, logger=None):
    pd.set_option('display.max_rows', max_rows)
    pd.set_option('display.max_columns', max_columns)
    pd.set_option('display.max_colwidth', max_colwidth)
    pd.set_option('display.width', max_width)
    pd.set_option('display.expand_frame_repr', True)
    log('Pandas options were successfully set', logger=logger)

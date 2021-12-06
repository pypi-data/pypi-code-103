import awswrangler as wr
from typing import Dict, Any, List, Iterable
import time
import psycopg2
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import pandas as pd
import io
import teradatasql
import awswrangler as wr


def split_column_type(features: Dict[str, str], exclude_cols: Iterable[str] = None):
    exclude_cols = set(col.lower() for col in (exclude_cols or []))
    categorical_cols = []
    numerical_cols = []
    for k, v in features.items():
        if k.lower() not in exclude_cols:
            if v.upper().startswith(("CHAR", "STRING", "VARCHAR")):
                categorical_cols.append(k)
            else:
                numerical_cols.append(k)
    categorical_cols.sort()
    numerical_cols.sort()

    return categorical_cols, numerical_cols

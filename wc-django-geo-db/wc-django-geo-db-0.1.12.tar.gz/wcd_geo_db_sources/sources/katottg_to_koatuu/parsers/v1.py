import json
from typing import TYPE_CHECKING, TextIO
from enum import Enum
import tempfile
from pandas import read_excel

from ..._base.parser import json_encoder

if TYPE_CHECKING:
    from ..process import KATOTTG_TO_KOATUUImportRunner


UA_CODE = 'UA'


class Field(int, Enum):
    KOATUU: int = 1
    KATOTTG: int = 4



def parse(runner: 'KATOTTG_TO_KOATUUImportRunner', file: TextIO):
    dfs = read_excel(file.name)
    items = [
        (row[Field.KATOTTG], row[Field.KOATUU])
        for row in dfs.itertuples()
        if (
            row[Field.KATOTTG] and
            isinstance(row[Field.KATOTTG], str) and
            row[Field.KATOTTG].startswith(UA_CODE)
        )
    ]

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp.write(json.dumps(
            items,
            default=json_encoder
        ))

    return tmp.name

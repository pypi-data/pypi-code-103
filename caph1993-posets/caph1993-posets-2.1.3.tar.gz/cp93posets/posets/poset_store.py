from __future__ import annotations
from typing import Sequence, Tuple, List, Union, Dict, Any
from pathlib import Path
import json, os, warnings
from cp93pytools.easySqlite import SqliteTable

from ..poset_wbools import WBools
from .posets import Poset


def warn_collision(a: Poset, b: Poset):
    warning = 'You found a hash collision! Please inform the developers of caph1993-posets.'
    try:
        file = './collision.log'
        info = dict(
            a_hash=a.hash,
            b_hash=b.hash,
            a_children=a.children,
            b_children=b.children,
        )
        with open(file, 'w') as f:
            json.dump(info, f, indent=2)
        warning += f'\nA log was written to {file}'
    finally:
        warnings.warn(warning)
    return


class PosetStore(SqliteTable):

    def __init__(self, file: Union[Path, str]):
        super().__init__(file, 'posets')
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS posets(
                hash integer PRIMARY KEY NOT NULL,
                children text NOT NULL,
                n integer NOT NULL,
                is_lattice boolean,
                is_distributive boolean,
                is_modular bool boolean,
                is_semimodular bool boolean
            )
        ''')
        self.db.execute('''
            CREATE INDEX IF NOT EXISTS posets_n ON posets (n)
        ''')

    def __getitem__(self, hash: int):
        poset = self.get_poset(hash=hash)
        if poset is None:
            raise KeyError(hash)
        return poset

    def get_poset(self, hash: int):
        poset, _ = self._get_poset(hash=hash)
        return poset

    def _get_poset(self, hash: int):
        data = self.get_dict(hash=hash)
        if data is None:
            return None, None
        return self._parse_data(data)

    def _parse_data(self, data):
        data.pop('hash')
        data.pop('n')
        children = json.loads(data.pop('children'))
        poset = Poset.from_children(children)
        for k, v in data.items():
            if v is not None:
                if k.startswith('is_'):
                    v = poset._wbool(bool(v))
                poset.__dict__[k] = v
        return poset, data

    table_columns = [
        'is_lattice',
        'is_distributive',
        'is_modular',
        'is_semimodular',
    ]

    def save_poset(self, poset: Poset):
        current, current_data = self._get_poset(hash(poset))
        data = {
            'n': poset.n,
            'children': json.dumps(poset.children),
            'hash': hash(poset),
        }
        for k in self.table_columns:
            if k in poset.__dict__:
                data[k] = bool(poset.__dict__[k])

        if current is not None and current_data is not None:
            if current != poset:
                warn_collision(current, poset)
            data = {**current_data, **data}
        self.update(data, hash=hash(poset))
        return hash(poset)

    def keys(self):
        return [s for s in self.column('hash')]

    def random_posets(self, limit: int):
        dicts = self.random_dicts(limit=limit)
        return [self._parse_data(data)[0] for data in dicts]

    def random_poset(self):
        return self.random_posets(1)[0]

    def filter(self, limit: int = None, **where):
        dicts = self.dicts(limit=limit, **where)
        return [self._parse_data(data)[0] for data in dicts]

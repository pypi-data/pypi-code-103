"""Meta information class."""

from typing import Optional

from . import Readable


class ReadableMeta(Readable):
    def __init__(self,
                 type: str,
                 subtype: Optional[str] = None,
                 **kwargs) -> None:
        super().__init__()
        self._type = type
        self._subtype = subtype
        self._dict = {'type': type}
        if self._subtype is not None:
            self._dict['subtype'] = self._subtype
        self._dict = dict(self._dict, **kwargs)

    @property
    def meta(self):
        return self._dict

    def to_json(self):
        content = self.content if hasattr(self, 'content') else ''
        return {'meta': self.meta, 'content': content}

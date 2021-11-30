from typing import Optional, TypedDict

from doutline import OutlineNode


class Metadata(TypedDict, total=False):
    body: Optional[str]
    css: Optional[str]
    outline: Optional[OutlineNode[str]]
    title: Optional[str]

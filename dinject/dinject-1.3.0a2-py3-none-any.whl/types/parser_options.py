from dataclasses import dataclass
from typing import Optional

from dinject.enums import Content, Host


@dataclass
class ParserOptions:
    force_content: Optional[Content] = None
    """
    None = default
    """

    force_host: Optional[Host] = None
    """
    None = default
    """

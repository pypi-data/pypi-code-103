import os
from pathlib import Path
from typing import Text, Optional

from pydantic import BaseModel

__all__ = ["StorageHandlerConfig"]


class StorageHandlerConfig(BaseModel):
    base_dir: Optional[Text] = os.path.join(Path.home(), ".cnside")
    _token_name: Optional[Text] = "token.json"

    @property
    def token_file_path(self):
        return os.path.join(self.base_dir, self._token_name)

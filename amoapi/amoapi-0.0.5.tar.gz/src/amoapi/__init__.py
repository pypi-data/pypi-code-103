import os
from pathlib import Path
from .interaction import BaseInteraction
from .tokens import TokenManager, FileTokensStorage
import logging
logger = logging.getLogger(__name__)

# load token manager
token_path = Path.cwd().resolve()

default_token_manager = TokenManager()
default_token_manager(
    client_id=os.environ.get("client_id"),
    client_secret=os.environ.get("client_secret"),
    subdomain=os.environ.get("subdomain"),
    redirect_url=os.environ.get("redirect_url"),
    storage=FileTokensStorage(token_path),  # by default FileTokensStorage
)
default_token_manager.init(code=os.environ.get("start_code"), skip_error=True)
amo_interaction = BaseInteraction(token_manager=default_token_manager)

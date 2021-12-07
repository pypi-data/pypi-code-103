import hmac
from datetime import datetime
from typing import Optional

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from .settings import PARAM, USE_PUBLIC_NAMESPACE, PUBLIC_NAMESPACE


class TitofistoStorage(FileSystemStorage):
    """Time-token secured variant of the base filesystem storage."""

    def url(self, name: str) -> str:
        """Compute URL for requested storage file."""
        # Get regular URL from base FileSystemStorage
        raw_url = super().url(name)

        if USE_PUBLIC_NAMESPACE:
            # Public files are accessible without a token
            if name.startswith(PUBLIC_NAMESPACE):
                return raw_url

        # Get token and timestamp
        token = self.get_token(name)

        # Generate full, token-secured URL
        full_url = f"{raw_url}?{PARAM}={token}"
        return full_url

    def get_token(self, name: str, ts: Optional[int] = None) -> str:
        """Get a token for a filename."""
        # Determine parts of the HMAC from the file
        if self.exists(name):
            mtime = self.get_modified_time(name).isoformat()
        else:
            mtime = datetime.now().isoformat()
        if ts is None:
            ts = int(datetime.now().strftime("%s"))
        full_msg = f"{name}//{mtime}@{ts}"

        # Calculate a HMAC with the parts
        token = hmac.new(
            bytes(settings.SECRET_KEY, "utf-8"), msg=bytes(full_msg, "utf-8"), digestmod="sha256"
        ).hexdigest() + hex(ts)[2:]
        return token

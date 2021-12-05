"""
    http connector
"""

import io
import requests

class HttpConnector:

    blob = None

    def get(self, ref):
        """Get Data"""
        if ref.startswith('http://') or ref.startsiwth('https://'):
            r = requests.get(ref)
            if r.status_code == 200:
                return dict(
                    url=ref,
                    _blob=io.StringIO(r.content)
                )

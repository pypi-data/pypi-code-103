import json
import time
import urllib.parse
from typing import Dict, Optional, Text

import requests
from pydantic import BaseModel

from cnside import errors
from cnside.cli.documents import AnalyzeRequestDoc, AnalyzeResponseDoc
from cnside.objects.encoders import CNSIDEJsonEncoder

__all__ = ["APIClient", "APIClientConfig"]


class APIClientConfig(BaseModel):
    base_url: Text
    headers: Optional[Dict] = {}
    proxies: Optional[Dict] = {}
    max_attempts: Optional[int] = 500


class APIClient:
    def __init__(self, config: APIClientConfig):
        self.config = config
        self.session = self.open()

    def open(self) -> requests.Session:
        s = requests.Session()
        s.headers.update(self.config.headers)
        s.proxies.update(self.config.proxies)
        return s

    def close(self):
        self.session.close()

    def request_packages_from_cnside_system(self, request_document: AnalyzeRequestDoc) -> bool:
        analyze_url = urllib.parse.urljoin(self.config.base_url, "analyze")

        rv = False

        response = self.session.post(url=analyze_url,
                                     json=json.loads(json.dumps(request_document, cls=CNSIDEJsonEncoder)))

        if response.status_code == 401:
            raise errors.api.TokenExpired()
        elif not response.status_code == 202:
            raise errors.api.RemoteServerError(data=errors.api.ServerErrorData(status_code=response.status_code))

        data = AnalyzeResponseDoc(**response.json())

        workflow_id = data.workflow_id
        attempts = 0
        while attempts < self.config.max_attempts:
            time.sleep(10)
            response = self.session.get(url=f"{analyze_url}/{workflow_id}")
            if response.status_code == 404:
                pass
            else:
                data = AnalyzeResponseDoc(**response.json())
                if data.status == "COMPLETED":
                    rv = data.accepted
                    return rv
                attempts += 1

        return rv

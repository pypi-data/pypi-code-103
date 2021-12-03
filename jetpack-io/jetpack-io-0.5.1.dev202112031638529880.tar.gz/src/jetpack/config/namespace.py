from typing import Optional


class NamespaceCache:
    def __init__(self) -> None:
        self.cache: Optional[str] = None

    def __call__(self) -> Optional[str]:
        if not self.cache:
            with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace") as f:
                self.cache = f.read().strip()
        return self.cache


get = NamespaceCache()

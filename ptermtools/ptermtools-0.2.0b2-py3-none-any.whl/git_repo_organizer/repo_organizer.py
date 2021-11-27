#!/usr/bin/env python3
import hashlib

import param

from ..config import CONFIG, _dealias_shortcut, _is_shortcut
from .database import RepoDB


class RepoOrganizer:
    pass


class Repo(param.Parameterized):
    repo_name = param.String(default=None)
    _id = param.String()
    url = param.String(allow_None=False)
    path = param.Foldername(default=None)
    projects = param.Selector()
    groups = param.Selector()

    def __init__(self, **params):
        super().__init__(**params)
        if self.repo_name == "":
            raise ValueError(
                "You must provide an argument url with an address or shortcut!"
            )
        if not self.repo_name:
            self.repo_name = self._determine_repo_name_from_url()
        if not self.path:
            self.path = self._determine_path_from_url()
        hash_name = f"{self.url}:{self.path}"
        self._id = hashlib.sha256(hash_name.encode()).hexdigest()

    @classmethod
    def from_db(cls, url):
        all_urls = RepoDB.objects(url=url)
        if len(all_urls) == 0:
            raise ValueError(f"Unknown {url}, not yet in DB!")
        if len(all_urls) == 1:
            return all_urls[0]
        if len(all_urls) > 1:
            raise ValueError("Too many urls!")

    def to_db(self, MONGO_CLIENT):
        pass

    def _determine_path_from_url(self):
        # http[s]://github.com/pgierz/dots --> github.com/pgierz/dots
        _, url_stub = self.url.split("://")
        return f"{CONFIG('CODE_DIR')}/{url_stub.replace('.git', '')}"

    def _determine_repo_name_from_url(self):
        repo_name = None
        protocol, url = self.url.split(":")
        if _is_shortcut(protocol):
            url = f"{_dealias_shortcut(protocol)}/{url}"
        repo_name = url.split("/")[-1].replace(".git", "")
        return repo_name

    def clone(self):
        pass

    def register(self):
        pass

from typing import TypedDict


class RepoDescription(TypedDict):
    """GitHub repo description from API."""

    stargazers_count: int

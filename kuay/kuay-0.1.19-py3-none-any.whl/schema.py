from typing import Optional
from .ward import *
from herre.access.model import GraphQLModel
from kuay.graphql.queries.whale import GET_WHALE


class GithubRepo(GraphQLModel):
    user: Optional[str]
    repo: Optional[str]
    branch: Optional[str]

    class Meta:
        identifier = "githubrepo"
        ward = "port"
        get = GET_WHALE


class Whale(GraphQLModel):
    githubrepo: Optional[GithubRepo]
    template: Optional[str]
    image: Optional[str]
    config: Optional[dict]

    class Meta:
        identifier = "whale"
        ward = "port"
        get = GET_WHALE

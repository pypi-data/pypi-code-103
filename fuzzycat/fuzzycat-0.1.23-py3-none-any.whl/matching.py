import collections
import logging
import os
import re
import sys
from multiprocessing.dummy import Pool
from typing import Any, List, Optional, Type, Union

import elasticsearch
import elasticsearch_dsl
import fatcat_openapi_client
import requests
from fatcat_openapi_client import (ContainerEntity, DefaultApi, ReleaseContrib, ReleaseEntity)
from fatcat_openapi_client.rest import ApiException

from fuzzycat.config import settings
from fuzzycat.contrib import (ContribListMatcher, FuzzyStringSimilarity, JaccardIndexThreshold,
                              Pipeline)
from fuzzycat.entities import entity_from_dict, entity_from_json
from fuzzycat.utils import es_compat_hits_total

FATCAT_API_URL = settings.get("FATCAT_API_URL", "https://api.fatcat.wiki/v0")


class FuzzyReleaseMatcher:
    """
    This is a helper class to fetch related documents to a given release
    document from fatcat search (currently elasticsearc)). Elasticsearch should
    rank similar documents high itself, so all we try to do here is to tweak
    the specific query a bit, depending on the completeness of the input
    document, e.g. if the input has contrib and title, then use both, if it
    only has a title, then use just that, etc.

    We try to get the result in a single query.

    TODO/Tweaks: e.g. if document do have a "release_year", add this as a "should" clause.
    """
    def __init__(self,
                 es="https://search.fatcat.wiki",
                 api=None,
                 index="fatcat_release",
                 size=10,
                 min_token_length=3,
                 release_year_padding=1):
        if isinstance(es, str):
            self.es = elasticsearch.Elasticsearch([es])
        else:
            self.es = es if es else elasticsearch.Elasticsearch()
        self.api = api if api else public_api(FATCAT_API_URL)
        self.index = index
        self.size = size
        self.logger = logging.getLogger("fuzzy")
        self.min_token_length = min_token_length
        self.release_year_padding = 1

    def _match_id(self, release: Optional[ReleaseEntity]) -> List[ReleaseEntity]:
        """
        Check for exact matches by identifier.
        """
        ext_ids = release.ext_ids
        attrs = (
            "doi",
            "pmid",
            "wikidata_qid",
            "core",
            "pmcid",
            "arxiv",
            "dblp",
            "doaj",
            "jstor",
            "isbn13",
            "ark",
            "mag",
            "oai",
        )
        for attr in attrs:
            value = getattr(ext_ids, attr)
            if not value:
                continue
            try:
                r = self.api.lookup_release(**{attr: value})
            except fatcat_openapi_client.rest.ApiException as err:
                if err.status in [404, 400]:
                    r = None
                else:
                    raise err
            if r:
                return [r]
        return []

    def _match_title_contrib(self, release: Optional[ReleaseEntity]) -> List[ReleaseEntity]:
        """
        Match in the presence of defined title and contrib fields.
        """
        contrib_tokens = [tok for c in release.contribs for tok in c.raw_name.split()]
        contrib_queries = [{
            "match": {
                "contrib_names": {
                    "query": token,
                }
            }
        } for token in contrib_tokens]
        query = {
            "bool": {
                "must": [
                    {
                        "match": {
                            "title": {
                                "query": release.title,
                                "operator": "AND",
                                "fuzziness": "AUTO",
                            },
                        }
                    },
                ] + contrib_queries,
            },
        }
        if release.release_year is not None:
            query["bool"]["must"].append({
                "range": {
                    "year": {
                        "gte": release.release_year - self.release_year_padding,
                        "lte": release.release_year + self.release_year_padding,
                        "boost": 0.5,
                    }
                }
            })
        result = []
        self.logger.info(query)
        resp = self.es.search(index=self.index,
                              body={
                                  "query": query,
                                  "size": self.size,
                                  "track_total_hits": True
                              })
        if es_compat_hits_total(resp) == 0:
            return result
        if es_compat_hits_total(resp) > self.size:
            self.logger.warning('too many hits: {}'.format(es_compat_hits_total(resp)))
        entities = response_to_entity_list(resp,
                                           entity_type=ReleaseEntity,
                                           size=self.size,
                                           api=self.api)
        return entities

    def _match_title(self, release: Optional[ReleaseEntity]) -> List[ReleaseEntity]:
        """
        Match in the presence of a title.
        """
        query = {
            "bool": {
                "must": [
                    {
                        "match": {
                            "title": {
                                "query": release.title,
                                "operator": "AND",
                                "fuzziness": "AUTO",
                            },
                        }
                    },
                ],
            },
        }
        if release.release_year is not None:
            query["bool"]["must"].append({
                "range": {
                    "year": {
                        "gte": release.release_year - self.release_year_padding,
                        "lte": release.release_year + self.release_year_padding,
                        "boost": 0.5,
                    }
                }
            })
        result = []
        resp = self.es.search(index=self.index,
                              body={
                                  "query": query,
                                  "size": self.size,
                                  "track_total_hits": True
                              })
        if es_compat_hits_total(resp) == 0:
            return result
        if es_compat_hits_total(resp) > self.size:
            self.logger.warning('too many hits: {}'.format(es_compat_hits_total(resp)))
        entities = response_to_entity_list(resp,
                                           entity_type=ReleaseEntity,
                                           size=self.size,
                                           api=self.api)
        return entities

    def _match_contribs(self, release: Optional[ReleaseEntity]) -> List[ReleaseEntity]:
        """
        Match in the presence of contribs (and no title).
        """
        contrib_tokens = [tok for c in release.contribs for tok in c.raw_name.split()]
        contrib_queries = [{
            "match": {
                "contrib_names": {
                    "query": token,
                }
            }
        } for token in contrib_tokens]
        query = {
            "bool": {
                "must": contrib_queries,
            },
        }
        if release.release_year is not None:
            query["bool"]["must"].append({
                "range": {
                    "year": {
                        "gte": release.release_year - self.release_year_padding,
                        "lte": release.release_year + self.release_year_padding,
                        "boost": 0.5,
                    }
                }
            })
        result = []
        resp = self.es.search(index=self.index,
                              body={
                                  "query": query,
                                  "size": self.size,
                                  "track_total_hits": True
                              })
        if es_compat_hits_total(resp) == 0:
            return result
        if es_compat_hits_total(resp) > self.size:
            self.logger.warning('too many hits: {}'.format(es_compat_hits_total(resp)))
        entities = response_to_entity_list(resp,
                                           entity_type=ReleaseEntity,
                                           size=self.size,
                                           api=self.api)
        return entities

    def _match_generic(self, release: Optional[ReleaseEntity]) -> List[ReleaseEntity]:
        """
        Throw tokens at elasticsearch.
        """
        token_queries = [
            {
                "match": {
                    "biblio": {  # https://git.io/JMXvJ
                        "query": token,
                    }
                }
            } for token in release_tokens(release) if len(token) > self.min_token_length
        ]
        query = {
            "bool": {
                "must": token_queries,
            },
        }
        if release.release_year is not None:
            query["bool"]["must"].append({
                "range": {
                    "year": {
                        "gte": release.release_year - self.release_year_padding,
                        "lte": release.release_year + self.release_year_padding,
                        "boost": 0.5,
                    }
                }
            })
        result = []
        self.logger.info(query)
        resp = self.es.search(index=self.index,
                              body={
                                  "query": query,
                                  "size": self.size,
                                  "track_total_hits": True
                              })
        if es_compat_hits_total(resp) == 0:
            return result
        if es_compat_hits_total(resp) > self.size:
            self.logger.warning('too many hits: {}'.format(es_compat_hits_total(resp)))
        entities = response_to_entity_list(resp,
                                           entity_type=ReleaseEntity,
                                           size=self.size,
                                           api=self.api)
        return entities

    def match(self, release: Optional[ReleaseEntity]) -> List[ReleaseEntity]:
        """
        Match dispatches methods based on which fields are defined on the
        document.
        """
        if not release:
            return []
        if release.ext_ids and len(release.ext_ids.to_dict()) > 0:
            result = self._match_id(release)
        if release.title is not None and release.contribs is not None:
            result = self._match_title_contrib(release)
        elif release.title is not None:
            result = self._match_title(release)
        elif release.contribs is not None:
            result = self._match_contribs(release)
        else:
            result = self._match_generic(release)

        return result


def public_api(host_uri):
    """
    Note: unlike the authenticated variant, this helper might get called even
    if the API isn't going to be used, so it's important that it doesn't try to
    actually connect to the API host or something.
    """
    conf = fatcat_openapi_client.Configuration()
    conf.host = host_uri
    return fatcat_openapi_client.DefaultApi(fatcat_openapi_client.ApiClient(conf))


def release_tokens(release: ReleaseEntity) -> List[str]:
    """
    Turn a release into a set of tokens.
    """
    tokens = []
    red = release.to_dict()
    for k, v in red.items():
        if v is None or k == "ext_ids":
            continue
        v = str(v)
        for tok in v.split():
            tokens.append(tok)
    for _, v in red.get("ext_ids", {}).items():
        if v is None or not isinstance(v, str):
            continue
        for tok in v.split():
            tokens.append(tok)

    return tokens


def test_release_tokens():
    Case = collections.namedtuple("Case", "re tokens")
    cases = (
        Case(entity_from_dict({"ext_ids": {}}, ReleaseEntity), []),
        Case(entity_from_dict({
            "ext_ids": {},
            "title": "Flow my tears"
        }, ReleaseEntity), ["Flow", "my", "tears"]),
        Case(
            entity_from_dict(
                {
                    "ext_ids": {},
                    "subtitle": "An illustrated guide",
                    "release_year": 1981,
                }, ReleaseEntity), ["An", "illustrated", "guide", "1981"]),
    )
    for c in cases:
        tokens = release_tokens(c.re)
        assert tokens == c.tokens


def fetch_release(ident, api=None):
    """
    Return release entity of None.
    """
    if api is None:
        api = public_api(FATCAT_API_URL)
    try:
        re = api.get_release(ident, hide="refs,abstracts", expand="container,contribs,files")
    except ApiException as exc:
        if exc.status == 404:
            print("[err] failed to retrieve release entity: {}".format(id), file=sys.stderr)
        else:
            print("[err] api failed with {}: {}".format(exc.status, exc.message), file=sys.stderr)
    else:
        return re


def retrieve_entity_list(
    ids: List[str],
    api: DefaultApi = None,
    entity_type: Union[Type[ReleaseEntity], Type[ContainerEntity]] = ReleaseEntity,
) -> List[Union[Type[ReleaseEntity], Type[ContainerEntity]]]:
    """
    Parallel requests.
    """
    if api is None:
        api = public_api(FATCAT_API_URL)

    result = []
    if entity_type == ReleaseEntity:
        with Pool(10) as p:
            result = p.map(fetch_release, ids)
        return [v for v in result if v is not None]
    else:
        raise ValueError("[err] cannot retrieve ids {} of type {}".format(ids, entity_type))

    return result


def retrieve_entity_list_sequential(
    ids: List[str],
    api: DefaultApi = None,
    entity_type: Union[Type[ReleaseEntity], Type[ContainerEntity]] = ReleaseEntity,
) -> List[Union[Type[ReleaseEntity], Type[ContainerEntity]]]:
    """
    Retrieve a list of entities. Some entities might be missing. Return all
    that are accessible.

    TODO: parallelize API access.
    """
    if api is None:
        api = public_api(FATCAT_API_URL)
    result = []
    if entity_type == ReleaseEntity:
        for id in ids:
            try:
                re = api.get_release(id, hide="refs,abstracts", expand="container,contribs,files")
                result.append(re)
            except ApiException as exc:
                if exc.status == 404:
                    print("[err] failed to retrieve release entity: {}".format(id), file=sys.stderr)
                else:
                    print("[err] api failed with {}: {}".format(exc.status, exc.message),
                          file=sys.stderr)
    elif entity_type == ContainerEntity:
        for id in ids:
            try:
                re = api.get_container(id)
                result.append(re)
            except ApiException as exc:
                if exc.status == 404:
                    print("[err] failed to retrieve container entity: {}".format(id),
                          file=sys.stderr)
                else:
                    print("[err] api failed with {}: {}".format(exc.status, exc.message),
                          file=sys.stderr)
    else:
        raise ValueError("[err] cannot retrieve ids {} of type {}".format(ids, entity_type))

    return result


def response_to_entity_list(response, size=5, entity_type=ReleaseEntity, api: DefaultApi = None):
    """
    Convert an elasticsearch result to a list of entities. Accepts both a
    dictionary and an elasticsearch_dsl.response.Response.

    We take the ids from elasticsearch and retrieve entities via API.
    """
    if isinstance(response, dict):
        ids = [hit["_source"]["ident"] for hit in response["hits"]["hits"]][:size]
        return retrieve_entity_list(ids, entity_type=entity_type, api=api)
    elif isinstance(response, elasticsearch_dsl.response.Response):
        ids = [hit.to_dict().get("ident") for hit in response]
        return retrieve_entity_list(ids, entity_type=entity_type, api=api)
    else:
        raise ValueError("cannot convert {}".format(response))


def anything_to_entity(
    s: str,
    entity_type: Union[Type[ContainerEntity], Type[ReleaseEntity]],
    api_url: str = "https://api.fatcat.wiki/v0",
    es_url: str = "https://search.fatcat.wiki",
) -> Union[ContainerEntity, ReleaseEntity]:
    """
    Convert a string to a given entity type. This function may go out to the
    fatcat API or elasticsearch and hence is expensive.
    """
    names = {
        ContainerEntity: "container",
        ReleaseEntity: "release",
    }
    if not entity_type in names:
        raise ValueError("cannot convert {}, only: {}".format(entity_type, names.keys()))
    entity_name = names[entity_type]

    if s is None:
        raise ValueError("no entity found")

    if os.path.exists(s):
        with open(s) as f:
            return entity_from_json(f.read(), entity_type)

    match = re.search("/?([a-z0-9]{26})$", s)
    if match:
        url = "{}/{}/{}".format(api_url, entity_name, match.group(1))
        resp = requests.get(url)
        if resp.status_code == 200:
            return entity_from_json(resp.text, entity_type)
        if resp.status_code == 404:
            raise ValueError("entity not found: {}".format(url))

    if re.match("[0-9]{4}(-)?[0-9]{3,3}[0-9xx]", s):
        # TODO: make index name configurable
        url = "{}/fatcat_{}/_search?track_total_hits=true&q=issns:{}".format(es_url, entity_name, s)
        doc = requests.get(url).json()
        if es_compat_hits_total(resp) == 1:
            ident = doc["hits"]["hits"][0]["_source"]["ident"]
            url = "{}/{}/{}".format(api_url, entity_name, ident)
            return entity_from_json(requests.get(url).text, entity_type)

    if entity_name == "container":
        return entity_from_dict({"name": s}, entity_type)
    elif entity_name == "release":
        return entity_from_dict({"title": s, "ext_ids": {}}, entity_type)
    else:
        raise ValueError("unhandled entity type: {}".format(entity_type))

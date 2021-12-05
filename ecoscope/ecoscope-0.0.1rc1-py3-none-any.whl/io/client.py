import asyncio
import copy
import datetime
import logging
import math
import pprint
import types

import aiohttp
import backoff
import pandas
from dasclient import dasclient

list_errors = []
logger = logging.getLogger(__name__)


def exception_wrapper(func):
    """A wrapper that handles exception by returning a logger."""

    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except dasclient.DasClientNotFound:
            logger.error(f"404 (NotFound)")
        except Exception as exc:
            logger.exception(exc)
            return

    return inner


def backoff_wrapper(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except aiohttp.ContentTypeError as exc:
            list_errors.append(str(exc))
            return empty_dict()
        except Exception as exc:
            list_errors.append(str(exc))
            return empty_dict()

    return wrapper


def empty_dict():
    yield {}


class EarthRangerClient(dasclient.DasClient):

    def __init__(self,
                 er_server: str,
                 username: str,
                 password: str,
                 provider_key: str = '',
                 client_id: str = 'das_web_client'):
        """initialize the earthranger client"""
        root = '/'.join([er_server, 'api/v1.0'])
        token_url = '/'.join([er_server, 'oauth2/token'])

        super().__init__(username=username,
                         password=password,
                         service_root=root,
                         token_url=token_url,
                         provider_key=provider_key,
                         client_id=client_id)
        pprint.pprint(self.pulse())

    @exception_wrapper
    def _get(self, path, stream=False, **kwargs):
        return super(EarthRangerClient, self)._get(path, stream, **kwargs)

    def get_eventtypes(self, include_inactive=True):
        """Gets the eventtypes"""
        return self._get(f'activity/events/eventtypes?include_inactive={include_inactive}')


class AsyncEarthRangerClient:
    """Asynchronous EarthRanger Client"""

    def __init__(self, er_client):
        self.client = er_client
        self.service_root = er_client.service_root

    def _earthranger_url(self, path):
        return '/'.join((self.service_root, path))

    @staticmethod
    def _yield_results(results):
        for r in results:
            yield r

    @staticmethod
    def _paginate(params, page):
        p = copy.deepcopy(params)
        p['page'] = page
        return p

    @staticmethod
    def _page_counts(result):
        if isinstance(result, types.GeneratorType):
            logger.error("PageCountError: Unable to get page count.")
            return 0
        else:
            return int(result.get('count'))

    @backoff_wrapper
    @backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=10)
    async def _get_method(self, session, urlpath, params=None, with_count=False):
        async with session.get(urlpath, params=params) as response:
            json_data = await response.json()
            return self._yield_results(json_data['data']['results']) if not with_count else json_data['data']

    async def _future_objects(self, session, urlpath, params, page_size):

        rs = await self._get_method(session, urlpath, self._paginate(params, 1), with_count=True)
        rs_count = self._page_counts(rs)
        total_pages = math.ceil(rs_count / page_size)

        params['page_size'] = page_size
        return [asyncio.ensure_future(
            self._get_method(session,
                             urlpath,
                             self._paginate(params, page))) for page in range(1, total_pages + 1)]

    async def get_subject_observations(self,
                                       subject_id,
                                       start=None,
                                       end=None,
                                       filter_flag=0,
                                       include_details=True,
                                       page_size=4000,
                                       count=None,
                                       limit=0,
                                       ):

        connector = aiohttp.TCPConnector(limit=limit)
        async with aiohttp.ClientSession(headers=self.client.auth_headers(), connector=connector) as session:
            params = {}
            page_size = min(page_size, 4000)  # Max page_size supported is 4000
            urlpath = self._earthranger_url('observations')

            if start is not None and isinstance(start, datetime.datetime):
                params['since'] = start.isoformat()
            if end is not None and isinstance(end, datetime.datetime):
                params['until'] = end.isoformat()
            if subject_id:
                params['subject_id'] = subject_id
            else:
                raise ValueError('subject_id or source_id missing')

            params['filter'] = 'null' if filter_flag is None else filter_flag
            params['include_details'] = str(include_details)
            params['page_size'] = 1

            rs = await self._get_method(session, urlpath, self._paginate(params, 1), with_count=True)
            rs_count = self._page_counts(rs)
            total_pages = math.ceil(rs_count / page_size)
            count.append(rs_count)

            params['page_size'] = page_size

            tasks = [asyncio.ensure_future(
                self._get_method(session, urlpath, self._paginate(params, page))) for page in range(1, total_pages + 1)]
            return await asyncio.gather(*tasks)

    async def get_subjectsources(self, subjects, sources, page_size):
        async with aiohttp.ClientSession(headers=self.client.auth_headers()) as session:
            params = {}
            page_size = min(page_size, 4000)  # Max page_size supported is 4000
            urlpath = self._earthranger_url('subjectsources')

            params['subjects'] = subjects
            params['sources'] = sources
            params['page_size'] = 1

            tasks = await self._future_objects(session=session, urlpath=urlpath, page_size=page_size, params=params)
            return await asyncio.gather(*tasks)

    async def get_events(self, page_size, **kwargs):
        async with aiohttp.ClientSession(headers=self.client.auth_headers()) as session:
            params = {k: v for k, v in kwargs.items() if
                      k in ['state', 'event_type',
                            'filter', 'include_notes',
                            'include_related_events',
                            'include_files', 'include_details',
                            'include_updates', 'max_results', 'oldest_update_date']}
            page_size = min(page_size, 4000)  # Max page_size supported is 4000
            urlpath = self._earthranger_url('activity/events')

            tasks = await self._future_objects(session=session, urlpath=urlpath, page_size=page_size, params=params)
            return await asyncio.gather(*tasks)

    @staticmethod
    def yield_sources(results):
        yield results['data']

    @backoff_wrapper
    @backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=10)
    async def _get2_method(self, session, urlpath, params=None):
        async with session.get(urlpath, params=params) as response:
            json_data = await response.json()
            return self.yield_sources(json_data)

    async def get_sources(self, sources):
        """Temporary solution """
        async with aiohttp.ClientSession(headers=self.client.auth_headers()) as session:
            urlpath = self._earthranger_url('source/{}')
            tasks = [asyncio.ensure_future(self._get2_method(session, urlpath.format(source_id)))
                     for source_id in sources if not pandas.isnull(source_id)]
            return await asyncio.gather(*tasks)


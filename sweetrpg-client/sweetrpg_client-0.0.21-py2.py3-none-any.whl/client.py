# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""Client.
"""

import logging
import requests
from sweetrpg_client import constants
from sweetrpg_client.exceptions import *
from sweetrpg_client.types import *
from sweetrpg_client.types.registry import _types
from sweetrpg_model_core.model.base import Model
from jsonapi_client import Session
from sweetrpg_client.helpers import _flatten_object


class Client(object):
    """

    """

    def __init__(self, base_url: str, access_token: str = None, register_default_types: bool = True):
        """Create a new client instance using the provided base URL for the API endpoint. An optional
        access token may be provided.

        :param str base_url: The base URL of the API service. Paths will be appended for the appropriate
        type when the request is executed.
        :param str access_token: A bearer access token to use for endpoints that may require it.
        :param bool register_default_types: The client package comes with a number of types ready to use
        that will be registered automatically if this value is `True`. Set this to `False` if you don't want
        those types registered.
        """
        self.base_url = base_url
        self.access_token = access_token
        self.data_types = {}
        if register_default_types:
            for k, v in _types.items():
                self.register_type(k, v)

    def register_type(self, name: str, type_info: dict):
        """

        :param str name:
        :param dict type_info:
        :return None:
        """
        self.data_types[name] = type_info

    def get(self, data_type: str, id: str) -> Model:
        """

        :param str data_type:
        :param str id:
        :return Model:
        """
        logging.debug("Fetching data type %s ID %s...", data_type, id)

        type_info = self.data_types.get(data_type)
        logging.debug("type_info: %s", type_info)
        if not type_info:
            raise UnknownDataType(data_type)

        path = type_info[constants.ENDPOINT_PATH]
        logging.debug("path: %s", path)
        # url = f"{self.base_url}/{path}/{id}"
        # logging.debug("url: %s", url)
        headers = {}
        if self.access_token:
            logging.debug("adding access token to request headers")
            headers['Authorization'] = f"Bearer {self.access_token}"

        request_args = {
            'headers': headers,
            # 'params': params,
        }

        logging.info("Sending request to %s...", self.base_url)

        with Session(self.base_url, request_kwargs=request_args) as s:
            result = s.get(path, id)
            if data_type != result.resource.type:
                raise InvalidResponseData(path, 'type', data_type, f"Response data type {result.resource.type} does not match expected type: {data_type}")
            if result.resource.id != id:
                raise InvalidResponseData(path, 'object-id', f"{data_type}:{id}", f"Response data ID {result.resource.id} does not match expected ID: {id}")

            flat_obj = _flatten_object(result.resource)
            obj_class = type_info[constants.OBJECT_CLASS]
            logging.debug("obj_class: %s", obj_class)
            obj = obj_class(**flat_obj)
            logging.debug("obj: %s", obj)
            return obj

    def query(self, data_type: str, page: int = 0, limit: int = constants.DEFAULT_PAGE_SIZE) -> list:
        """

        :param str data_type:
        :param page:
        :param limit:
        :return list[Model]:
        """
        logging.debug("Querying for data type %s, page %d, limit %d...", data_type, page, limit)

        type_info = self.data_types.get(data_type)
        logging.debug("type_info: %s", type_info)
        if not type_info:
            raise UnknownDataType(data_type)

        path = type_info[constants.ENDPOINT_PATH]
        logging.debug("path: %s", path)
        # url = f"{self.base_url}/{path}/"
        # logging.debug("url: %s", url)
        headers = {}
        if self.access_token:
            logging.debug("adding access token to request headers")
            headers['Authorization'] = f"Bearer {self.access_token}"
        params = {}
        if page > 0:
            params[constants.PAGE_PARAM] = page
        if limit != constants.DEFAULT_PAGE_SIZE:
            params[constants.LIMIT_PARAM] = min(max(limit, 1), constants.MAX_PAGE_SIZE)

        request_args = {
            'headers': headers,
            'params': params,
        }

        logging.info("Sending request to %s...", self.base_url)

        with Session(self.base_url, request_kwargs=request_args) as s:
            result = s.get(path)
            # if data_type != result.resource.type:
            #     raise InvalidResponseData(path, 'type', data_type, f"Response data type {result.resource.type} does not match expected type: {data_type}")
            # if result.resource.id != id:
            #     raise InvalidResponseData(path, 'object-id', f"{data_type}:{id}", f"Response data ID {result.resource.id} does not match expected ID: {id}")

            flat_objs = list(map(_flatten_object, result.resources))
            obj_class = type_info[constants.OBJECT_CLASS]
            logging.debug("obj_class: %s", obj_class)
            objs = list(map(lambda o: obj_class(**o), flat_objs))
            logging.debug("objs: %s", objs)
            return objs

        # r = requests.get(url, headers=headers, params=params)
        # logging.debug("r: %s", r)
        # if r.status_code == 200:
        #     schema_class = type_info[constants.API_SCHEMA_CLASS]
        #     logging.debug("schema_class: %s", schema_class)
        #     schema = schema_class()
        #     objs = []
        #     j = r.json()
        #     # for obj_data in j['data']:
        #     objs = schema.load(j, many=True)
        #     # logging.debug("obj: %s", obj)
        #     # objs.append(obj)
        #
        #     logging.debug("objs: %s", objs)
        #     return objs
        # elif r.status_code == 404:
        #     raise NotFound(url)
        #
        # raise UnexpectedResponse(url, r.status_code, r.text)

    def update(self, data_type: str, id: str, update: dict) -> Model:
        """

        :param data_type:
        :param id:
        :param update:
        :return:
        """
        return None

    def delete(self, data_type: str, id: str) -> bool:
        """

        :param data_type:
        :param id:
        :return:
        """
        return False

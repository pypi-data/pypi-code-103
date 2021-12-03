import abc
import json
import io
from requests.auth import AuthBase
from typing import List, Optional
from defusedxml import ElementTree
from defusedxml.ElementTree import ParseError
from drb import AbstractNode
from drb.predicat import Predicate
from drb.exceptions import DrbException
from drb_impl_http import DrbHttpNode

from .exceptions import OdataRequestException


class OdataNode(AbstractNode, abc.ABC):
    """
    Common ODataNode interface
    """

    def __init__(self, service_url, auth: AuthBase = None):
        self._service_url = service_url
        self._auth = auth

    def get_service_url(self) -> str:
        """
        Returns URL of the OData service.
        :returns: string URL representation the OData service
        :rtype: str
        """
        return self._service_url

    def get_auth(self) -> Optional[AuthBase]:
        """
        Returns the associated authentication required to access to the OData
        service.
        :returns: an authentication compatible with requests library.
        :rtype: AuthBase
        """
        return self._auth

    def __eq__(self, other):
        return isinstance(other, OdataNode) and \
            self._service_url == other._service_url


def http_node_to_json(node: DrbHttpNode) -> dict:
    try:
        with node.get_impl(io.BytesIO) as stream:
            data = json.load(stream)
            if 'error' in data.keys():
                raise OdataRequestException(str(data['error']))
            return data
    except json.JSONDecodeError:
        raise OdataRequestException(f'Invalid json from {node.path.name}')
    except DrbException:
        raise OdataRequestException(f'Invalid node: {type(node)}')


def is_csc_odata_svc(service_url: str, auth: AuthBase = None) -> bool:
    """
    Check if the given URL is an OData CSC service.
    :param service_url: service URL
    :type service_url: str
    :param auth: (optional) authentication mechanism required by the service
    :param auth: AuthBase
    :returns: True if the given URL is an OData CSC service.
    :rtype: bool
    """
    try:
        url = f'{service_url}/$metadata'
        node = DrbHttpNode(url, auth=auth)
        tree = ElementTree.parse(node.get_impl(io.BytesIO))
        ns = tree.getroot()[0][0].get('Namespace', None)
        return 'OData.CSC' == ns
    except (DrbException, ParseError):
        return False


def req_svc(odata: OdataNode) -> dict:
    node = DrbHttpNode(odata.get_service_url(), auth=odata.get_auth(),
                       params={'$format': 'json'})
    data = http_node_to_json(node)
    return data


def req_svc_count(odata: OdataNode) -> int:
    url = f'{odata.get_service_url()}/Products/$count'
    node = DrbHttpNode(url, auth=odata.get_auth())
    stream = node.get_impl(io.BytesIO)
    value = stream.read().decode()
    stream.close()
    return int(value)


def req_svc_products(odata: OdataNode, **kwargs) -> list:
    params = {'$format': 'json'}
    if 'filter' in kwargs.keys() and kwargs['filter'] is not None:
        params['$filter'] = kwargs['filter']
    if 'order' in kwargs.keys() and kwargs['order'] is not None:
        params['$orderby'] = kwargs['order']
    if 'skip' in kwargs.keys() and kwargs['skip'] is not None:
        params['$skip'] = kwargs['skip']
    if 'top' in kwargs.keys() and kwargs['top'] is not None:
        params['$top'] = kwargs['top']

    url = f'{odata.get_service_url()}/Products'
    node = DrbHttpNode(url, auth=odata.get_auth(), params=params)
    data = http_node_to_json(node)
    return data['value']


def req_product_by_uuid(odata: OdataNode, prd_uuid: str) -> dict:
    url = f'{odata.get_service_url()}/Products({prd_uuid})'
    params = {'$format': 'json'}
    node = DrbHttpNode(url, auth=odata.get_auth(), params=params)
    return {
        k: v for k, v in http_node_to_json(node).items()
        if not k.startswith('@odata.')
    }


def req_product_by_name(odata: OdataNode, prd_name: str) -> List[dict]:
    url = f'{odata.get_service_url()}/Products'
    params = {
        '$format': 'json',
        '$filter': f"Name%20eq%20'{prd_name}'"
    }
    node = DrbHttpNode(url, auth=odata.get_auth(), params=params)
    data = http_node_to_json(node)
    if len(data['value']) > 0:
        return data['value']
    raise OdataRequestException(f'No product named {prd_name} found')


def req_product_attributes(odata: OdataNode, prd_uuid: str) -> List[dict]:
    url = f'{odata.get_service_url()}/Products({prd_uuid})/Attributes'
    params = {'$format': 'json'}
    node = DrbHttpNode(url, auth=odata.get_auth(), params=params)
    data = http_node_to_json(node)
    return data['value']


def req_product_download(odata: OdataNode, prd_uuid: str) -> io.BytesIO:
    url = f'{odata.get_service_url()}/Products({prd_uuid}/$value'
    node = DrbHttpNode(url, auth=odata.get_auth())
    return node.get_impl(io.BytesIO)


class ODataCustomQuery(Predicate):
    """This Predicate allows to customize the OData query request."""

    def __init__(self, **kwargs):
        """
        ODataCustomQuery constructor

        :key filter: OData query filter
        :key order: OData query orderby
        :key skip: OData query skip
        :key top: ODate query top
        """
        self.__filter = kwargs['filter'] if 'filter' in kwargs.keys() else None
        self.__order = kwargs['order'] if 'order' in kwargs.keys() else None
        self.__skip = kwargs['skip'] if 'skip' in kwargs.keys() else None
        self.__top = kwargs['top'] if 'top' in kwargs.keys() else None

    def matches(self, key) -> bool:
        return False

    def apply_query(self, node: OdataNode) -> List[dict]:
        """
        Performs the request with specific given query parameters.

        :param node: OData service on which perform the request.
        :type node: OdataNode
        :returns: list of dictionary (JSON OData response)
        :rtype: list
        """
        return req_svc_products(node, filter=self.__filter, order=self.__order,
                                skip=self.__skip, top=self.__top)

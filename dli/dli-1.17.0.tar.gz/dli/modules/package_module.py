#
# Copyright (C) 2020 IHS Markit.
# All Rights Reserved
#
import re
from collections import OrderedDict
from typing import Optional, Union, List
import requests

from dli.models.package_model import PackageModel

from platform_services_lib.lib.services.exceptions import CatalogueEntityNotFoundException
from platform_services_lib.lib.adapters.pagination_adapters import Paginator
from platform_services_lib.lib.context.urls import package_urls


class PackageModule:
    """
    This class is bound to the client and can not be initalised
    directly.

    It is accessed by:

    .. code:: python

        client.packages

    """

    @staticmethod
    def _search_terms_to_filters(search_terms, start_count):

        def to_dict(k, op, v):
            return {'key': k.strip(), 'op': op.strip(), 'val': v.strip()}

        def partition_search_term(x):
            split = re.split("(<|>|=>|<=|=|!=| contains | like | ilike )", x)
            if len(split) == 3:
                return to_dict(*split)
            else:
                return None

        arguments = map(partition_search_term, search_terms)
        enumerated_partitions = [
            (x, y) for x, y in enumerate(arguments, start=start_count)
            if y is not None
        ]
        opmp = {
            "=": "eq",
            ">=": "gte",
            "<=": "lte",
            ">": "gt",
            "<": "lt",
        }

        to_numbered_filter = lambda partition: (lambda idx, x: {
            f'filter[{idx}][field]': x['key'],
            f'filter[{idx}][operator]': opmp.get(x['op'], x['op']),
            f'filter[{idx}][value]': x['val']

        })(*partition)

        yield from map(to_numbered_filter, enumerated_partitions)

    @staticmethod
    def _filter_creation(search_term, only_mine):
        bump = 0
        if only_mine:
            yield {
                'filter[0][value]': True,
                'filter[0][operator]': 'eq',
                'filter[0][field]': 'has_access',
            }
            bump = 1
        else:
            yield {}

        if type(search_term) is str:
            search_term = [search_term]

        if search_term and type(search_term) is list:
            yield from PackageModule._search_terms_to_filters(search_term, bump)

    def __call__(
        self, search_term: Optional[Union[str, List[str]]]=None,
        only_mine: Optional[bool]=False, page_size=5000
    ) -> 'OrderedDict[str, PackageModel]':
        """ 

        Find packages. Synonymous with .find().

        
        :Example:

            Get all packages:

            .. code:: python

                client.packages()

        :Example:

            Get **only** packages you have access to and
            can read the datasets of:

            .. code:: python

                client.packages(only_mine=True)

        :Example:

            Search for packages using `ilike`. This will find fields that are
            similar to value. This is recommended over using `like` as it
            performs case insensitive matching.

            Some examples of how the `ilike` logic matches in the database
            when there is a dataset named `example`:

            'example' ILIKE 'example'    true

            'example' ILIKE 'ex%'     true

            'example' ILIKE 'c'      false

            Example usage in the DLI:

            .. code:: python

                # Exact match `example` (case sensitive).
                client.packages(search_term='name=example')

                # Match `example` (case insensitive).
                client.packages(search_term='name ilike example')

                # Match `example` (case insensitive) followed by any characters.
                client.packages(search_term='name ilike example%')

                # Match `example` (case insensitive) in the middle of any characters.
                client.packages(search_term='name ilike %example%')

        :Example:

            Search for packages with multiple search terms:

            .. code:: python

                client.packages(
                    search_term=[
                        'name=example',
                        'manager_id=example'
                    ]
                )

        :Example:

            Search for packages with name and only_mine:

            .. code:: python

                client.packages(
                    search_term='name=example',
                    only_mine=True,
                )


        :param search_term: search term for package. Can filter using a simple
            query language. E.G "field=value", "field>value", "field ilike value".
            Can pass in multiple values using a list of strings.

        :param only_mine: Specify whether to collect packages only
            accessible to you (user) or to discover packages that you may
            want to discover. Set to True searches and returns only those
            packages which you also have access to and also match the
            search_term conditions. Set to false (default) searches and
            returns all packages matching the search_term conditions.

        :param int page_size: Optional. Default 5000. Used to control the size of internal calls from the SDK to the Catalogue.
            This parameter is only exposed to allow performance testing and changes for batch jobs.
            Customers should use the default setting.

        :returns: A dictionary containing named entries matching the search_term values and parameters mapping to the accompanying PackageModel which represents it
        :rtype: OrderedDict[str, PackageModel]

        .. seealso::

            :ref:`Package Attributes <package-attributes>`
                Definition of a Package, and what fields you can filter on (all fields labeled as "dynamic".

        """

        # search_term = ["y=z", "a>c", "d", "f contains pull", "f ilike pig"]
        filters = {}
        for x in PackageModule._filter_creation(search_term, only_mine):
            filters.update(x)

        search_paginator = Paginator(
            package_urls.v2_package_index,
            self._client._Package,
            self._client._Package._from_v2_response_unsheathed,
            page_size=5000,
            filters=filters
        )

        return OrderedDict([(v.name, v) for v in search_paginator])

    def find(self, search_term: Optional[Union[str, List[str]]]=None,
        only_mine: Optional[bool]=False, page_size=5000
    ) -> 'OrderedDict[str, PackageModel]':
        """

        Find packages matching search terms and whether to only find package which you can access.


        :Example:

            Get all packages:

            .. code:: python

                client.packages.find()

        :Example:

            Get **only** packages you have access to and
            can read the datasets of:

            .. code:: python

                client.packages.find(only_mine=True)

        :Example:

            Search for packages using `ilike`. This will find fields that are
            similar to value. This is recommended over using `like` as it
            performs case insensitive matching.

            Some examples of how the `ilike` logic matches in the database
            when there is a dataset named `example`:

            'example' ILIKE 'example'    true

            'example' ILIKE 'ex%'     true

            'example' ILIKE 'c'      false

            Example usage in the DLI:

            .. code:: python

                # Exact match `example` (case sensitive).
                client.packages.find(search_term='name=example')

                # Match `example` (case insensitive).
                client.packages.find(search_term='name ilike example')

                # Match `example` (case insensitive) followed by any characters.
                client.packages.find(search_term='name ilike example%')

                # Match `example` (case insensitive) in the middle of any characters.
                client.packages.find(search_term='name ilike %example%')

        :Example:

            Search for packages with multiple search terms:

            .. code:: python

                client.packages.find(
                    search_term=[
                        'name=example',
                        'manager_id=example'
                    ]
                )

        :Example:

            Search for packages with name and only_mine:

            .. code:: python

                client.packages.find(
                    search_term='name=example',
                    only_mine=True,
                )


        :param search_term: search term for package. Can filter using a simple
            query language. E.G "field=value", "field>value", "field ilike value".
            Can pass in multiple values using a list of strings.

        :param only_mine: Specify whether to collect packages only
            accessible to you (user) or to discover packages that you may
            want to discover. Set to True searches and returns only those
            packages which you also have access to and also match the
            search_term conditions. Set to false (default) searches and
            returns all packages matching the search_term conditions.

        :param int page_size: Optional. Default 5000. Used to control the size of internal calls from the SDK to the Catalogue.
            This parameter is only exposed to allow performance testing and changes for batch jobs.
            Customers should use the default setting.

        :returns: A dictionary containing named entries matching the search_term values and parameters mapping to the accompanying PackageModel which represents it
        :rtype: OrderedDict[str, PackageModel]

        .. seealso::

            :ref:`Package Attributes <package-attributes>`
                Definition of a Package, and what fields you can filter on (all fields labeled as "dynamic".

        """

        return self.__call__(search_term, only_mine, page_size)


    def get(self, name: str) -> PackageModel:
        """
        Find a PackageModel with the matching name. If not found then
        returns None.

        :param name: The name of the package to
            collect (short codes are yet to be implemented for packages)

        :Example:

            Search for packages with multiple search terms:

            .. code:: python

                # NOTE: this will break in future when package
                # short codes supersede names. Use at your own
                # risk.
                client.package.get('package name')

        """

        # NOTA BENE - this is commented out until such a time that package shortcodes are being implemented
        # THE BELOW MESSAGE SHOULD THEN BE SHOWN UNTIL SUCH A TIME THAT EVERYONE HAS UPGRADED TO AT LEAST
        # THE FIRST RELEASE VERSION WHICH AGAIN SHOWS IT.
        # warnings.warn(
        #     'Getting a package by name'
        #     'will be deprecated in future. Short-codes will replace this.',
        #     PendingDeprecationWarning
        # )

        res = self._client.packages(search_term=[f"name={name}"]).get(name)
        if res:
            return res
        else:
            if self._client.strict:
                r = requests.Response()
                r.status_code = 404
                r.request = (lambda: True)
                r.request.method = f"No such package {name}"
                r.request.url = ""
                raise CatalogueEntityNotFoundException(
                    message=f"No such package {name}",
                    response=r
                )
            else:
                return None
#
# Copyright (C) 2020 IHS Markit.
# All Rights Reserved
#
import textwrap
from collections import OrderedDict
from typing import Dict

import dli.models
from dli.models.dataset_model import DatasetModel

from platform_services_lib.lib.adapters.pagination_adapters import Paginator
from platform_services_lib.lib.services.dlc_attributes_dict import AttributesDict
from platform_services_lib.lib.context.urls import package_urls


class PackageModel(AttributesDict):
    """
    Represents a package
    """

    @classmethod
    def _from_v2_response_unsheathed(cls, response_json, page_size=None):
        """

        :param response_json:
        :param page_size: Unused value, added to keep the same interface as
        datasetModel's _from_v2_response_unsheathed.
        :return:
        """

        return cls({
            'data': response_json
        })

    def __init__(self, json):
        # We have to declare the attribute `documentation` because it is
        # referenced in the code of this class. This means that there will
        # be an `documentation` attribute even when there is zero
        # `documentation` attribute in the Catalogue response JSON.
        self.documentation = None
        self.__shape = None

        # Maintain compatibility between V1 (which had package_id) and V2
        # (which only has ID).
        if 'package_id' not in json['data']['attributes']:
            json['data']['attributes']['package_id'] = json['data']['id']

        super().__init__(id=json['data']['id'], **json['data']['attributes'])
        self._paginator = Paginator(
            package_urls.v2_package_datasets.format(id=self.id),
            self._client._DatasetFactory,
            self._client._DatasetFactory._from_v2_response_unsheathed
        )

    @property
    def shape(self):
        """
        :returns: The number of datasets within this package
        :rtype: Int
        """
        if self.__shape is None:
            self.__shape = len(self.datasets())
        return self.__shape

    def datasets(self) -> Dict[str, DatasetModel]:
        """
        :returns: Dictionary of datasets shortcodes mapping to the model of the respective dataset, for each in the package.
        :rtype: OrderedDict[id: str, dli.models.dataset_model.DatasetModel]
        """
        return OrderedDict([
            (v.short_code, v) for v in self._paginator
        ])

    def contents(self):
        """Print each of the datasets in this package.

          :Example:

            .. code:: python

                >>> p1 = client.packages.get('example')
                >>> p1.contents()

                DATASET "Paint Colours Palettes" [PARQUET]
                >> Shortcode: PaintColours
                >> Available Date Range: 2020-05-13 to 2020-05-13
                >> ID: 804002d8-2466-4303-a470-3cb73f6def77
                >> Published: Monthly by Dulux Paints
                >> Accessible: True

                This dataset lists the in vogue colour palettes

                --------------------------------------------------------------------------------
                DATASET "Furniture Inventory" [CSV]
                >> Shortcode: FurnitureInventory
                >> Available Date Range: 2012-01-13 to 2020-05-13
                >> ID: 804002d8-2466-4303-a470-3cb73f6aaab7
                >> Published: Daily by Furniture 4 You
                >> Accessible: True

                This dataset lists the currently in-stock furniture available to be purchase
                from the wholesaler for decorators and designers

                --------------------------------------------------------------------------------
        """
        for p in self.datasets().items():
            print(str(p[1]))

    def metadata(self):
        """
        Once you have selected a package, you can print the metadata
        (the available fields and values). These are the attributes and their values for this package as listed on this page

        :example:

            .. code-block:: python

                # Get all packages with a name containing the text 'example package'. Filtering
                # is done on the server side.
                >>> packages = client.packages('example package')
                # Get metadata of the 'example package' package.
                >>> packages['example package'].metadata()

        :return: Prints the metadata (attributes) keys and values.
        """
        dli.models.print_model_metadata(self)

    def __str__(self):
        separator = "-"*80
        split_description = "\n".join(textwrap.wrap(self.description, 80))
        split_keywords = "\n".join(self.keywords or [])

        # documentation is not guaranteed to be available
        split_documentation = 'No documentation available.'
        if self.documentation is not None:
            split_documentation = "\n".join(textwrap.wrap(self.documentation, 80))

        # When the fields are re-named in the JSON, it breaks our mapping. Use
        #   return str(self.__dict__)
        # to get the new field names then update the below.
        return f"\nPACKAGE \"{self.name}\" " \
               f"(Contains: {self.shape} datasets)\n" \
               f">> ID: {self.id} \n" \
               f">> Accessible: {self.has_access}\n" \
               f"\n" \
               f"{split_description}\n" \
               f"Documentation: {split_documentation}\n\n" \
               f"Keywords:\n{split_keywords}\n" \
               f"{separator}"

    def __repr__(self):
        return f'<Package name={self.name}>'

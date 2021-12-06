#
# Copyright (C) 2020 IHS Markit.
# All Rights Reserved
#
import logging
import warnings

from deprecated.sphinx import deprecated

from platform_services_lib.lib.aspects.base_component import BaseComponent
from platform_services_lib.lib.context.urls import package_urls

logger = logging.getLogger(__name__)


class Package(BaseComponent):

    _KNOWN_FIELDS = {"name",
                     "description",
                     "keywords",
                     "topic",
                     "access",
                     "internalData",
                     "contractIds",
                     "termsAndConditions",
                     "derivedDataNotes",
                     "derivedDataRights",
                     "distributionNotes",
                     "distributionRights",
                     "internalUsageNotes",
                     "internalUsageRights",
                     "documentation",
                     "publisher",
                     "techDataOpsId",
                     "accessManagerId",
                     "managerId",
                     "intendedPurpose",
                     "isInternalWithinOrganisation"}
    """
    A mixin providing common package operations
    """

    @deprecated(version='1.17.0', reason="You should use `package=client.packages.get(<package_name>)` to get a package, followed by `package.datasets()`")
    def get_package_datasets(self, package_id, count=100):
        """
        Returns a list of all datasets registered under a package.

        :param str package_id: The id of the package.
        :param int count: Optional. Count of datasets to be returned. Defaults to 100.

        :returns: List of all datasets registered under the package.
        :rtype: list[collections.namedtuple]

        - **Sample**

        .. code-block:: python

                client = dli.connect()
                datasets = client.get_package_datasets(
                    package_id,
                    count=100
                )
        """
        warnings.warn(
            'This method is be deprecated and will be removed soon.'
            'Please use `client.datasets()` instead.',
            PendingDeprecationWarning
        )

        response = self.session.get(
            package_urls.v2_package_datasets.format(id=package_id),
            params={'page_size': count}
        )

        return self._DatasetFactory._from_v2_list_response(response.json())

    @classmethod
    def get_default_package_terms_and_conditions(cls, organisation_name: str):
        """
        Returns a string representing the default Terms And Conditions for packages created in DataLake for a given organisation.

        :returns: The default DataLake Terms And Conditions
        :rtype: str
        """
        # Scott: please do not deprecate this function. It is used by Excel users.
        if organisation_name == 'IHS Markit':
            return ('By submitting this Data request and checking the "Accept Terms and Conditions" '
                'box, you acknowledge and agree to the following:\n'
                '\n'
                '* To promptly notify the relevant Access Manager/Producer of your intended use '
                'of the Data;\n'
                '* To obtain the terms and conditions relevant to such use for such Data from '
                'the Producer;\n'
                '* To distribute such terms and conditions to each member of your '
                'Consumer Group who may use the Data;\n'
                '* To use the Data solely for such intended use, subject to such terms and '
                'conditions;\n'
                '* To ensure that the Data is only accessed by members of your Consumer Group, '
                'and only used by such members for such intended use, subject to such terms and '
                'conditions;\n'
                '* To adhere to any additional requests of Producer with respect to the Data '
                '(including but not limited to ceasing use of the Data and deleting the Data, '
                'and ensuring other members of the Consumer Group do so, upon revocation of your '
                'license by Producer).\n'
                '\n'
                'Please refer to the <a href="/terms-of-use" target="_blank">EULA</a> for any '
                'defined terms used above. '
                'The <a href="/terms-of-use" target="_blank">EULA</a> '
                'is the document you agreed to adhere to by accessing the Lake.')
        else:
            return ''

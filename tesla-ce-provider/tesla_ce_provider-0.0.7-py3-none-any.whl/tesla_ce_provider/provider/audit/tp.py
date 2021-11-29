#  Copyright (c) 2020 Roger Muñoz Bernaus
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" TeSLA CE Plagiarism Provider Audit module """
from .base import BaseAudit


class Comparison:
    """
        Instance of a comparison
    """
    def __init__(self):
        # Identification of comparison
        self.comparison_id = None

        # Value of similitude
        self.result = None

        # Extra info
        self.extra_info = None

    def json(self):
        return {
            'comparison_id': self.comparison_id,
            'result': self.result,
            'extra_info': self.extra_info
        }


class PlagiarismAudit(BaseAudit):
    """ Base Audit for Plagiarism providers class """

    def __init__(self, documents, total_documents, total_documents_accepted, total_documents_rejected,
                 alerts=None, warnings=None, comparisons=None):
        """
            Create a plagiarism audit
            :param total_documents: Total documents
            :type total_documents: int
            :param total_documents_accepted: Total documents accepted
            :type total_documents_accepted: int
            :param total_documents_rejected: Total documents rejected
            :type total_documents_rejected: int
            :param documents: List of documents
            :type documents: list
            :param alerts: List of alerts
            :type alerts: list
            :param warnings: List of warnings
            :type warnings: list
            :param comparisons: List of comparison
            :type comparisons: list
        """
        super().__init__(alerts, warnings)

        self.comparisons = []
        self.documents = documents
        self.total_documents = total_documents
        self.total_documents_accepted = total_documents_accepted
        self.total_documents_rejected = total_documents_rejected
        if comparisons is not None:
            self.comparisons += comparisons

    def add_comparison(self, comparison_id, result, extra_info=None):
        """
            Add a new comparison to the results

            :param comparison_id: Identification of comparison
            :type comparison_id: int
            :param result: Result of similitude
            :type result: float
            :param extra_info: Extra information
            :type extra_info: dict
        """
        if extra_info is None:
            extra_info = {}
        c = Comparison()
        c.comparison_id = comparison_id
        c.result = result
        c.extra_info = extra_info

        self.comparisons.append(c)

    def json(self):
        base = super().json()
        base['comparisons'] = []
        base['documents'] = self.documents
        base['total_documents'] = self.total_documents
        base['total_documents_accepted'] = self.total_documents_accepted
        base['total_documents_rejected'] = self.total_documents_rejected

        for comparison in self.comparisons:
            base['comparisons'].append(comparison.json())
        return base

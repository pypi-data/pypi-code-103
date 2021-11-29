#  Copyright (c) 2021 Roger Muñoz Bernaus
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
""" TeSLA CE Keystroke Provider Audit module """
from .base import BaseAudit


class KeystrokeAudit(BaseAudit):
    """ Base Audit for KeystrokeAudit providers class """

    def __init__(self, num_samples_discarded, num_features, alerts=None, warnings=None):
        """
        Create a Keystroke audit
        :param num_samples_discarded:
        :param num_features:
        :param alerts:
        :param warnings:
        """
        super().__init__(alerts, warnings)

        self.num_samples_discarded = num_samples_discarded
        self.num_features = num_features

    def json(self):
        base = super().json()
        base['num_samples_discarded'] = self.num_samples_discarded
        base['num_features'] = self.num_features

        return base

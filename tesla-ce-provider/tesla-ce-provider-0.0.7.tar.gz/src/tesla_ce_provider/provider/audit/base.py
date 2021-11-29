#  Copyright (c) 2020 Xavier Baró
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
""" TeSLA CE Provider Base Audit module """


class BaseAudit():
    """ Base Audit class """

    def __init__(self, alerts=None, warnings=None):
        """
            Create an audit object

            :param alerts: List of alerts
            :type alerts: list
            :param warnings: List of warnings
            :type warnings: list
        """
        self.alerts = []
        self.warnings = []

        if alerts is not None:
            self.alerts += alerts
        if warnings is not None:
            self.warnings += warnings

    def json(self):
        return {
            'alerts': self.alerts,
            'warnings': self.warnings
        }

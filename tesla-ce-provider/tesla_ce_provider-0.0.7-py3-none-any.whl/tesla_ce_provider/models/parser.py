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
""" TeSLA CE Base Provider base model module """
from .base import ValidationData
from .fr import FRValidationData

def parse_validation_data(object):
    """
        Load a ValidationData object from a JSON representation

        :param object: JSON representation of the object
        :type object: dict
        :return: The specific validation object for this data or None if is an invalid JSON representation
        :rtype: FRValidationData |
    """
    base = ValidationData()
    specific = None
    if base.load(object):
        if base.instrument['acronym'] == 'fr':
            specific = FRValidationData()
        elif base.instrument['acronym'] == 'vr':
            # TODO: Add VR validation data
            pass
        elif base.instrument['acronym'] == 'ks':
            # TODO: Add KS validation data
            pass
    # Load the object with the specific data
    if specific is None or not specific.load(object):
        return None
    return specific

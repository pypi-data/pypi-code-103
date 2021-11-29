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
""" TeSLA CE Provider Messages module """
from enum import Enum


class Provider(Enum):
    """ Message codes related to Providers """
    PROVIDER_MULTIPLE_PEOPLE = 'PROVIDER_MULTIPLE_PEOPLE'
    PROVIDER_INCOMPLETE_ENROLMENT = 'PROVIDER_INCOMPLETE_ENROLMENT'
    PROVIDER_NO_FACE_DETECTED = 'PROVIDER_NO_FACE_DETECTED'
    PROVIDER_INVALID_MIMETYPE = 'PROVIDER_INVALID_MIMETYPE'
    PROVIDER_MISSING_MIMETYPE = 'PROVIDER_MISSING_MIMETYPE'
    PROVIDER_INVALID_SAMPLE_DATA = 'PROVIDER_INVALID_SAMPLE_DATA'
    PROVIDER_BLACK_IMAGE = 'PROVIDER_BLACK_IMAGE'
    PROVIDER_EXTERNAL_SERVICE_DOWN = 'PROVIDER_EXTERNAL_SERVICE_DOWN'
    PROVIDER_EXTERNAL_SERVICE_TIMEOUT = 'PROVIDER_EXTERNAL_SERVICE_TIMEOUT'

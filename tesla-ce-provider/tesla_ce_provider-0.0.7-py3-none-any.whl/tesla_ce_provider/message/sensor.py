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
""" TeSLA CE Sensor Messages module """
from enum import Enum


class Sensor(Enum):
    """ Message codes related to Sensors """
    SENSOR_BROWSER_NOT_SUPPORTED = 'SENSOR_BROWSER_NOT_SUPPORTED'

    SENSOR_CAMERA_MISSING = 'SENSOR_CAMERA_MISSING'
    SENSOR_CAMERA_APP_BLOCKING = 'SENSOR_CAMERA_APP_BLOCKING'
    SENSOR_CAMERA_NO_GRANT = 'SENSOR_CAMERA_NO_GRANT'
    SENSOR_CAMERA_STARTED = ''
    SENSOR_CAMERA_BLACK_IMAGE = ''

    SENSOR_MICROPHONE_MISSING = 'SENSOR_MICROPHONE_MISSING'
    SENSOR_MICROPHONE_APP_BLOCKING = 'SENSOR_MICROPHONE_APP_BLOCKING'
    SENSOR_MICROPHONE_NO_GRANT = 'SENSOR_MICROPHONE_NO_GRANT'
    SENSOR_MICROPHONE_STARTED = ''

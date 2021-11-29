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
""" TeSLA CE Base Provider Face Recognition models module """
from .base import ValidationData


class FRValidationData(ValidationData):
    """
        Validation class for Face Recognition providers
    """
    def __init__(self, data_object=None):
        super().__init__(data_object=data_object)

        #: Detected face
        self.face_location = None

        #: Face orientation
        self.pose = None

    def set_location(self, left, top, height, width):
        """
            Set the face coordinates in image

            :param left: Left coordinate
            :type left: float
            :param top: Top coordinate
            :type top: float
            :param height: Height of the face region
            :type height: float
            :param width: Width of the face region
            :type width: float
        """
        self.face_location = {
            'left': left,
            'top': top,
            'height': height,
            'width': width
        }

    def set_pose(self, roll, yaw, pitch):
        """
            Set head pose estimation
            :param roll: Roll value
            :type roll: float
            :param yaw: Yaw value
            :type yaw: float
            :param pitch: Pith value
            :type pitch: float
        """
        self.pose = {
            'roll': roll,
            'yaw': yaw,
            'pitch': pitch
        }

    def to_json(self):
        """
            Get a JSON representation of the object
            :return: JSON representation
            :rtype: dict
        """
        base_json = super().to_json()
        base_json.update(
            {
                'face_location': self.face_location,
                'pose': self.pose
            }
        )
        return base_json

    def load(self, object):
        """
            Load an object from a JSON representation
            :param object: JSON representation of the object
            :type object: dict
            :return: Whether this object is a valid representation or not
            :rtype: bool
        """
        if super().load(object) and 'face_location' in object and 'pose' in object:
            self.face_location = object['face_location']
            self.pose = object['pose']
            return True
        return False

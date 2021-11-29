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
""" TeSLA CE Face Recognition Provider Audit module """
from enum import Enum
from .base import BaseAudit


class DetectedFace():
    """
        Instance of a detected face
    """

    def __init__(self):
        # Coordinates of the face
        self.coordinates = None

        # Most similar face in the model (ID from enrolment)
        self.most_similar_sample = None

        # Image for the face region
        self.image = None

        # Additional face data
        self.info = None

        # Value of similitude
        self.score = None

    def json(self):
        return {
            'coordinates': self.coordinates,
            'most_similar_sample': self.most_similar_sample,
            'image': self.image,
            'info': self.info,
            'score': self.score
        }


class FaceRecognitionAudit(BaseAudit):
    """ Base Audit for Face Recognition providers class """

    def __init__(self, alerts=None, warnings=None, faces=None):
        """
            Create a face recognition audit

            :param alerts: List of alerts
            :type alerts: list
            :param warnings: List of warnings
            :type warnings: list
            :param faces: List of detected faces
            :type faces: list
        """
        super().__init__(alerts, warnings)

        self.faces = []
        if faces is not None:
            self.faces += faces

    def add_face(self, coordinates, score, most_similar=None, info=None, image=None):
        """
            Add a new detected face to the results

            :param coordinates: Coordinates of the detected face
            :type coordinates: list
            :param score: Score of the recognition
            :type score: float
            :param most_similar: ID of the most similar enrolment sample
            :type most_similar: int
            :param info: Additional information for detected face
            :type info: dict
            :param image: Base64 encoded image for the detected face
            :type image: str
        """
        new_face = DetectedFace()
        new_face.coordinates = coordinates
        new_face.score = score
        new_face.most_similar_sample = most_similar
        new_face.info = info
        new_face.image = image
        self.faces.append(new_face)

    def json(self):
        base = super().json()
        base['faces'] = []
        for face in self.faces:
            base['faces'].append(face.json())
        return base

"""MIT License

Copyright (c) 2021 Pycord

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


class ListeningException(ClientException):
    """Exception that's thrown when there is an error while trying to listening to
    audio from a voice channel.
    """

    pass


class NotConnected(ListeningException):
    """Exception that's thrown when trying to listen while not connected"""

    pass


class AlreadyListening(ListeningException):
    """Exception that's thrown when trying to listen while already listening"""

    pass


class NotListening(ListeningException):
    """Exception that's thrown when trying to stop/pause listening without listening"""

    pass


class MissingSink(ListeningException):
    """Exception that's thrown when trying to listen whithout a valid Sink Object"""

    pass


class audioException(Exception):
    """Base audio Exception."""


class NodeOccupied(audioException):
    """Exception raised when node identifiers conflict."""


class InvalidIDProvided(audioException):
    """Exception raised when an invalid ID is passed somewhere in audio."""


class ZeroConnectedNodes(audioException):
    """Exception raised when an operation is attempted with nodes, when there are None connected."""


class AuthorizationFailure(audioException):
    """Exception raised when an invalid password is provided toa node."""


class BuildTrackError(audioException):
    """Exception raised when a track is failed to be decoded and re-built."""

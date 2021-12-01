from typing import Text


class bf_nluException(Exception):
    """Base exception class for all errors raised by bf_nlu."""


class ModelNotFound(bf_nluException):
    """Raised when a model is not found in the path provided by the user."""


class NoEventsToMigrateError(bf_nluException):
    """Raised when no events to be migrated are found."""


class NoConversationsInTrackerStoreError(bf_nluException):
    """Raised when a tracker store does not contain any conversations."""


class NoEventsInTimeRangeError(bf_nluException):
    """Raised when a tracker store does not contain events within a given time range."""


class PublishingError(bf_nluException):
    """Raised when publishing of an event fails.

    Attributes:
        timestamp -- Unix timestamp of the event during which publishing fails.
    """

    def __init__(self, timestamp: float) -> None:
        self.timestamp = timestamp

    def __str__(self) -> Text:
        return str(self.timestamp)

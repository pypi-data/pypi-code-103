"""Define package errors."""


class WeatherbitError(Exception):
    """Define a base error."""

    pass


class InvalidApiKey(WeatherbitError):
    """Define an error related to invalid or missing API Key."""

    pass

class NotInitialized(WeatherbitError):
    """Define an error related to not initializing station data."""

    pass

class RequestError(WeatherbitError):
    """Define an error related to invalid requests."""

    pass


class ResultError(WeatherbitError):
    """Define an error related to the result returned from a request."""

    pass

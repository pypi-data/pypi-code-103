# coding: utf-8

__all__ = ["Definition"]


class Definition(object):
    """
    Create definition object for desktop session.
    When user provides "session-name", then it is checked
    in the config file for matches, if match is found,
    then this session will be taken, otherwise, an exception will be raised

    When user doesn't provide a session name,
    then the default session from the config file is taken

    Parameters
    ----------
        name: str
            name of the session in config. For example: 'default'
        app_key: str
            application key
    Raises
    ---------
    Exception
        If app-key is not found in the config file and in arguments.

    Examples
    --------
    >>> from refinitiv.data import session
    >>> definition = session.desktop.Definition(name="custom-session-name")
    >>> desktop_session = definition.get_session()
    """

    def __init__(
        self,
        name: str = "default",
        app_key: str = None,
    ):
        from ._session_provider import _make_desktop_session_provider_by_arguments

        if not isinstance(name, str):
            raise ValueError("Invalid session name type, please provide string.")

        self._create_session = _make_desktop_session_provider_by_arguments(
            session_name=name,
            app_key=app_key,
        )

    def get_session(self):
        session = self._create_session()
        return session

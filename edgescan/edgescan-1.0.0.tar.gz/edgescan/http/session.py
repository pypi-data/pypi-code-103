from edgescan.api.authentication import DEFAULT_API_KEY
from hodgepodge.http import DEFAULT_MAX_RETRIES_ON_CONNECTION_ERRORS, DEFAULT_MAX_RETRIES_ON_READ_ERRORS, \
    DEFAULT_MAX_RETRIES_ON_REDIRECT, DEFAULT_BACKOFF_FACTOR, Session

import hodgepodge.http
import edgescan.api.authentication


def get_session(
        api_key: str = DEFAULT_API_KEY,
        max_retries_on_connection_errors: int = DEFAULT_MAX_RETRIES_ON_CONNECTION_ERRORS,
        max_retries_on_read_errors: int = DEFAULT_MAX_RETRIES_ON_READ_ERRORS,
        max_retries_on_redirects: int = DEFAULT_MAX_RETRIES_ON_REDIRECT,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR) -> Session:

    session = Session()
    session.headers.update({
        'X-Api-Token': edgescan.api.authentication.validate_api_key(api_key),
        'Content-Type': 'application/json'
    })
    auto_retry_policy = hodgepodge.http.get_automatic_retry_policy(
        max_retries_on_connection_errors=max_retries_on_connection_errors,
        max_retries_on_read_errors=max_retries_on_read_errors,
        max_retries_on_redirects=max_retries_on_redirects,
        backoff_factor=backoff_factor,
    )
    hodgepodge.http.attach_session_policies(session=session, policies=[auto_retry_policy])
    return session

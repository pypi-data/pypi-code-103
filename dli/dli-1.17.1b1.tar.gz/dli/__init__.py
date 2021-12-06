#
# Copyright (C) 2020 IHS Markit.
# All Rights Reserved
#
import warnings


warnings.filterwarnings(
    'always', module="dli"
)

warnings.filterwarnings(
    'ignore', module="dli", category=ResourceWarning
)

warnings.filterwarnings(
    action='ignore',
    category=FutureWarning,
    message='^pandas.util.testing is deprecated'
)

__version__ = '1.17.1b1'
__product__ = "ihsm-datalake"


try:
    import simplejson as _  # noqa
    warnings.warn(
        'Incompatible Package `simplejson`.\n\n'
        '\t`simplejson` is a backport of the built in json library in Python. '
        'It contains subtle differences, and is not intended for use beyond '
        'Python 2.6. Please uninstall `simplejson` by running:\n\n'
        '\t\tpip uninstall simplejson\n\n'
        '\tOr run the DLI from a virtual environment as it is known to cause '
        'issues within the DLI.\n',
        ImportWarning
    )
except ImportError:
    pass


def connect(
    root_url="https://catalogue.datalake.ihsmarkit.com/__api",
    debug=None,
    strict=True,
    use_keyring=True,
    log_level=None,
    show_login_url=False,
):
    """
    Entry point for the Data Lake SDK, returns a client instance that
    can be used to consume or register datasets.

    Example for starting a session:


    .. code:: python

        import dli
        client = dli.connect()

    :param str root_url: Optional. The environment you want to point to. By default it
                        points to Production.
    :param bool debug: Optional. Log SDK operations to a file in the current working
                       directory with the format "sdk-{end of api key}-{timestamp}.log"

    :param bool strict: Optional. When True, all exception messages and stack
                        trace are printed. When False, a shorter message is
                        printed and `None` should be returned.
    :param bool use_keyring: Optional. When True, cache the JWT in the system keyring
                             and retrieve that JWT from the system keyring if set.
                             Otherwise disable the keyring completely.

    :returns: Data Lake interface client
    :rtype: dli.client.dli_client.DliClient

    """
    from dli.client.session import _start_session

    return _start_session(
        root_url=root_url,
        debug=debug,
        strict=strict,
        use_keyring=use_keyring,
        log_level=log_level,
        show_login_url=show_login_url,
    )


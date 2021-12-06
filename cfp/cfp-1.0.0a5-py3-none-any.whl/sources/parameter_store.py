from dataclasses import dataclass
from typing import Optional

from boto3.session import Session

from cfp.sources.source import Source


@dataclass
class FromParameterStore(Source):
    """
    Describes how to look-up a value in Amazon Web Services Systems Manager
    Parameter Store.

    Example:

            from cfp import FromParameterStore, StackParameters

            sp = StackParameters()
            sp.add("ParameterA", FromParameterStore("/cfp/example1"))
            sp.add("ParameterB", FromParameterStore("/cfp/example2"))

            print(sp.api_parameters)

    """

    name: str
    """Name of the parameter in Parameter Store."""

    region: Optional[str] = None
    """
    Amazon Web Services region in which the parameter resides.

    Not required if :py:attr:`.session` is configured for the correct region, or
    if  :py:attr:`.session` is omitted but the default session region is correct.
    """

    session: Optional[Session] = None
    """
    boto3 session to use to retrieve the value from Parameter Store.

    A new session will be created if omitted. If :py:attr:`.region` is set then
    the new session will be configured for that region, otherwise the default
    session region will be used.

    You must specify a session if you want to read Parameter Store values in
    another account.
    """

import attr

from ..modules import Module


@attr.s(slots=True, repr=False)
class BespokeModule(Module):
    """
    Abstract class that needs to be implemented by all the Levo CLI plugins. The setup and teardown
    methods will allow the plugin to setup any pre-requisites, like bringing up a ZAP server, in order
    to run the test cases of that plugin successfully.
    """

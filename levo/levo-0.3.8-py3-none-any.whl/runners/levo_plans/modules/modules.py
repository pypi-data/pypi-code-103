from enum import Enum

import attr

from ....config import TestPlanCommandConfig


class ModuleName(str, Enum):
    Schemathesis = "schemathesis"
    Bespoke = "bespoke"
    Ssrfmap = "ssrfmap"


@attr.s(slots=True, repr=False)
class Module:
    """
    Abstract class that needs to be implemented by all the Levo CLI plugins. The setup and teardown
    methods will allow the plugin to setup any pre-requisites, like bringing up a ZAP server, in order
    to run the test cases of that plugin successfully.
    """

    name: str = attr.ib()

    def setup(self, config: TestPlanCommandConfig) -> None:
        pass

    def teardown(self) -> None:
        pass

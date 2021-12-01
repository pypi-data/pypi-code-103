"""This module contains all definitions to describe meta data of a plugin, a.k.a. PluginInfo."""
from enum import Enum
from typing import Any, Optional

from attr import dataclass


@dataclass
class Author:
    """
    The author of an Extraction Plugin.

    This information can be retrieved by an end-user from Hansken.
    """

    name: str
    email: str
    organisation: str


class MaturityLevel(Enum):
    """This class represents the maturity level of an extraction plugin."""

    PROOF_OF_CONCEPT = 0
    READY_FOR_TEST = 1
    PRODUCTION_READY = 2


@dataclass
class PluginId:
    """Identifier of a plugin, consisting of domain, category and name. Needs to be unique among all tools/plugins."""

    domain: str
    category: str
    name: str


class PluginResources:
    """
    PluginResources contains information about how many resources will be used for a plugin.

    The most common resources to specify are CPU and memory (RAM).

    CPU resources are measured in cpu units. One cpu is equivalent to 1 vCPU/Core for cloud providers and 1 hyperthread
    on bare-metal Intel processors. Also, fractional requests are allowed. A plugin that asks 0.5 CPU uses half as
    much CPU as one that asks for 1 CPU.

    Memory resources are measured in Megabytes.

    Here is an example to set resources for a plugin:

    .. code-block:: python

        PluginResources.builder()
            .maximum_cpu(0.5)
            .maximum_memory(1000)
            .build()

    In this example the plugin has a limit of 0.5 cpu and 1G of memory.
    """

    def __init__(self, max_cpu: float, max_memory: int) -> None:
        """
        Initialize PluginResources (don't use this, use .PluginResources.Builder instead).

        :param maxima: map of resource type and maximum quantities
        """
        self._max_cpu = max_cpu
        self._max_memory = max_memory

    def maximum_cpu(self) -> Optional[float]:
        """
        Return the maximum cpu.

        :return: Maximum cpu
        """
        return self._max_cpu

    def maximum_memory(self) -> Optional[int]:
        """
        Return the maximum memory.

        :return: Maximum memory
        """
        return self._max_memory

    @staticmethod
    def builder():
        """:return a Builder."""
        return PluginResources.Builder()

    class Builder:
        """Helper class that implements a resources builder."""

        def __init__(self) -> None:
            """Initialize a Builder."""
            self._max_cpu: float
            self._max_memory: int

        def maximum_cpu(self, quantity: float):
            """
            Set maximum cpu usage to plugin resources.

            :param quantity the cpu resource quantity
            :return: this `.PluginResources.Builder`
            """
            self._max_cpu = quantity
            return self

        def maximum_memory(self, quantity: int):
            """
            Set maximum memory usage to plugin resources.

            :param quantity the memory resource quantity
            :return: this `.PluginResources.Builder`
            """
            self._max_memory = quantity
            return self

        def build(self) -> 'PluginResources':
            """
            Return PluginResources.

            :return: PluginResources
            """
            return PluginResources(self._max_cpu, self._max_memory)


class PluginInfo:
    """This information is used by Hansken to identify and run the plugin."""

    plugin: Any  # noqa
    version: str
    description: str
    author: Author
    maturity: MaturityLevel
    matcher: str
    webpage_url: str
    id: PluginId
    license: str
    deferred_iterations: int
    resources: PluginResources

    def __init__(self, plugin, version, description, author, maturity, matcher, webpage_url, id, license=None,
                 deferred_iterations=1, resources=None):
        """
        Initialize a PluginInfo.

        :param plugin: the plugin that returns this plugininfo, pass self
        :param version: version of the plugin
        :param description: short description of the functionality of the plugin
        :param author: the author, this is an Author object
        :param maturity: maturitylevel, see enum
        :param matcher: this matcher selects the traces offered to the plugin
        :param webpage_url: plugin url
        :param id: PluginId consisting of domain, category of name. this combination should be unique for every plugin
        :param license: license of this plugin
        :param deferred_iterations: Optional, number of deferred iterations. Only for deferred plugins.
                                    Number should be between 1 and 20.
        :param resources: Optional, resources for a plugin
        """
        self.plugin = plugin
        self.version = version
        self.description = description
        self.author = author
        self.maturity = maturity
        self.matcher = matcher
        self.webpage_url = webpage_url
        self.id = id
        self.license = license
        self.deferred_iterations = deferred_iterations
        self.resources = resources

        if not 1 <= self.deferred_iterations <= 20:
            raise ValueError(f'Invalid value for deferredIterations: {self.deferred_iterations}. '
                             f'Valid values are 1 =< 20.')

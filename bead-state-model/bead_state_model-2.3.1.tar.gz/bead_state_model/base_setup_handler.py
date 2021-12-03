from abc import ABC, abstractmethod
from typing import Dict, Any

from readdy import ReactionDiffusionSystem


class BaseSetupHandler(ABC):
    """
    Derive from this class to implement setup handlers for your simulation setup.
    Provide an instance of your implemented class when creating
    :class:`~bead_state_model.Simulation` instances.
    Override the :meth:`~bead_state_model.BaseSetupHandler.__call__` method to contain the configuration
    of interactions between the 4 filament particles ``["head", "core", "motor", "tail"]`` and any
    external particles/topologies you have defined. Furthermore, define any external potentials
    (to create layers of filaments, etc.) affecting filaments or any external particles.
    Override the :meth:`~bead_state_model.BaseSetupHandler.from_config_dict` and
    :meth:`~bead_state_model.BaseSetupHandler.to_config_dict` methods to make your simulation output
    reproducible. I.e., it has to be possible to create identical instances of your implemented SetupHandler
    through the :meth:`~bead_state_model.BaseSetupHandler.from_config_dict` method with the dictionary
    that your :meth:`~bead_state_model.BaseSetupHandler.to_config_dict` method returns.
    """

    @abstractmethod
    def __call__(self, system: ReactionDiffusionSystem):
        """
        This method gets executed during simulation setup. Override this method
        and make sure to handle all definitions of external particles and
        potentials in here.

        :param system: The system object of the underlying ReaDDy simulation framework. You
                       can make full use of all methods the system object provides. See
                       documentation of `ReaDDy <https://readdy.github.io/>`_ for more information.
        """
        ...

    @staticmethod
    @abstractmethod
    def from_config_dict(d: Dict[str, Any]) -> 'BaseSetupHandler':
        """
        Override this method to generate an instance of your class from stored parameters. The
        parameters specified in ``d`` should match those of the
        :meth:`~bead_state_model.BaseSetupHandler.to_config_dict`. The pattern of
        ``from_config_dict/to_config_dict`` is an attempt to force the user to properly save/load
        parameters in a reproducible manner.

        :param d: Dictionary containing all parameters required to create an instance of your implementation
                  of the BaseSetupHandler.
        :return: Instance generated with provided parameters.
        """
        ...

    @abstractmethod
    def to_config_dict(self) -> Dict[str, Any]:
        """
        Override this method when you create an implementation of the ``BaseSetupHandler``.
        Use attributes of your class to construct a (complete) dictionary, containing
        all parameters that would be required to reproduce an identical instance of the class.
        This is to make sure you write all important parameters to the config file. The
        config file will be generated automatically when you run a simulation
        (through the :meth:`~bead_state_model.Simulation.run` method).

        :return: All parameters of the instance of your class.
        """
        ...

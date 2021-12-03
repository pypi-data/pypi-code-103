""" Utilities to generate random, biomimetic biopolymer networks. """

from typing import Any, Dict
import numpy as np

from .create_network import Filament, CreateNetwork, RandomNumberHandler


class CreateNetworkNatural(CreateNetwork):

    """ Class to manage generation of random polymer networks.

    You control the generation via rates for nucleation (start of a new, short polymer)
    and assembly (rate at which new beads get added to polymers). Furthermore,
    you have to specify for how many steps the algorithm should run. Rates are in
    instances per simulated step.
    With this algorithm you can not:

    * Generate a network with fixed number of Polymers. The number of polymers
      can be estimated via :code:`n_steps * rate_nucleation`.
    * Generate polymers of identical length. The lengths of polymers are hard
      to predict, for each polymer they roughly
      :code:`(n_steps - step_of_nucleation) * rate_assembly`. To limit the variance
      of this to some degree, you can forbid nucleations after a certain
      time step via parameter no_nucleation_after.

    To generate inhomogeneous, this class uses the so called
    ``acceptance_rate_handler``. You can overwrite
    the default ``acceptance_rate_handler`` to make new polymers to nucleate and new
    beads to assembly with higher probability in certain locations of the system
    based on potentials. I.e. this module contains the class
    :class:`bead_state_model.network_assembly.create_network.AcceptanceRateHandlerBeadInNetwork`,
    that adds a repulsive potential in the center of the box, to leave a gap where a bead
    will be placed in the simulations. This is to reduce overlap in the simulations and to make
    relaxation less dangerous.

    See the documentation's example section for different usages of this class.
    """

    def __init__(self, reserve_n_beads: int, n_steps: int,
                 rate_nucleation: float, rate_assembly: float,
                 box: np.ndarray, k_bend: float, k_stretch: float,
                 no_nucleation_after: int=None):
        super().__init__(reserve_n_beads, box, k_bend, k_stretch)
        self.n_steps = n_steps
        self.rate_nucleation = rate_nucleation
        self.rate_assembly = rate_assembly

        if no_nucleation_after is None:
            self.no_nucleation_after = self.n_steps
        else:
            self.no_nucleation_after = no_nucleation_after
        
        self.t = 0
        self.nucleation_events = []
        self._draw_nucleation_events()
        self.current_nucleation_event = 0


    def run(self, verbose=False):
        """ Run the network generation algorithm for the before hand specified
        number of time steps.
        """
        n_digits = len(str(self.n_steps))
        percent = self.n_steps//100
        process_str = "creating network ... step {:0" + str(n_digits) + "}/"+str(self.n_steps)
        for t in range(0, self.n_steps):
            if verbose:
                if t % percent == 0:
                    print(process_str.format(t), end='\r')
            self.t = t
            while self._nucleation_happens():
                self._add_filament()
            for f in self.filaments:
                while f.assembly_happens(self.t):
                    self._add_bead(f)
        if verbose:
            print()

    def get_config_as_dict(self) -> Dict[str, Any]:
        d = super().get_config_as_dict()
        d.update({
            'n_steps': self.n_steps,
            'rate_nucleation': self.rate_nucleation,
            'rate_assembly': self.rate_assembly,
            'sigma_angle': self.sigma_theta,
            'sigma_stretch': self.sigma_stretch,
            'no_nucleation_after': self.no_nucleation_after,
        })
        return d
        
    def _nucleation_happens(self) -> bool:
        if len(self.nucleation_events) <= self.current_nucleation_event:
            return False
        if self.nucleation_events[self.current_nucleation_event] == self.t:
            self.current_nucleation_event += 1
            return True
        return False

    def _draw_nucleation_events(self):
        self.nucleation_events = self._rn_handler.get_poisson_events(
            self.rate_nucleation, self.no_nucleation_after)

    def _add_filament(self):
        start, end = self._add_beads_of_nucleated_filament()
        f = FilamentWithPoissonEvents(start, end, self.rate_assembly, self.n_steps, self.t)
        self.filaments.append(f)


class FilamentWithPoissonEvents(Filament):

    def __init__(self, first, last, rate, n_steps, current_step):
        super().__init__(first, last)
        event_times = RandomNumberHandler.get_poisson_events(
            rate, n_steps-current_step)
        self.assembly_events = event_times + current_step
        self.current_event = 0

    def assembly_happens(self, current_step) -> bool:
        if len(self.assembly_events) <= self.current_event:
            return False
        if self.assembly_events[self.current_event] == current_step:
            self.current_event += 1
            return True
        return False

def create_network(folder: str, n_steps: int,
                   rate_nucleation: float, rate_assembly: float,
                   box: np.ndarray, k_bend: float, k_stretch: float,
                   no_nucleation_after: int):    
    expected_max = int((no_nucleation_after*rate_nucleation * n_steps*rate_assembly)*2)

    s = CreateNetworkNatural(expected_max, n_steps, rate_nucleation, rate_assembly,
                             box, k_bend, k_stretch, no_nucleation_after)
    s.run()
    s.write(folder)


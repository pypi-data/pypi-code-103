from typing import Dict, Any
import numpy as np
from .create_network import CreateNetwork


class CreateNetworkSimple(CreateNetwork):
    """
    Create a network of N filaments with identical number of beads M.
    The actual number of beads can be shorter for some filaments, if
    the system volume is very crowded and no place can be found to
    place the beads. In that case you might want to sort out
    shorter filaments afterwards, if you strictly need filaments
    of same size.
    Call method ``CreateNetworkSimple.run`` to start
    network generation.
    Before calling run method, set attribute ``acceptance_rate_handler``
    if you do not want to use the default one (e.g. to account
    for potentials in your system use
    ``bead_state_model.network_assembly.create_network.AcceptanceRateHandlerPotential``).
    Same goes for attribute ``nucleation_direction_func``.
    """

    def __init__(self, box: np.ndarray, k_bend: float, k_stretch: float,
                 n_filaments: int, n_beads_per_filament: int):
        """
        :param box: Array of 3 floats: length of x y z edges.
        :param k_bend: Bending modulus of filaments. See section :ref:`potentials`
                       in the documentation.
        :param k_stretch: Stretching modulus, i.e. strength of harmonic bond
                          keeping adjacent beads at desired distance of 1.
        :param n_filaments: Number of filaments to create.
        :param n_beads_per_filament: Number of beads per filament (identical for all
                                     filaments, as long as there is enough space to
                                     place all the beads).
        """
        super().__init__(n_filaments * n_beads_per_filament,
                         box, k_bend, k_stretch)
        self.n_filaments = n_filaments
        self.n_beads_per_filament = n_beads_per_filament

    def run(self, verbose=False):
        """
        Calling this methods runs the network generation algorithm, all parameters have
        to be specified prior to this.
        Call method ``write`` afterwards, to save resulting network to file.
        """
        for i in range(self.n_filaments):
            self._add_filament()

        n_digits = len(str(self.n_beads_per_filament))
        process_str = "creating network ... appended {:0" + str(n_digits)
        process_str += "}/" + str(self.n_beads_per_filament) + " beads to all filaments"

        for i in range(2, self.n_beads_per_filament):
            if verbose:
                print(process_str.format(i+1), end='\r')
            for f in self.filaments:
                self._add_bead(f)
        if verbose:
            print()

    def get_config_as_dict(self) -> Dict[str, Any]:
        d = super().get_config_as_dict()
        d.update({
            'n_filaments': int(self.n_filaments),
            'n_beads_per_filament': int(self.n_beads_per_filament)
        })
        return d

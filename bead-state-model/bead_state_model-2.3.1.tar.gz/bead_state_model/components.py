from typing import List, Tuple, Union
import numpy as np

LinksArray = np.ndarray


class Bead:
    """
    Container to store all information on one bead: its id,
    position, and to which other beads it is bound.

    :ivar id_: Bead ID.
    :ivar prv: ID of previous bead in the filament, if you go from tail to head
               along the beads of a filament. -1 if no previous bead.
    :ivar nxt: ID of next bead in filament. -1 if no next bead.
    :ivar cross_filament: ID of bead in another filament this bead is bound to.
                          If this is a positive integer, this bead (and the one it is
                          connected to) is a motor/cross-link. -1 if no bond to
                          bead in another filament.
    """

    def __init__(self, id_, x, y, z, prv, nxt, cross_filament):
        self.id_ = id_
        self.x = x
        self.y = y
        self.z = z
        self.prv = prv
        self.nxt = nxt
        self.cross_filament = cross_filament


class Filament:
    """
    Filament stores information which beads belong to this filament. In order
    to create a list of bead indices belonging to this filament, either
    a list of all beads needs to be provided, or a array containing information
    on bonds between beads.

    Filament can also be initialized with two lists of integers, where the first
    is the list of ordered bead indices that are part of this filament, the second
    one is the list of motors (which items of the first list are motors).

    :ivar items: Ordered list of bead IDs that represent this filament.
    :ivar motors: Subset of bead IDs in self.items that are motors.
    """

    def __init__(self, filament_id: int, idx_tail: Union[int, List[int]],
                 link_info: Union[List[Bead], np.ndarray, List[int]]):
        """
        :param idx_tail: Starting point of filament, i.e. the bead that has no previous neighbor bead.
                         Or in the second mode, a list of indices of beads that form this filament.
        :param link_info: Either a list of Bead instances or an integer array with
                          link information (3 columns, pointers to linked beads:
                          1. previous, 2. next, 3.cross-filament)
                          Or in the second mode, a list of indices (that has to be a subset of the first
                          list) indicating which of this filament's beads are motors.
        """
        msg = "link_info needs to be either a list of Bead instances or an "
        msg += "integer array with link information "
        msg += "(3 columns, pointers to linked beads: 1. previous, 2. next, 3.cross-filament)"

        if isinstance(idx_tail, list):
            if not isinstance(link_info, list):
                msg = "In second mode (initialization via lists of bead indices), the second "
                msg += "parameter ``link_info`` has to be a list, too. The parameter provided "
                msg += "is not a list!"
                raise KeyError(msg)
            self.items = idx_tail
            self.motors = link_info
        elif isinstance(link_info, list):
            if isinstance(link_info[0], Bead):
                self.items, self.motors =\
                    Filament._init_items_with_bead_list(idx_tail, link_info)
            else:
                raise KeyError(msg)
        elif isinstance(link_info, np.ndarray):
            self.items, self.motors =\
                Filament._init_items_with_link_array(idx_tail, link_info)
        else:
            raise KeyError(msg)
        self.id = filament_id

    @staticmethod
    def _init_items_with_link_array(
            idx_tail: int,
            links: np.ndarray
    ) -> Tuple[List[int], List[int]]:
        items = [idx_tail]
        motors = []
        while links[items[-1], 1] != -1:
            idx_current = links[items[-1], 1]
            items.append(idx_current)
            if links[idx_current, 2] != -1:
                motors.append(idx_current)
        return items, motors

    @staticmethod
    def _init_items_with_bead_list(
            idx_tail,
            beads: List[Bead]
    ) -> Tuple[List[int], List[int]]:
        items = [idx_tail]
        motors = []
        while beads[items[-1]].nxt != -1:
            idx_current = beads[items[-1]].nxt
            items.append(idx_current)
            if beads[idx_current].cross_filament != -1:
                motors.append(idx_current)
        return items, motors
        
    def to_readdy_species_list(self) -> List[str]:
        """
        Export filament as species list that can be passed to readdy.
        """
        if len(self.items) < 3:
            raise RuntimeError("need at least 3 items for filament")
        slist = ['tail'] + ['core']*(len(self.items)-2) + ['head']
        for m in self.motors:
            slist[self.items.index(m)] = 'motor'
        return slist

    def to_particle_coordinates(self, beads: List[Bead]) -> np.ndarray:
        """
        Get bead coordinates as np.array.
        """
        coords = np.empty((len(self.items), 3))
        for i, particle_id in enumerate(self.items):
            b = beads[particle_id]
            coords[i] = (b.x, b.y, b.z)
        return coords

    def get_tail(self) -> int:
        """
        Get tail of filament.
        """
        return self.items[0]
    
    def __str__(self) -> str:
        s = "Filament; ordered items: {}".format(self.items)
        return s

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def generate_filaments_from_link_array(
            ids: np.ndarray,
            tails: np.ndarray,
            links: np.ndarray
    ) -> List['Filament']:
        filaments = []
        for i, tail in enumerate(tails):
            row = links[tail]
            if not is_tail(*row):
                raise RuntimeError(f"Tail bead {tail} is not a tail at all! "
                                   "Something is wrong. Entry in link array is: "
                                   f" {row} .")
            id_ = ids[i]
            filaments.append(Filament(id_, tail, links))
        return filaments


def load_beads(fname: str) -> Tuple[List[Bead], List[Filament], LinksArray]:
    """
    Load particles from bead file (see documentation for format
    of those files).

    :return: [0] List of Bead objects (position, state, bonds),
             [1] List of Filament objects (head, tail, bead indices),
             [2] Numpy array defining the bonds between beads as a linked list
             (-1 means no bond). See documentation for meaning of columns and rows.
    """
    with open(fname, 'rt') as fp:
        lines = fp.readlines()
    beads = []
    links = []
    for line in lines:
        s = line.split()
        link_previous_bead = int(s[4])
        link_next_bead = int(s[5])
        link_cross_filament = int(s[6])
        position = [
            float(s[1]),
            float(s[2]),
            float(s[3]),
        ]
        beads.append(Bead(int(s[0]),
                          position[0],
                          position[1],
                          position[2],
                          link_previous_bead,
                          link_next_bead,
                          link_cross_filament))
        links.append([link_previous_bead, link_next_bead, link_cross_filament])

    filaments = []
    for i, b in enumerate(beads):
        if b.prv != -1:
            continue
        id_ = len(filaments)
        fil = Filament(id_, i, beads)
        filaments.append(fil)

    links = np.array(links)

    return beads, filaments, links


def is_tail(previous, nxt, cross_filament) -> bool:
    if previous != -1:
        return False
    if nxt == -1:
        return False
    if cross_filament != -1:
        return False
    return True



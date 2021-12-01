import numpy as np
from typing import List
from .bead import (Bead, Filament,
                   STATE_FILAMENT_START,
                   STATE_FILAMENT_INTERIOR,
                   STATE_FILAMENT_END)


class BeadStates(object):

    def __init__(self, links_array):
        self.linked_beads = {}
        self.filaments = []
        self.links = links_array
        
        self.states = self._bead_links_to_states(self.links)
        self.parse_links_to_beads(links_array)
        self.parse_beads_to_filaments()

    def get_indices_of_filament(self, filament_index: int) -> List[int]:
        f = self.filaments[filament_index]
        return f.items

    def parse_links_to_beads(self, links_array):
        if (links_array.shape[0] % 3 != 0):
            msg = "links_array needs to be multiple of 3 " 
            msg += "(links to previous, next, and cross-linked beads)."            
            raise RuntimeError(msg)
        for i in range(links_array.shape[0] // 3):
            links_i = links_array[i * 3: (i + 1) * 3]            
            if (links_i != -1).any():
                if links_i[0] == links_i[1]:
                    msg = "errors in data: bead " + str(i) \
                          + " has same previous and next neighbour!"
                    raise RuntimeError(msg)
                b = Bead()
                b.previous, b.next, b.cross = links_i                
                self.linked_beads[i] = b

    def parse_beads_to_filaments(self):
        for i in self.linked_beads:
            b_i = self.linked_beads[i]
            if b_i.previous == -1 and b_i.next != -1:
                start = i
                n = b_i.next
                items = [start, n]
                motors = []
                b_next = self.linked_beads[n]
                while b_next.next != -1:
                    if b_next.cross != -1:
                        motors.append(n)
                    n = b_next.next
                    items.append(n)
                    b_next = self.linked_beads[n]
                f = Filament(items, motors)
                self.filaments.append(f)

    def _bead_links_to_states(self, links_array):
        if links_array.shape[0] % 3 != 0:
            msg = "links_array' length needs to be multiple of 3 "
            msg += "(links to previous, next beads and across filaments)."
            raise RuntimeError(msg)
        s = np.zeros(links_array.shape[0] // 3)
        for i in range(0, s.shape[0], 1):
            l = links_array[i * 3: (i + 1) * 3]
            if (l == -1).all():
                continue
            if (l[0] != -1) and (l[1] != -1):
                s[i] = STATE_FILAMENT_INTERIOR                
            elif (l[0] != -1) and (l[1] == -1):
                s[i] = STATE_FILAMENT_END
            elif (l[0] == -1) and (l[1] != -1):
                s[i] = STATE_FILAMENT_START
        return s

#!/usr/bin/env python3

"""
|=========================|
| Les connections reseau. |
|=========================|

* Dans un graphe qui represente un reseau internet, les arcs
relient les machines aux boxes et aux routeurs.
* Modelise un debit variable, le ping ...
"""

import time

from ..segment import Arrow
from .adaptive import Adaptive


class Connection(Arrow, Adaptive):
    """
    |====================================|
    | Un cable RJ45 et une carte reseau. |
    |====================================|
    """
    def __init__(self, vs, vd):
        """
        |=============================================|
        | Initialise une representauon de connection. |
        |=============================================|

        Parameters
        ----------
        :param vs: Noeud de depart
        :type vs: Vertex
        :param vd: Noeud d'arrive.
        :type vd: Vertex
        """
        Arrow.__init__(self, vs, vd)
        Adaptive.__init__(self)

        self.flags["color"] = "black"
        
    def get_attr(self):
        """
        |===================================|
        | Recupere les arguments suffisants |
        | a la reconstitution de self.      |
        |===================================|

        Returns
        -------
        :return: Les clefs et les valeurs a passer a l'initialisateur
            de facon a instancier un nouvel objet de contenu identique a self.
        :rtype: dict
        """
        return {"vs": self.vs.n, "vd": self.vd.n}

#!/usr/bin/env python3

"""
|==========================|
| Les noeuds 'ordinateur'. |
|==========================|

* Dans un graphe qui represente un reseau internet, les noeuds
modelises ici sont les noeuds qui sont capable d'effectuer un calcul.
"""

import time

from raisin.tools import identity
from ..vertex import Vertex
from .adaptive import Adaptive


class Computer(Vertex, Adaptive):
    """
    |===============================|
    | Un ordinateur dans un reseau. |
    |===============================|

    * C'est une entitee capable d'executer des taches.
    """
    def __init__(self, mac, *, n=None):
        """
        :param mac: Adresse mac de la machine physique.
        :type mac: str
        """
        # Initialisation des attributs standards.
        self.mac = mac

        # Heritage.
        Vertex.__init__(self, n=n, name=f"computer_{mac}")
        Adaptive.__init__(self)

        # Constantes.
        self.flags["edgecolor"] = "black"
        if mac == identity["mac"]:
            self.flags["facecolor"] = "#ff0000" # Rouge.
        else:
            self.flags["facecolor"] = "#77c100" # Vert.

    def get_attr(self):
        """
        |======================================|
        | Recupere les arguments suffisants    |
        | a la reconstitution d'un ordinateur. |
        |======================================|

        Returns
        -------
        :return: Les clefs et les valeurs a passer a l'initialisateur
            de facon a instancier un nouvel objet de contenu identique a self.
        :rtype: dict
        """
        return {"mac": self.mac,
                "n": self.n}

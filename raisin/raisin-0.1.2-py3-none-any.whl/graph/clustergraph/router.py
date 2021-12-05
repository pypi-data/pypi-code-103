#!/usr/bin/env python3

"""
|=======================================|
| Les noeuds d'interconnection routeur. |
|=======================================|

* Dans un graphe qui represente un reseau internet, les noeuds
modelises ici sont les noeuds qui n'effectuent pas de calcul mais
qui sont capable d'aiguiller des paquets.
"""

import time

import getmac

from raisin.tools import identity
from raisin.application.settings import settings
from ..vertex import Vertex
from .adaptive import Adaptive


class Internet(Vertex, Adaptive):
    """
    |=================|
    | Noeud internet. |
    |=================|

    * Les arcs qui partent de ce noeud pointent vers des
    noeuds de type 'InBoxing'.
    * Les arcs qui arrivent sur ce noeud provienent de
    noeuds de type 'OutBoxing'.
    """
    def __init__(self, n=None):
        Vertex.__init__(self, name="internet", n=n)
        Adaptive.__init__(self)
        self.flags["edgecolor"] = "black"
        self.flags["facecolor"] = "#aedbe7" # Bleu ciel.

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
        return {"n": self.n}

class InBoxing(Vertex, Adaptive):
    """
    |============================|
    | La boxe d'un reseau local. |
    | WAN --> LAN                |
    |============================|

    * Tous les ordinateurs d'un reseau local sont
    connectes 'dans les 2 sens' a ce noeud.
    * Ce noeud a aussi un arc qui pointe vers 'Internet'.
    """
    def __init__(self, *, mac=None, n=None):
        """
        |=========================================|
        | Initialisation du noeud de redirection. |
        |=========================================|

        Parameters
        ----------
        :param mac: Adresse mac de la boxe, si elle est omise, cherche l'adresse de la boxe actuelle.
        :type mac: str
        :param n: Numero unique de noeud.
        :type n: int
        """

        # Recuperartion adresse mac.
        self.mac = mac
        for ip in {"192.168.0.1", "192.168.1.1"}:
            if self.mac:
                break
            self.mac = getmac.get_mac_address(ip=ip)
        if not self.mac:
            self.mac = getmac.get_mac_address(hostname="_gateway")
        if not self.mac:
            raise OSError("Impossible de trouver l'adresse mac de la boxe.")

        # Heritage.
        Vertex.__init__(self, name=f"inboxing_{self.mac}", n=n)
        Adaptive.__init__(self)

        # Constantes.
        self.flags["edgecolor"] = "#960406" # Rouge sang.
        self.flags["facecolor"] = "#ffff66" # Jaune clair.

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
        return {"mac": self.mac, "n": self.n}

class OutBoxing(Vertex, Adaptive):
    """
    |============================|
    | La boxe d'un reseau local. |
    | LAN --> WAN                |
    |============================|
    """
    def __init__(self, mac, *, n=None):        
        # Recuperartion adresse mac.
        self.mac = mac
        for ip in ["192.168.0.1", "192.168.1.1"]:
            if self.mac:
                break
            self.mac = getmac.get_mac_address(ip=ip)
        if not self.mac:
            self.mac = getmac.get_mac_address(hostname="_gateway")
        if not self.mac:
            raise OSError("Impossible de trouver l'adresse mac de la boxe.")
        
        # Heritage
        Vertex.__init__(self, name=f"outboxing_{self.mac}", n=n)
        Adaptive.__init__(self)

        # Constantes.
        self.flags["edgecolor"] = "#01946d" # Vert / Bleu turquoise fonce.
        self.flags["facecolor"] = "#ffff55" # Jaune clair.

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
        return {"mac": self.mac, "n": self.n}

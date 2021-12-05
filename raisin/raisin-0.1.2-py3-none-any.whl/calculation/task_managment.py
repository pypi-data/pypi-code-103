#!/usr/bin/env python3

"""
|=======================|
| Décide qui fait quoi. |
|=======================|

* C'est le cerveau qui fait de la theorie des
graphes pour trouver comment dispatcher les paquets
qui constituent un noeud de calcul.

* Plus precisement, ce module annalyse continuellement
l'etat du graphe pour y metre a jour les consignes de
calcule de chaques machines.
"""
from raisin.graph.clustergraph.network import Network

class TaskLeader:
    """
    |=================================|
    | Permet d'enregistrer certains   |
    | resultats pour gagner du temps. |
    |=================================|
    """
    def __init__(self):
        """Contient toutes les infos des calculs."""
        raise NotImplementedError


    def __call__(self, graph):
        """
        |=================================================|
        | Met a jour le graphe avec des consignes neuves. |
        |=================================================|

        Parameters
        ----------
        :param graphe: Le graphe present dans le serveur local.
            Ce graphe doit etre fraichement mis a jour, si il est
            perime, c'est pas tip top.
        :type graphe: Network

        Returns
        -------
        :returns: Ce meme graphe mis a jour. C'est a dire
            que les noeuds du graphe possedent les nouvelles
            instructions a suivre.
        :rtype: Network
        """
        assert isinstance(graph, Network)

        raise NotImplementedError

        return graph

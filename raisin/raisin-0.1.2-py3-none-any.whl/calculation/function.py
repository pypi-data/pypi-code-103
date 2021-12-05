#!/usr/bin/env python3

"""
|============================================|
| Representation de la fonction d'une tache. |
|============================================|

Lorsque qu'un utilisateur shouaite deporter des calculs,
chaque calcul est decompose comme un apel de fonction
qui prend des arguments. La classe 'Function' permet justement
de representer ce point d'entre.

Ce fichier permet de representer la fonction de facon optimale pour pouvoir:
* Charger une fonction deja enregistree.
* Sauver la fonction pour pouvoir gagner du temps par la suite.
* La metre en forme pour qu'elle puisse voyager a travers internet.
* La couvrir d'information annexe qui permettent de faire des statistiques.
"""

class Function:
    """
    |=============================|
    | Point d'entree d'une tache. |
    |=============================|
    """
    def __init__(self, func, *, func_id=None):
        """
        |===============================|
        | Encapsulation de la fonction. |
        |===============================|

        Parameters
        ----------
        :param func: Le pointeur de la fonction veritable PAS SERIALIZEE.
        :type func: callable
        :param func_id: Si il est connu, l'identifiant de cette fonction.
            Si il est omis, il est recalcule.
        :type func_id: str
        """
        raise NotImplementedError

    def save(self):
        """
        |=========================|
        | Enregistre la fonction. |
        |=========================|
        """
        raise NotImplementedError

    def to_dict(self):
        """
        |===============================|
        | Mise en forme pour le reseau. |
        |===============================|
        """
        raise NotImplementedError

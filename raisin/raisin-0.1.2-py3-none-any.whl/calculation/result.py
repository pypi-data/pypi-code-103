#!/usr/bin/env python3

"""
|=========================================|
| Representation du resultat d'un calcul. |
|=========================================|

Lorsque qu'une tache s'est executee sur un ordinater, il faut faire
parvenir le resultat vers l'utilisateur qui a lance ce calcul.

Ce fichier permet de metre cela en forme de facon optimale pour pouvoir:
* Charger un resultat deja existant.
* Enregistrer un resultat.
* Le metre en forme pour qu'il puisse voyager a travers internet.
* Le couvrir d'information annexe qui permettent de faire des statistiques.
"""

class Result:
    """
    |===================================|
    | Represente un 'packet' qui        |
    | contient le resultat d'une tache. |
    |===================================|
    """
    def __init__(self, result, *, res_id=None, dest_mac=None, stats=None):
        """
        |============================|
        | Encapsulation du resultat. |
        |============================|

        Parameters
        ----------
        :param result: Le resultat du calcul PAS SERIALIZE.
        :type result: object
        :param res_id: Si il est connu, l'identifiant du resultat.
            Si il est omis, il est recalcule.
        :type res_id: str
        :param dest_mac: Adresse MAC du destinataire, celui qui doit recevoir le resultat.
            Si il est omis, on considere que ce resultat est pour cet ordinateur la.
        :type dest_mac: str
        :param stats: Statistique sur le resultat, par example:
            * Temps de calcul, RAM utilisee, Sur quelle machine il a ete cree,
            Quel chemin il a empreinte a travers le reseau...
        :type stats: dict
        """
        raise NotImplementedError

    def save(self):
        """
        |============================================|
        | Enregistre ce resultat dans le disque dur. |
        |============================================|
        """
        raise NotImplementedError

    def to_dict(self):
        """
        |===============================|
        | Mise en forme pour le reseau. |
        |===============================|
        """
        raise NotImplementedError

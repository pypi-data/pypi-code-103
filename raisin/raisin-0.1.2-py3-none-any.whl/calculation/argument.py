#!/usr/bin/env python3

"""
|==============================================|
| Representation d'un argument pour une tache. |
|==============================================|

Losrqu'il faut executer un calcul, il faut en fait
executer une fonction avec des arguments. La classe
``Argument`` permet de representer l'un d'entre eux.
"""

class Argument:
	"""
	|=====================================|
	| Argument d'une ou plusieurs taches. |
	|=====================================|
	"""
	def __init__(self, arg, *, tasks, arg_id=None):
		"""
		|=================================|
		| Conextualisation de l'argument. |
		|=================================|

		Un argument n'a pas de sens lorsqu'il est seul,
		cela permet de donner un sens a son existance.

		Parameters
		----------
		:param arg: L'argment lui meme NON SERIALISE.
		:type arg: object
		:param tasks: C'est le dictionaire qui permet de savoir
			pour quelles taches cette argument intervient.
			Les clefs sont les identifiants des taches (task_id),
			et a chaque clef, est associer la position de l'argument ou son nom.
		:type tasks: dict
		:param arg_id: Si il est connu, l'identifiant de cet argument.
            Si il est omis, il est recalcule.
        :type func_id: str
        """
        raise NotImplementedError

    def save(self):
        """
        |========================|
        | Enregistre l'argument. |
        |========================|
        """
        raise NotImplementedError

    def to_dict(self):
        """
        |===============================|
        | Mise en forme pour le reseau. |
        |===============================|
        """
        raise NotImplementedError


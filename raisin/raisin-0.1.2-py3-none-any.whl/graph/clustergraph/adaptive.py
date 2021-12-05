#!/usr/bin/env python3

"""
|================================================|
| Interface qui permet au graphe de se modifier. |
|================================================|

* Permet de surcharger les noeuds et les arretes d'un graphe de facon
a ce qu'ils aient des attributs qui puissent se metre a jour et se propager
d'un objet a l'autre.
"""

import time


class Adaptive:
    """
    |===========================================|
    | Il faut le voir comme une interface java. |
    |===========================================|
    """
    def __init__(self):
        """
        * Doit etre appele dans l'initialisateur de la classe mere
        comme suit: ``Adaptive.__init__(self)``
        """
        self.attrs = {} # A chaque attribut associ sa derniere date de mise a jour.
        self.dead_attrs = {} # A chaque nom d'attribut mort, associ la date du premier tuer.
        self._creation_date = None # La premiere date de creation de cet objet.

    def add_attr(self, attr, value, *, date=None):
        """
        |================================================|
        | Ajoute ou met a jour un nouvel attribut prive. |
        |================================================|

        * Si l'attribut existe deja, il est ecrase.
        * Ajoute reelement dynamiquement l'attribut a self,
        qui est desormais accessible en faisant self.attr .

        :param attr: Nom de l'attribut.
        :type attr: str
        :param value: Valeur de l'attribut.
        :param date: Derniere date de mise a jour de cet attribut,
            time.time() par defaut.
        :type date: float
        """
        assert isinstance(attr, str)
        assert date is None or isinstance(date, float)

        if date is None:
            date = time.time()
        self.attrs[attr] = date
        setattr(self, attr, value) # Ajout reel de l'attribut

    def remove_attr(self, attr, *, date=None):
        """
        |======================================================================|
        | Supprime un attribut et fait en sorte que sa suppression se propage. |
        |======================================================================|

        :param attr: Nom de l'attribut.
        :type attr: str
        :param date: Premiere (la plus vielle) date de suppression de cet attribut,
            time.time() par defaut.
        :type date: float
        """
        assert attr in self.attrs, "L'attribut %s n'existe pas bien." % repr(attr)
        assert date is None or isinstance(date, float)

        if date is None:
            date = time.time()

        self.dead_attrs[attr] = date
        del self.attrs[attr]
        delattr(self, attr)

    def merge(self, other):
        """
        |==================================================================|
        | Met a jour les attributs de self en se basant sur ceux de other. |
        |==================================================================|

        * Ne change pas l'etat de 'other', affecte seulement self.
        """
        assert isinstance(other, Adaptive), "'other' n'est pas un objet adaptable."

        for attr in set(self.attrs) & set(other.attrs): # Pour tous les attributs communs.
            if other.attrs[attr] > self.attrs[attr]: # Si l'attribut de l'autre est plus recent.
                self.add_attr(attr, getattr(other, attr), date=other.attrs[attr]) # On ecrase la valeur actuelle de self.

        for attr in set(other.attrs) - set(self.attrs): # Pour tous les nouveaux attributs.
            self.add_attr(attr, getattr(other, attr), date=other.attrs[attr]) # On les ajoute sans se poser de questions

        for attr, date in other.dead_attrs.items(): # Pour chaque attribut qui ne doivent pas exister dans self.
            if attr in self.attrs: # Si cet attribut n'est pas supprime ici.
                if date > self.attrs[attr]: # Et qu'il a ete supprime plus recement:
                    self.remove_attr(attr, date=date)

    def init(self, elements=None):
        """
        |============================================================|
        | Initialisateur et serialisateur de l'adaptativite de self. |
        |============================================================|

        * Permet d'initialiser l'etat et la valeur des attributs adaptatifs de self.
        * Permet aussi de recuperer toutes les donnees nescessaires.

        :param elements: Le dictionaire renvoye par cette methode.
        :return: Le dictionaire qui contient le nessessaire a la reconstruction des
        attributs adaptables.
        """
        # Verifications.
        if elements is not None:
            assert isinstance(elements, dict)
            assert set(elements) == {"dead", "adaptive", "creation"}
            assert all(isinstance(attr, str) for attr in elements["dead"].keys())
            assert all(isinstance(date, float) for date in elements["dead"].values())
            assert all(isinstance(attr, str) for attr in elements["adaptive"].keys())
            assert all(isinstance(v, tuple) for v in elements["adaptive"].values())
            assert all(isinstance(date, float) for date, _ in elements["adaptive"].values())
            assert isinstance(elements["creation"], float)

        # Cas ecriture.
            for attr, (date, value) in elements["adaptive"].items():
                self.add_attr(attr, value, date=date)
            for attr, date in elements["dead"].items():
                if date > time.time() - 3600*24*365: # Si l'attribut n'existe plus depuis moins d'un ans.
                    self.dead_attrs[attr] = date # On en garde une trace.
            self._creation_date = elements["creation"]

        # Cas serialisation.
        return {
            "adaptive": {attr: (date, getattr(self, attr)) for attr, date in self.attrs.items()},
            "dead": self.dead_attrs,
            "creation": self._creation_date if self._creation_date is not None else time.time()}

    def is_older(self, other):
        """
        |==================================|
        | Compare la viellesse des objets. |
        |==================================|

        :return: True si self est plus vieux que other, True si self est plus jeune.
        :rtype: boolean
        """
        assert isinstance(other, Adaptive), "'other' n'est pas un objet adaptable."

        if self._creation_date is None:
            return True
        if other._creation_date is None:
            return False
        return self._creation_date < other._creation_date

"""Module relatif aux structures de données."""
from collections import deque


class Pile:
    """Classe représentant une pile"""

    def __init__(self):
        """On initialise la pile vide.

        L'attribut _data est de type list
        """
        self._data = []

    def empiler(self, élément):
        """Ajoute l'élément au sommet de la pile."""
        self._data.append(élément)

    def dépiler(self):
        """Retire l'élément au sommet de la pile et le renvoie."""
        return self._data.pop()

    def est_vide(self):
        """Renvoie `True` si la pile est vide et `False` sinon."""
        return not self._data

    def sommet(self):
        """Renvoie l'élément présent au sommet de la pile, et `None` si la pile est
        vide."""
        if self.est_vide():
            return None
        return self._data[-1]

    def __repr__(self):
        """Représente la pile verticalement"""
        # si la pile est vide on la dessine quand même
        if self.est_vide():
            N = 3
            txt = "|   | <- Sommet\n"
        else:
            # cherche la plus longue valeur de la pile
            N = 2 + max([len(str(x)) for x in self._data])
            txt = ""
            for i, e in enumerate(self._data[::-1]):
                txt += "|{:^{N}}|".format(str(e), N=N)
                if i == 0:
                    txt += " <- Sommet\n"
                else:
                    txt += "\n"
        # Tiret bas
        txt += chr(8254) * (N + 2)
        txt += "\n{:^{N}}\n".format("PILE", N=N + 2)
        return txt


class File:
    """Classe représentant une file"""

    def __init__(self):
        """On initialise la file vide.

        L'attribut _data est de type collections.deque
        """
        self._data = deque()

    def enfiler(self, élément):
        """Ajoute l'élément à la queue la file."""
        self._data.appendleft(élément)

    def défiler(self):
        """Retire l'élément à la tête de la file et le renvoie."""
        return self._data.pop()

    def est_vide(self):
        """Renvoie `True` si la file est vide et `False` sinon."""
        return not self._data

    def tête(self):
        """Renvoie l'élément présent à la tête de la file, et `None` si la file est
        vide."""
        if self.est_vide():
            return None
        return self._data[-1]

    def __repr__(self):
        """Représente la file horizontalement vers la droite"""
        # cherche la plus longue valeur de la pile
        txt_0 = "Queue -> | "
        txt_1 = " | ".join([str(e) for e in self._data])
        txt_2 = " | -> Tête"

        # contours
        CONTOUR_UP = (
            " " * (len(txt_0) - 2) + "_" * (len(txt_1) + 4) + " " * (len(txt_2) - 2)
        )
        CONTOUR_DOWN = (
            " " * (len(txt_0) - 2)
            + chr(8254) * (len(txt_1) + 4)
            + " " * (len(txt_2) - 2)
        )

        # Affiche FILE au milieu en dessous
        LABEL = "\n{:^{N}}\n".format("FILE", N=len(CONTOUR_DOWN))
        return CONTOUR_UP + "\n" + txt_0 + txt_1 + txt_2 + "\n" + CONTOUR_DOWN + LABEL

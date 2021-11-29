
from LinAlgebraPy.matrices.matrix import *
from LinAlgebraPy.vectors.vector import *


def checkIfIterator(i):
    try:
        iterator = iter(i)
    except TypeError:
        raise TypeError(i, ' is not iterable ')


class SetM(set):
    def __init__(self, args=None):
        if args == None:
            args = []
        accepted = [Matrix, Vector]
        hashable, matrices, vectors = [], [], []
        for i in args:
            hashfori = (i).__hash__
            typeofI = type(i)
            if hashfori == None and typeofI not in accepted:
                raise TypeError("unhashable type : '", typeofI,
                                "' or it's not a Matrix nor a Vector")
            else:
                if hashfori != None:
                    hashable.append(i)
                elif typeofI == Matrix:
                    elem = i.elements
                    matrices.append(tuple((tuple(i) for i in elem)))
                elif typeofI == Vector:
                    elem = i.elements
                    if i.isLine:
                        vectors.append(tuple(elem))
                    else:
                        vectors.append(tuple([tuple([i[0]]) for i in elem]))
        hashable = list(set(hashable))
        vectors = list(set(vectors))
        matrices = list(set(matrices))
        lengthVectors = len(vectors)
        for i in range(lengthVectors):
            if type(vectors[i][0]) == tuple:
                vectors[i] = Vector([list(j) for j in vectors[i]])
            else:
                vectors[i] = Vector(vectors[i])
        lengthMatrices = len(matrices)
        for i in range(lengthMatrices):
            matrices[i] = Matrix([list(j) for j in matrices[i]])
        elements = hashable + vectors + matrices
        self.elements = elements
        self.cardinal = len(elements)
        self.isEmpty = len(elements) == 0
        self.__hashable = hashable
        self.__vectors = vectors
        self.__matrices = matrices

    def __updateSetM(self, elements):
        self.__dict__ = SetM(elements).__dict__

    def __iter__(self):
        self.iterations = -1
        return self

    def __next__(self):
        elements = self.elements
        self.iterations += 1
        if self.iterations < self.cardinal:
            return elements[self.iterations]
        else:
            raise StopIteration

    def __repr__(self) -> str:
        string = str(self.elements)
        return "\n SetM(" + string[1:len(string)-1] + ') \n'

    def __str__(self) -> str:
        string = '\n {'
        elem = self.elements
        length = len(elem)
        if len(elem) == 0:
            return '{}'
        for i in range(length):
            if type(elem[i]) == str and elem[i][0] != "'":
                string += "\'{}\',".format(elem[i])
            else:
                string += ' {},'.format(elem[i])

        string = string[:len(string)-1] + '}'
        return string

    def __len__(self) -> int:
        return self.cardinal

    def __contains__(self, o: object) -> bool:
        if type(o) == Vector:
            for i in self.__vectors:
                try:
                    if o == i:
                        return True
                except:
                    continue
            return False
        elif type(o) == Matrix:
            for i in self.__matrices:
                try:
                    if o == i:
                        return True
                except:
                    continue
            return False
        else:
            return o in self.__hashable

    def add(self, var) -> None:
        newElement = self.elements
        newElement.append(var)
        self.__updateSetM(newElement)

    def clear(self):
        self.elements = []
        self.__updateSetM(self.elements)

    def copy(self):
        newelements = self.elements
        return SetM(newelements)

    def remove(self, element) -> None:
        listOfElements = self.elements
        if element in self:
            listOfElements.remove(element)
        else:
            raise KeyError(element)
        self.__updateSetM(listOfElements)

    def discard(self, element) -> None:
        listOfElements = self.elements
        if element in self:
            listOfElements.remove(element)
        self.__updateSetM(listOfElements)

    def pop(self):
        res = self.elements.pop()
        self.__updateSetM(self.elements)
        return res

    def update(self, *s):
        newelements = self.elements
        for i in s:
            checkIfIterator(i)
            for j in i:
                newelements.append(j)
        self.__updateSetM(newelements)

    def union(self, *s):
        newelements = self.elements.copy()
        for i in s:
            checkIfIterator(i)
            for j in i:
                newelements.append(j)
        return SetM(newelements)

    def intersection(self, *s):
        newelements = self.elements
        intersect = []
        for i in s:
            checkIfIterator(i)
            for j in i:
                if j in newelements:
                    intersect.append(j)
        return SetM(intersect)

    def intersection_update(self, *s) -> None:
        newelements = self.elements
        intersect = []
        for i in s:
            checkIfIterator(i)
            for j in i:
                if j in newelements:
                    intersect.append(j)
        self.__updateSetM(intersect)

    def difference(self, *s):
        elements = self.elements.copy()
        for i in s:
            checkIfIterator(i)
            for j in i:
                if j in elements:
                    elements.remove(j)
        return SetM(elements)

    def difference_update(self, *s) -> None:
        elements = self.elements
        for i in s:
            checkIfIterator(i)
            for j in i:
                if j in elements:
                    elements.remove(j)
        self.__updateSetM(elements)

    def isdisjoint(self, s) -> bool:
        return len(self.intersection(s)) == 0

    def issubset(self, s) -> bool:
        checkIfIterator(s)
        elements = self.elements
        for j in elements:
            if j not in s:
                return False
        return True

    def issuperset(self, s) -> bool:
        checkIfIterator(s)
        return s.issubset(self)

    def symmetric_difference(self, s):
        checkIfIterator(s)
        set1 = self.difference(s)
        set2 = s.difference(self)
        return set1.union(set2)

    def symmetric_difference_update(self, s) -> None:
        set1 = self.difference(s)
        set2 = s.difference(self)
        set3 = set1.union(set2)
        self.__updateSetM(set3.elements)

    def __and__(self, s):
        return SetM(s.elements)

    def __iand__(self, s):
        self.__and__(s)

    def __or__(self, s):
        return SetM(self.elements)

    def __ior__(self, s):
        self.__or__(s)

    def __xor__(self, s):
        return self.symmetric_difference(s)

    def __ixor__(self, s):
        self.__xor__(s)

    def __eq__(self, o: object) -> bool:
        if type(o) == SetM:
            return self.elements == o.elements
        else:
            return self == o

    def __ne__(self, o: object) -> bool:
        return not self == o

    def __le__(self, s) -> bool:
        return self.issubset(s)

    def __ge__(self, s) -> bool:
        return self.issuperset(s)

    def __lt__(self, s) -> bool:
        return self.issubset(s) and s != self

    def __gt__(self, s) -> bool:
        return self.issuperset(s) and s != self



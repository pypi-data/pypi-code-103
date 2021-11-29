
from LinAlgebraPy.sets.generalSet import *
from LinAlgebraPy.matrices import *
from LinAlgebraPy.vectors import *
from LinAlgebraPy.vectors import vector


def superSet(hasComplex, vectorDim) -> str:
    superscript = str.maketrans(
        '0 1 2 3 4 5 6 7 8 9', '\u2070 \u00b9 \u00b2 \u00b3 \u2074 \u2075 \u2076 \u2077 \u2078 \u2079')
    if hasComplex:
        return '\u2102{}'.format(vectorDim).translate(superscript)
    else:
        return '\u211D{}'.format(vectorDim).translate(superscript)


class SetVectors(SetM):
    def __init__(self, args=None):
        if args == None:
            args = []
        vectors = []
        firstdim = (0, 0)
        if args != [] and type(args[0]) == Vector:
            firstone = args[0]
            if firstone.isLine:
                firstone = firstone.transpose()
            firstdim = firstone.dim
        isComplexVector = False
        for i in args:
            typeofI = type(i)
            if typeofI != Vector:
                raise TypeError("it's not a vector: ", i, ' : ', typeofI)
            else:
                if i.isLine:
                    i = i.transpose()
                if firstdim != i.dim:
                    raise TypeError(
                        'The dimensions of the vectors are not the same')

                elem = i.elements
                vectors.append(tuple([tuple([i[0]]) for i in elem]))
        vectors = list(set(vectors))
        lengthVectors = len(vectors)
        for i in range(lengthVectors):
            vectors[i] = Vector([list(j) for j in vectors[i]])
            if vectors[i].isComplex:
                isComplexVector = True
        self.elements = vectors
        self.cardinal = len(vectors)
        self.isEmpty = len(vectors) == 0
        self.__vectorDim = firstdim[0]
        self.__hasComplex = isComplexVector
        self.superSet = superSet(self.__hasComplex, self.__vectorDim)

    def __updateSetVectors(self, elements):
        self.__dict__ = SetVectors(elements).__dict__

    def __contains__(self, o: Vector) -> bool:
        for i in self.elements:
            try:
                if o == i:
                    return True
            except:
                continue
        return False

    def add(self, var: Vector) -> None:
        newElement = self.elements
        newElement.append(var)
        self.__updateSetVectors(newElement)

    def clear(self):
        self.elements = []
        self.__updateSetVectors(self.elements)

    def copy(self):
        return SetVectors(self.elements)

    def remove(self, element: Vector) -> None:
        listOfElements = self.elements
        if element in self:
            listOfElements.remove(element)
        else:
            raise KeyError(element)
        self.__updateSetVectors(listOfElements)

    def discard(self, element: Vector) -> None:
        listOfElements = self.elements
        if element in self:
            listOfElements.remove(element)
        self.__updateSetVectors(listOfElements)

    def pop(self):
        res = self.elements.pop()
        self.__updateSetVectors(self.elements)
        return res

    def update(self, *s):
        newelements = self.elements
        for i in s:
            checkIfIterator(i)
            for j in i:
                newelements.append(j)
        self.__updateSetVectors(newelements)

    def union(self, *s):
        newelements = self.elements.copy()
        for i in s:
            checkIfIterator(i)
            for j in i:
                newelements.append(j)
        return SetVectors(newelements)

    def intersection(self, *s):
        newelements = self.elements
        intersect = []
        for i in s:
            checkIfIterator(i)
            for j in i:
                if j in newelements:
                    intersect.append(j)
        return SetVectors(intersect)

    def intersection_update(self, *s) -> None:
        newelements = self.elements
        intersect = []
        for i in s:
            checkIfIterator(i)
            for j in i:
                if j in newelements:
                    intersect.append(j)
        self.__updateSetVectors(intersect)

    def difference(self, *s):
        elements = self.elements.copy()
        for i in s:
            checkIfIterator(i)
            for j in i:
                if j in elements:
                    elements.remove(j)
        return SetVectors(elements)

    def difference_update(self, *s) -> None:
        elements = self.elements
        for i in s:
            checkIfIterator(i)
            for j in i:
                if j in elements:
                    elements.remove(j)
        self.__updateSetVectors(elements)

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
        self.__updateSetVectors(set3.elements)

    def __and__(self, s):
        return SetVectors(s.elements)

    def __iand__(self, s):
        self.__and__(s)

    def __or__(self, s):
        return SetVectors(self.elements)

    def __ior__(self, s):
        self.__or__(s)

    def __xor__(self, s):
        return self.symmetric_difference(s)

    def __ixor__(self, s):
        self.__xor__(s)

    def __eq__(self, o: object) -> bool:
        if type(o) == SetVectors:
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

    def isLinearlyIndependent(self) -> bool:
        if self.isEmpty:
            return False
        return Matrix(self.elements).rank() == len(self)

    def isBasis(self) -> bool:
        if self.isEmpty:
            return False
        return self.isLinearlyIndependent() and len(self) == self.__vectorDim

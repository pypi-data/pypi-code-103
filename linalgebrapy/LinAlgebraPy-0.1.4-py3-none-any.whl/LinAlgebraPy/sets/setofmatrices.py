from LinAlgebraPy.matrices import *
from LinAlgebraPy.vectors import *
from LinAlgebraPy.sets.generalSet import *


def superSet(hasComplex, matrixDim) -> str:
    if hasComplex:
        return u'\U0001d544'+'(\u2102) ({},{})'.format(matrixDim[0], matrixDim[1])
    else:
        return u'\U0001d544' + '(\u211D) ({},{})'.format(matrixDim[0], matrixDim[1])


class SetMatrices(SetM):
    def __init__(self, args=None):
        if args == None:
            args = []
        matrices = []
        firstdim = (0, 0)
        if args != [] and type(args[0]) == Matrix:
            firstone = args[0]
            firstdim = firstone.dim
        isComplexMatrix = False
        for i in args:
            typeofI = type(i)
            if typeofI != Matrix:
                raise TypeError("it's not a Matrix: ", i, ' : ', typeofI)
            else:
                if firstdim != i.dim:
                    raise TypeError(
                        'The dimensions of the matrices are not the same')
                elem = i.elements
                matrices.append(tuple((tuple(i) for i in elem)))
        matrices = list(set(matrices))
        lengthMatrices = len(matrices)
        for i in range(lengthMatrices):
            matrices[i] = Matrix([list(j) for j in matrices[i]])
            if matrices[i].isComplex:
                isComplexMatrix = True
        self.elements = matrices
        self.cardinal = len(matrices)
        self.isEmpty = len(matrices) == 0
        self.__matrixDim = firstdim
        self.__hasComplex = isComplexMatrix
        self.superSet = superSet(self.__hasComplex, self.__matrixDim)

    def __updateSetMatrices(self, elements):
        self.__dict__ = SetMatrices(elements).__dict__

    def __contains__(self, o: Matrix) -> bool:
        for i in self.elements:
            try:
                if o == i:
                    return True
            except:
                continue
        return False

    def add(self, var: Matrix) -> None:
        newElement = self.elements
        newElement.append(var)
        self.__updateSetMatrices(newElement)

    def clear(self):
        self.elements = []
        self.__updateSetMatrices(self.elements)

    def copy(self):
        return SetMatrices(self.elements)

    def remove(self, element: Matrix) -> None:
        listOfElements = self.elements
        if element in self:
            listOfElements.remove(element)
        else:
            raise KeyError(element)
        self.__updateSetMatrices(listOfElements)

    def discard(self, element: Matrix) -> None:
        listOfElements = self.elements
        if element in self:
            listOfElements.remove(element)
        self.__updateSetMatrices(listOfElements)

    def pop(self):
        res = self.elements.pop()
        self.__updateSetMatrices(self.elements)
        return res

    def update(self, *s):
        newelements = self.elements
        for i in s:
            checkIfIterator(i)
            for j in i:
                newelements.append(j)
        self.__updateSetMatrices(newelements)

    def union(self, *s):
        newelements = self.elements.copy()
        for i in s:
            checkIfIterator(i)
            for j in i:
                newelements.append(j)
        return SetMatrices(newelements)

    def intersection(self, *s):
        newelements = self.elements
        intersect = []
        for i in s:
            checkIfIterator(i)
            for j in i:
                if j in newelements:
                    intersect.append(j)
        return SetMatrices(intersect)

    def intersection_update(self, *s) -> None:
        newelements = self.elements
        intersect = []
        for i in s:
            checkIfIterator(i)
            for j in i:
                if j in newelements:
                    intersect.append(j)
        self.__updateSetMatrices(intersect)

    def difference(self, *s):
        elements = self.elements.copy()
        for i in s:
            checkIfIterator(i)
            for j in i:
                if j in elements:
                    elements.remove(j)
        return SetMatrices(elements)

    def difference_update(self, *s) -> None:
        elements = self.elements
        for i in s:
            checkIfIterator(i)
            for j in i:
                if j in elements:
                    elements.remove(j)
        self.__updateSetMatrices(elements)

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
        self.__updateSetMatrices(set3.elements)

    def __and__(self, s):
        return SetMatrices(s.elements)

    def __iand__(self, s):
        self.__and__(s)

    def __or__(self, s):
        return SetMatrices(self.elements)

    def __ior__(self, s):
        self.__or__(s)

    def __xor__(self, s):
        return self.symmetric_difference(s)

    def __ixor__(self, s):
        self.__xor__(s)

    def __eq__(self, o: object) -> bool:
        if type(o) == SetMatrices:
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
        matriceList = []
        for i in self.elements:
            matriceList.append(Vector(i.elements1d).transpose())
        return Matrix(matriceList).rank() == len(self)

    def isBasis(self) -> bool:
        if self.isEmpty:
            return False
        return self.isLinearlyIndependent() and len(self) == (self.__matrixDim[0]*self.__matrixDim[1])

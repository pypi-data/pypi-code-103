from cmath import cos, exp, pi, sqrt
from typing import List, Sequence, Tuple, Union

# Problem in only type


def onlytype(elements, *types):
    for i in elements:
        if type(i) not in types:
            return False
    return True


def magnitude(vector):
    res = 0
    if vector.isComplex:
        for i in vector:
            res += i*(i).conjugate()
        return sqrt(res)
    else:
        for i in vector:
            res += abs(i**2)
        return sqrt(res)


class Vector():

    def __init__(self, *coord: Union[int, float, complex, List[Union[int, float, complex]], Tuple[Union[int, float, complex]]]):

        length = len(coord)
        types = [float, int, complex, list, tuple]
        elements = []

        typeIndexCoordList = onlytype(coord, list, tuple)
        # returns True if all coord[i] is list or tuple

        i = 0
        while i < length:  # looping through coord
            indexCoord = coord[i]
            if type(indexCoord) in types:
                if type(indexCoord) == tuple:
                    # Input : Vector(([x],[y],[z])) Output: elements= [[x],[y],[z]]
                    # Input : Vector((x,),(y,),(z,)])) Output: elements= [[x],[y],[z]]
                    indexCoord = list(indexCoord)
                if type(indexCoord) in types[0:3]:
                    # Input : Vector(x,y,z) Output: elements= [x,y,z]
                    elements.append(indexCoord)
                # if coord[i] is a list and if all coord[i] are lists
                elif type(indexCoord) == list and typeIndexCoordList:
                    # onlylist : if all indexCoord[j] are lists
                    onlylist = onlytype(indexCoord, list)
                    # onlycomplex:  if all indexCoord[j] are [int, float, complex]
                    onlycomplex = onlytype(indexCoord, int, float, complex)
                    # Input : Coord([x,y,z])        "indexCoord=[x,y,z]         " Output: elements= [x,y,z]  Or is for Coord[[x]] Output: elemnents=[x]
                    if (onlycomplex and len(indexCoord) != 1) or (len(indexCoord) == len(coord) and onlycomplex):
                        elements += indexCoord
                    # Input : Coord([[x],[y],[z]])  "indexCoord=[[x],[y],[z]] " Output: elements= [[x],[y],[z]]
                    elif onlycomplex and len(indexCoord) == 1:
                        elements += [indexCoord]

                    # Input : Coord([x],[y],[z])    "indexCoord= [x] "          Output: elements= [[x],[y],[z]]
                    elif onlylist:
                        for j in indexCoord:
                            if type(j[0]) not in types[0:3] or len(j) != 1:
                                raise SyntaxError('Your input is not right')
                            else:
                                elements += [j]
                    else:
                        raise ValueError(
                            "Something isn't right. Check your input")

            else:
                raise TypeError(
                    "Arguments allowed are float,int,complex,list,tuple ")
            i += 1
        isComplex = False
        self.isColumn = onlytype(elements, list)
        self.isLine = onlytype(elements, float, int, complex)
        self.elements = elements
        if self.isColumn:
            self.elements1d = [i[0] for i in elements]
            self.dim = (len(self.elements), 1)
        elif self.isLine:
            self.elements1d = elements
            self.dim = (1, len(self.elements))
        else:
            raise ValueError('Something isn\'t right')
        newelements = []
        for elem in self:
            instance = type(elem)
            if instance != complex and elem <= 1e-14 and elem >= -1e-14:  # changed type in echelon with N and Echelon
                elem = 0
            elif instance == complex:
                isComplex = True
                real = complex(elem).real
                imag = complex(elem).imag
                comparereal = (real <= 1e-13 and real >= -1e-13)
                compareimag = (imag <= 1e-13 and imag >= -1e-13)
                if comparereal and compareimag:
                    elem = 0
                elif compareimag:
                    elem = round(real, 13)
                elif comparereal:
                    elem = round(imag, 13)*1j
            if self.isColumn:
                newelements += [[elem]]
            else:
                newelements += [elem]
        if self.isColumn:
            self.elements1d = [i[0] for i in newelements]
        else:
            self.elements1d = newelements
        self.elements = newelements
        self.isComplex = isComplex
        self.magn = magnitude(self)

    def __updateVector(self, elements):
        self.__dict__ = Vector(elements).__dict__

    def __iter__(self):
        self.iterations = -1
        return self

    def __next__(self):
        (m, n) = self.dim
        elements = self.elements1d
        self.iterations += 1
        if self.iterations < len(elements):
            return elements[self.iterations]
        else:
            raise StopIteration

    def __repr__(self):
        if self.isLine:
            return str(tuple(self.elements))
        else:
            string = '\n'
            for i in self.elements:
                string += '( {} ) \n'.format(i[0])
            return string

    def __getitem__(self, i):
        if self.isLine:
            return self.elements[i]
        else:
            return self.elements[i][0]

    def __setitem__(self, i, val):
        elem = self.elements
        instance = type(val)
        if instance != complex and val <= 1e-14 and val >= -1e-14:  # changed type in echelon with N and Echelon
            val = 0
        elif instance == complex:
            real = complex(val).real
            imag = complex(val).imag
            comparereal = (real <= 1e-13 and real >= -1e-13)
            compareimag = (imag <= 1e-13 and imag >= -1e-13)
            if comparereal and compareimag:
                val = 0
            elif compareimag:
                val = round(real, 14)
            elif comparereal:
                val = round(imag, 14)*1j

        if self.isLine:
            if len(elem) == 0:
                elem.append(val)
            elif i < len(elem) and i >= 0:
                elem[i] = val
            else:
                raise IndexError("Index out of range")
        else:
            if len(elem) == 0:
                elem.append([val])
            elif i < len(elem) and i >= 0:
                elem[i] = [val]
            else:
                raise IndexError("Index out of range")
        self.__updateVector(elem)

    def __add__(self, var):
        types = [list, tuple, Vector]
        if type(var) in types:
            if type(var) == Vector:
                if self.dim != var.dim:
                    raise ValueError(
                        "Vectors cannot add with different dimensions.")
                else:
                    length = len(self.elements)
                    v1, v2 = self.elements, var.elements
                    if self.isLine:
                        elements = [v1[i] + v2[i] for i in range(length)]
                    else:
                        elements = [[v1[i][0] + v2[i][0]]
                                    for i in range(length)]
                    vect = Vector(elements)
                    return vect
            elif type(var) == list:
                if self.isLine:
                    elem = self.elements + var
                else:
                    elem = self.elements + [var]
                vect = Vector(elem)
                return vect
            else:
                if self.isLine:
                    elem = self.elements + list(var)
                else:
                    elem = self.elements + [list(var)]
                vect = Vector(elem)
                return vect
        else:
            raise TypeError("Arguments allowed for adding are list and tuple ")

    def __radd__(self, var):
        return self.__add__(var)

    def __IADD__(self, var):
        return self.__add__(var)

    def __sub__(self, var):
        if type(var) == Vector:
            (m1, n1) = self.dim
            length = len(self.elements)
            v1, v2 = self.elements, var.elements
            if self.isLine and var.isLine:
                elements = [v1[i]-v2[i] for i in range(length)]
                vect = Vector(elements)
            elif self.isColumn and var.isColumn:
                if m1 == 1:
                    elements = [v1[0][0]-v2[0][0]]
                else:
                    elements = [[v1[i][0]-v2[i][0]] for i in range(length)]
                vect = Vector(elements)
            else:
                raise ValueError(
                    "For substraction, the values shoul be two vectors and the same dimension")
            return vect
        else:
            raise TypeError("Substraction should be with another Vector")

    def __ISUB__(self, var):
        return self.__sub__(var)

    def __rsubb__(self, var):
        return self.__sub__(var)

    def __mul__(self, var):
        (m1, n1) = self.dim
        if type(var) == Vector:
            (m2, n2) = var.dim
            res = 0
            if n1 == m2 and self.isLine:
                for i in range(n1):
                    res += self.elements[i]*var.elements[i][0]
                return Vector(res)
            else:
                raise ValueError(
                    "Multiplying two vectors cannot be done if i of the first vector is not equal to j of the second vector or the Product returns a matrix")
        else:
            v1 = self.elements
            length = len(self.elements)
            if self.isLine:
                vect = Vector([v1[i]*var for i in range(length)])
            else:
                if m1 == 1:
                    vect = Vector([v1[0][0]*var])
                else:
                    vect = Vector([[v1[i][0]*var] for i in range(length)])
            return vect

    def __rmul__(self, var):
        return self.__mul__(var)

    def __eq__(self, other):
        if type(other) != Vector:
            return False
        elif self.dim != other.dim:
            return False
        else:
            return self.elements1d == other.elements1d

    def normalize(self):
        magnitude = self.magn
        if magnitude == 0:
            raise ZeroDivisionError("Cannot normalize a zero-vector")
        else:
            vect = Vector(self.elements)
            return vect*(1/magnitude)

    def transpose(self):
        elem = self.elements
        if self.isLine:
            vect = Vector([[i] for i in elem])
        else:
            vect = Vector([i[0] for i in elem])
        return vect

    def isNul(self):
        if self.isLine:
            for i in self.elements:
                if i != 0:
                    return False
        else:
            for i in self.elements:
                if i[0] != 0:
                    return False
        return True


def scalarproduct(vect1, vect2):
    if type(vect1) == Vector and type(vect2) == Vector:
        (m1, n1) = vect1.dim
        (m2, n2) = vect2.dim
        res = 0
        if m1 == m2 and vect1.isColumn and vect2.isColumn:
            for i in range(m1):
                res += vect1.transpose().elements[i]*vect2.elements[i][0]
            return res
        elif n1 == n2 and vect1.isLine and vect2.isLine:
            for i in range(n1):
                res += vect1.transpose().elements[i][0]*vect2.elements[i]
            return res
        else:
            raise ValueError("The vectors should be the same Dimension")
    else:
        raise ValueError("Only vectors allowed for scalar product")


def orthogonalVectors(vectors):
    length = len(vectors)
    for i in range(length):
        if type(vectors[i]) == Vector:
            for j in range(i+1, length):
                if scalarproduct(vectors[i], vectors[j]) != 0:
                    return False
        else:
            raise TypeError(
                "Arguments should be only vectors with same number of elements")
    return True


def indexPivot(vector):
    i = vector.elements
    for j in range(len(i)):
        if i[j] != 0:
            return j
    return -1


def indexPivotColumn(vector):
    i = vector.elements
    for j in range(len(i)):
        if i[j][0] != 0:
            return j
    return -1


def colinear(vect1, vect2):
    if vect1.isColumn and vect2.isColumn:
        vect1 = vect1.transpose()
        vect2 = vect2.transpose()
    elif not(vect1.isColumn ^ vect2.isLine):
        raise ValueError('Not the same dimensions')
    (n, m) = vect1.dim
    vec1 = vect1.elements
    vec2 = vect2.elements
    i = 0
    while i < m:
        if (vec1[i] != 0) ^ (vec2[i] != 0):
            return False
        elif vec2[i] != 0 and vec1[i] != 0:
            vect1 *= (1/vec1[i])
            vect2 *= (1/vec2[i])
            return vect1 == vect2
        elif vect1.isNul() and vect2.isNul():
            return True
        i += 1

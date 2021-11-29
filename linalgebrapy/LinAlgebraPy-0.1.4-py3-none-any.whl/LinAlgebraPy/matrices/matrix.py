from random import *
from typing import Iterator, List, Mapping, Sequence, Set, Tuple, TypeVar, Union
from LinAlgebraPy.vectors.vector import Vector, colinear, indexPivot, indexPivotColumn
from LinAlgebraPy.matrices.matrixfunc import onlytypeM, sortList, sortMatrix
from cmath import exp, log, sqrt, pi


def Identity(n: int):
    """Identity Matrix

    Args:
        n (integer): Dimension of the square matrix

    Returns:
        [Matrix]: Identity Matrix (n x n)
    """
    lis = []
    elem = []
    for i in range(n):
        for j in range(n):
            if i != j:
                lis.append(0)
            else:
                lis.append(1)
        elem.append(lis)
        lis = []
    return Matrix(elem)


class Matrix():
    """Matrix

        Args:
            This Matrix can take only one type of arguments:
            -2 integers : it will create a zero Matrix with dimensions (i,j)
            -Vectors (Column or Line): Vectors should have the same dimension and same type of Vectors
            -List of vectors : Vectors in the List should have the same dimension and same type of Vectors
            -Tuples: Tuples should have the same dimensions and contain only numbers (int,float,complex)
            -List (only numbers) : It will add every list as a line in the Matrix and should have the same length
            -List of lists:  List of lists (only numbers) as seen before

        To make some changes to the Matrix (set):
            Two types of changes:
            (i index of line and j index of column)
            1)  To change an entry:
                Example:
                    M[i,j]=2  (It will set 2 to the entry  at i line and j column)

            2) To change a line or a column:
                Example for changing a line:
                    M['L',i]=Vector   (Vector should be a line and have the same dimensions of the lines in the Matrix)
                Example for changing a vector:
                    M['C',j]=Vector   (Vector should be a column and have the same dimensions of the columns in the Matrix)

        To get an entry or a Vector from a Matrix (get):
            Two types of get:
            1) M[i,j]    ,it will return an element of type int or float or complex

            2) M['L',i]  ,it will return a the Line in j position as a Vector Line
               M['C',j] , it will return the Column in j position as a Vector Column

    """

    def __init__(self, *args: Union[int, Vector, List[Vector], List[Union[int, float, complex]], List[List[Union[int, float, complex]]], Tuple[Union[int, float, complex]]]):
        elementsM = []
        onlylist = onlytypeM(args, list)
        onlyvector = onlytypeM(args, Vector)
        onlytuple = onlytypeM(args, tuple)
        types = [float, int, complex, list, tuple, Vector]
        length = len(args)
        i = 0

        if len(args) == 2 and type(args[0]) == int and type(args[1]) == int:
            (m, n) = args
            elementsM = [[0 for j in range(n)] for k in range(m)]
        elif onlylist:
            if type(args[0][0]) in types[0: 3]:
                while i < length:
                    c = args[i]
                    elementsM.append(c)
                    i += 1
            elif type(args[0][0]) == list:
                while i < length:
                    c = args[i]
                    elementsM += c
                    i += 1
            elif type(args[0][0]) == Vector:
                ArgsIn = args[0]
                onlyVectorIn = onlytypeM(ArgsIn, Vector)
                len2 = len(ArgsIn)
                if onlyVectorIn == len2 and onlyVectorIn != 0:
                    while i < len2:
                        c = ArgsIn[i]
                        elementsM.append(c.elements)
                        i += 1
                elif onlyVectorIn == sqrt(2)*len2 and onlyVectorIn != 0:
                    (m, n) = ArgsIn[0].dim
                    while i < m:
                        elementsM += [[j.elements[i][0] for j in ArgsIn]]
                        i += 1
            else:
                raise ValueError(
                    'Type of Arguments allowed are in this list => [float,int,complex,list,Vector]')
        elif onlytuple:
            while i < length:
                c = args[i]
                elementsM += [list(c)]
                i += 1
        elif onlyvector == length and onlyvector != 0:
            while i < length:  # Problem in Vectors Column
                c = args[i]
                elementsM += [c.elements]
                i += 1
        elif onlyvector == sqrt(2)*length and onlyvector != 0:
            (m, n) = args[0].dim
            while i < m:
                elementsM += [[j.elements[i][0] for j in args]]
                i += 1
        else:
            raise TypeError("Arguments allowed are list, tuple and Vector ")
        isComplex = False
        self.elements = elementsM
        self.dim = (len(self.elements), len(self.elements[0]))
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                elem = elementsM[i][j]
                if type(elem) in types[0:3]:
                    instance = type(elem)
                    if instance != complex and elem <= 1e-13 and elem >= -1e-13:  # changed type in echelon with N and Echelon
                        elementsM[i][j] = 0
                    elif instance == complex:
                        isComplex = True
                        real = complex(elementsM[i][j]).real
                        imag = complex(elementsM[i][j]).imag
                        comparereal = (real <= 1e-13 and real >= -1e-13)
                        compareimag = (imag <= 1e-13 and imag >= -1e-13)
                        if comparereal and compareimag:
                            elementsM[i][j] = 0
                        elif compareimag:
                            elementsM[i][j] = round(real, 14)
                        elif comparereal:
                            elementsM[i][j] = round(imag, 14)*1j
                else:
                    raise ValueError(
                        "1-Arguments allowed are list, tuple , int, complex, float and Vector \n 2-You can't combine Vector , tuple and list together . It should be unique")
        self.elements = elementsM
        self.isSquared = self.dim[0] == self.dim[1]
        self.elements1d = [x[y] for x in elementsM for y in range(len(x))]
        self.isComplex = isComplex

    def __updateMatrix(self, elements):
        self.__dict__ = Matrix(elements).__dict__

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

    def __add__(self, mat):
        """Adding a Matrix

        Args:
            mat (Matrix): The two added Matrix should have the same Dimensions

        Raises:
            ValueError: A matrix can only be added to another matrix if the two matrices have the same dimensions .

        Returns:
            [Matrix]: Addition of the Matrix
        """
        elements = self.elements
        if type(mat) == Matrix and mat.dim == self.dim:
            elemA = []
            lis = []
            for i in range(len(elements)):
                for j in range(len(elements[0])):
                    lis.append(elements[i][j]+mat.elements[i][j])
                elemA.append(lis)
                lis = []
            return Matrix(elemA)
        else:
            raise ValueError(
                "A matrix can only be added to another matrix if the two matrices have the same dimensions .")

    def __radd__(self, mat):
        return self.__add__(mat)

    def __IADD__(self, mat):
        return self.__add__(mat)

    def __sub__(self, mat):
        """Substitution

        Args:
            mat (Matrix): The two matrices should have the same dimensions

        Raises:
            ValueError: A matrix can only be added to another matrix if the two matrices have the same dimensions .

        Returns:
            [Matrix]: Substitution Matrix
        """
        elements = self.elements
        if type(mat) == Matrix and mat.dim == self.dim:
            elemA = []
            lis = []
            for i in range(len(elements)):
                for j in range(len(elements[0])):
                    lis.append(elements[i][j]-mat.elements[i][j])
                elemA.append(lis)
                lis = []
            return Matrix(elemA)
        else:
            raise ValueError(
                "A matrix can only be added to another matrix if the two matrices have the same dimensions .")

    def __ISUB__(self, mat):
        return self.__sub__(mat)

    def __rsubb__(self, mat):
        return self.__sub__(mat)

    def __mul__(self, var):
        """Multiplying a Matrix by a scalar or another Matrix or a Vector

        Args:
            var (Matrix||Vector||integer||float||complex): 
            -Multiplying a Matrix with a scalar will result to 
            multiplying every element in the Matrix
            -Multiplying A Matrix with another Matrix
            -Multiplyinf A matrix with a Vector

        Raises:
            ValueError: Multiplying two matrices or a matrix by a vector cannot be done if n1!=m2 ( dim(A)=(m1,n1) dim(B)=(m2,n2)  )

        Returns:
            Matrix 
        """
        if type(var) == Vector:
            var = Matrix(var)
        if type(var) == Matrix:
            (m1, n1) = self.dim
            (m2, n2) = var.dim
            if n1 == m2:
                elements = self.elements
                lis, elemA = [], []
                res = 0
                for i in range(m1):
                    for j in range(n2):
                        for k in range(n1):
                            res = res + elements[i][k]*var.elements[k][j]
                        lis.append(res)
                        res = 0
                    elemA.append(lis)
                    lis = []
                return Matrix(elemA)
            else:
                raise ValueError(
                    "Multiplying two matrices or a matrix by a vector cannot be done if n1!=m2 ( dim(A)=(m1,n1) dim(B)=(m2,n2)  )")
        else:
            elements = self.elements
            elemA, lis = [], []
            for i in range(len(elements)):
                for j in range(len(elements[0])):
                    lis.append(elements[i][j]*var)
                elemA.append(lis)
                lis = []
            return Matrix(elemA)

    def __rmul__(self, var):
        return self.__mul__(var)

    def __IMUL__(self, var):
        return self.__mul__(var)

    def __getitem__(self, index):
        i, j = index
        if type(i) == int:  # Format M[i,j]
            return self.elements[i][j]
        elif i == "L":  # Format M["L",j] (returs a Vector at j index)
            return Vector(self.elements[j])
        elif i == "C":  # Format M["C",j] (returs a Vector at j index)
            m = self.transpose()
            return Vector(m.elements[j]).transpose()
        else:
            raise ValueError()

    def __setitem__(self, index: int, val: Union[int, float, complex]):
        (i, j) = index
        dimension = self.dim
        instance = type(val)
        # changed type in echelon with N and Echelon
        if instance != complex and instance != Vector and val <= 1e-14 and val >= -1e-14:
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

        if type(i) == int:
            # Format M[i,j]= integer
            self.elements[i][j] = val
        elif i == "L" and type(val) == Vector and val.isLine:
            # Format M["L",j]=Vector(..) (Vector should be a Line)
            self.elements[j] = val.elements
        elif i == "C" and type(val) == Vector and val.isColumn:
            # Format M["C",j]=Vector(..) (Vector should be a Column)
            (m, n) = val.dim
            for k in range(m):
                self.elements[k][j] = val.elements[k][0]
        self.__updateMatrix(self.elements)

    def trace(self):
        i = 0
        res = 0
        len = self.dim[0]
        if self.isSquared:
            while i < len:
                res += self.elements[i][i]
                i += 1
            return res
        else:
            raise ValueError("Matrix should be square")

    def transpose(self):
        (m, n) = self.dim
        new = Matrix(n, m).elements
        i, j = 0, 0
        while i < m:
            while j < n:
                new[j][i] = self.elements[i][j]
                j += 1
            j = 0
            i += 1
        return Matrix(new)

    def echelon(self, choice=None):
        """Echelon a Matrix
        This function has a float precision to 1e-14 and 1e14 for better performance
        Args:
            choice (string, optional): [description]. Defaults to None.

        Returns:
            Matrix: Echeloned Matrix (REF or RREF)
        """
        (m, n) = self.dim
        Vect = [self["L", i] for i in range(m)]
        index = [indexPivot(x) for x in Vect]
        (index, Vect, k, negative) = sortList(index, Vect)

        L = []
        for i in range(len(index)-k):
            (index, Vect, k, neg) = sortList(index, Vect)
            negative *= neg

            ind = index[i]

            for j in range(i+1, len(index)-k):
                if index[j] in L:
                    break
                if index[i] == index[j]:
                    Vect[j] = Vect[j] - Vect[i]*(Vect[j][ind]/Vect[i][ind])
            L.append(ind)
            index = [indexPivot(x) for x in Vect]

        if choice == "DET":
            return (Matrix(Vect), negative)

        index = [indexPivot(x) for x in Vect]
        for i in range(len(index)):
            if index[i] == -1:
                break
            else:
                Vect[i] = Vect[i]*(1/Vect[i][index[i]])

        if choice == None or choice == "REF":
            return Matrix(Vect)

        for j in range(len(index)):
            for i in range(j):
                if i == -1 or Vect[i].isNul():
                    break
                else:
                    Vect[i] = Vect[i]-(Vect[j]*Vect[i][index[j]])

        if choice == "RREF":
            return Matrix(Vect)

    def det(self):
        if self.isSquared:
            (mat, neg) = self.echelon(choice="DET")
            (n, m) = mat.dim
            res = 1
            for i in range(n):
                res *= mat.elements[i][i]
            return res*neg
        else:
            raise ValueError("Matrix is not a square matrix")

    def isInversible(self) -> bool:
        try:
            if self.det() != 0:
                return True
        except:
            return False

    def __repr__(self):
        string = ''
        i, j = 0, 0
        elem = self.elements
        while i < len(elem):
            string += '\n('
            while j < len(elem[0]):
                e = elem[i][j]
                if type(e) != complex:
                    e = round(e, 4)
                string += " {:^g} ".format(e)
                j += 1
            string += ')'
            j = 0
            i += 1
        string += '\n'
        return string

    def __eq__(self, other):
        accepted = [Matrix, Vector]
        if type(other) not in accepted:
            return False
        elif self.dim != other.dim:
            return False
        else:
            return self.elements1d == other.elements1d

    def echelonWithN(self, N):
        (m, n) = self.dim
        (m1, n1) = N.dim
        if type(N) == Vector and m == m1:
            N = Matrix(N)
        elif type(N) != Matrix and m1 != m:
            raise ValueError(
                "N should be a matrix or a vector column and the same dimension")

        Nvect = [N["L", i] for i in range(m)]
        Vect = [self["L", i] for i in range(m)]
        index = [indexPivot(x) for x in Vect]
        (index, Vect, k, negative, Nvect) = sortMatrix(index, Vect, Nvect)
        L = []

        for i in range(len(index)-k):
            (index, Vect, k, neg, Nvect) = sortMatrix(index, Vect, Nvect)
            negative *= neg
            ind = index[i]
            if index[i] == -1:
                break
            else:
                # here there was a problem on 06/09/2021
                Nvect[i] = Nvect[i]*(1/Vect[i][ind])
                Vect[i] = Vect[i]*(1/Vect[i][ind])
            for j in range(i+1, len(index)-k):

                if index[j] in L:
                    break
                if index[i] == index[j]:
                    Nvect[j] = Nvect[j] - Nvect[i]*(Vect[j][ind])
                    Vect[j] = Vect[j] - Vect[i]*(Vect[j][ind])

            L.append(ind)
            index = [indexPivot(x) for x in Vect]

        for j in range(len(index)):
            for i in range(j):
                if i == -1 or Vect[i].isNul():
                    break
                else:
                    Nvect[i] = Nvect[i]-(Nvect[j]*Vect[i][index[j]])
                    Vect[i] = Vect[i]-(Vect[j]*Vect[i][index[j]])

        if n1 == 1:
            return Matrix(Nvect).transpose()
        else:
            return Matrix(Nvect)

    def isSymmetric(self) -> bool:
        if self.isSquared:
            (m, n) = self.dim
            i = 0
            while i < m:
                if self["L", i] != self["C", i].transpose():
                    return False
                i += 1
            return True
        else:
            raise ValueError("The matrix should be squared ")

    def __invert__(self):
        """Inverse a Matrix

        Raises:
            ValueError: The matrix is not inversible (If it's a square matrix, det=0 or the matrix is not square

        Returns:
            Matrix: The inverse of a Matrix
        """
        if self.isInversible():
            (m, n) = self.dim
            I = Identity(m)
            return self.echelonWithN(I)
        else:
            raise ValueError(
                "The matrix is not inversible (If it's a square matrix, det=0 or the matrix is not square")

    def rank(self) -> int:
        (m, n) = self.dim
        matecheloned = self.echelon(choice="RREF")
        Vect = [matecheloned["L", i] for i in range(m)]
        index = [indexPivot(x) for x in Vect]
        try:
            rank = index.index(-1)
        except:
            rank = m
        return rank

    def isDiagonalMatrix(self) -> bool:
        if self.isSquared:
            (m, n) = self.dim
            elem = self.elements
            for i in range(m):
                for j in range(n):
                    if i != j and elem[i][j] != 0:
                        return False
            return True
        else:
            raise ValueError("The matrix should be squared")

    def OperationOnDiagonalM(self, operation, n=1):
        if self.isDiagonalMatrix():
            (m1, n1) = self.dim
            if operation == pow:
                for i in range(m1):
                    self.elements[i][i] = operation(self.elements[i][i], n)
            else:
                for i in range(m1):
                    self.elements[i][i] = operation(self.elements[i][i])

            return Matrix(self.elements)
        else:
            raise ValueError('Matrix should be squared and diagonal')

    def Null(self, sub=None):
        """Null Space

        Args:
            sub (int||float||complex, optional): used mostly for finding Eigenvectors.
            Example: (Ker(Matrix - sub*Identity)
            Defaults to None.

        Returns:
            array: Null space vectors
        """
        (m, n) = self.dim
        rank = 0
        iden = Identity(n)
        if self.isSquared and sub != None:
            matEcheloned = self - (iden*sub)
            matEcheloned = matEcheloned.echelon("RREF")

        else:
            matEcheloned = self.echelon("RREF")

        Vect = [matEcheloned["C", i] for i in range(n)]
        index = [indexPivotColumn(x) for x in Vect]
        idenVectors = [iden["C", i] for i in range(n)]
        VectNull = Vector([[0] for x in range(n)])
        NullSpace = []
        indexCroissant = []
        max = index[0]
        if max == -1:
            NullSpace.append(idenVectors[0])
        for i in range(1, n):
            if index[i] == max and index[i] != -1 or index[i] in indexCroissant:
                vect1 = idenVectors[i]
                for j in range(m):
                    vect1[j] -= Vect[i][j]
                NullSpace.append(vect1)
            elif index[i] == -1:
                NullSpace.append(idenVectors[i])
            indexCroissant.append(max)
            max = index[i]
        if len(NullSpace) == 0:
            NullSpace.append(VectNull)
        return NullSpace

    def eigenvalues(self):
        """Eigenvalues for 2x2 Matrix

        Raises:
            ValueError: "Can't compute eigenvalues with complex determinant yet! :("
            ValueError: The Matrix isn't Squared

        Returns:
            List: list of eigenvalues
        """
        if self.isSquared:
            (m, n) = self.dim
            trace = -self.trace()
            det = self.det()
            delta = 0
            eigenV = []
            Vect = [self["L", i] for i in range(m)]
            index = [indexPivot(x) for x in Vect]
            # (L, Vect, k, neg) = sortList(index, Vect)
            # det *= neg
            if m == 2 and n == 2:
                delta = ((trace**2)-4*det)
                if type(delta) != complex:
                    if delta < 0:
                        eigenV.extend(
                            [(-trace-1j*sqrt(-delta))/2, (-trace+1j*sqrt(-delta))/2])
                    elif delta > 0:

                        eigenV.extend(
                            [(-trace-sqrt(delta))/2, (-trace+sqrt(delta))/2])
                    else:
                        eigenV.extend([-trace/2]*2)
                else:
                    raise ValueError(
                        "Can't compute eigenvalues with complex determinant yet! :(")
            return eigenV

        else:
            raise ValueError("The Matrix isn't Squared")

    def eigenvectors(self):
        (m, n) = self.dim
        if m == 2 and n == 2:
            eigenValues = self.eigenvalues()
            null = []
            eigenNotRepeated = list(set(eigenValues))
            for i in range(len(eigenNotRepeated)):
                null += self.Null(sub=eigenNotRepeated[i])
        else:
            raise ValueError(
                "This operation only works for 2x2 matrix for now")
        return(null)

    def Diagonalizable(self):
        """Diagonalizable

        Raises:
            ValueError: The matrix should be squared

        Returns:
            Bool: if the matrix is diagonalizable
        """
        if self.isSquared:
            eigen = self.eigenvalues()
            multiplicity = {i: eigen.count(i) for i in eigen}
            eigenNotRepeated = list(set(eigen))
            for i in range(len(multiplicity)):
                null = self.Null(sub=eigenNotRepeated[i])
                if(len(null) != multiplicity[eigenNotRepeated[i]]):
                    return False
            return True
        else:
            raise ValueError('The matrix should be squared')

    def Diagonalize(self):
        (m, n) = self.dim
        if m == 2 and n == 2:
            if(self.Diagonalizable()):
                (m, n) = self.dim
                diagonal = Identity(m)
                eigenValues = self.eigenvalues()
                null = []
                for i in range(m):
                    diagonal[i, i] *= eigenValues[i]
                eigenNotRepeated = list(set(eigenValues))
                for i in range(len(eigenNotRepeated)):
                    null += self.Null(sub=eigenNotRepeated[i])
                eigenVectorsMatrix = Matrix(null)
                inverseEigenVectorsMatrix = eigenVectorsMatrix.__invert__()
                return {'P': eigenVectorsMatrix, 'D': diagonal, 'P**-1': inverseEigenVectorsMatrix}
        else:
            raise ValueError(
                "This operation only works for 2x2 matrix for now")

    def __pow__(self, var):
        """Power of a Matrix

        Args:
            var (int): the var is the chosen power  for the matrix

        Raises:
            ValueError: This operation only works for 2x2 real matrix for now

        Returns:
            Matrix: Matrix to the power of var
        """
        (m, n) = self.dim
        if m == 2 and n == 2:
            if(self.Diagonalizable()):
                allmatrices = self.Diagonalize()
                return allmatrices['P']*allmatrices['D'].OperationOnDiagonalM(pow, var)*allmatrices['P**-1']
        else:
            raise ValueError(
                "This operation only works for 2x2 matrix for now")

    def __ipow__(self, var):
        return self.__pow__(var)


def logM(self: Matrix) -> Matrix:
    (m, n) = self.dim
    if m == 2 and n == 2:
        if(self.Diagonalizable()):
            allmatrices = self.Diagonalize()
            return allmatrices['P']*allmatrices['D'].OperationOnDiagonalM(log)*allmatrices['P**-1']
        else:
            raise ValueError(
                "This operation only works for 2x2 Diagonalizable matrix for now")
    else:
        raise ValueError(
            "This operation only works for 2x2 Diagonalizable matrix for now")


def expM(self: Matrix) -> Matrix:
    (m, n) = self.dim
    if m == 2 and n == 2:
        if(self.Diagonalizable()):
            allmatrices = self.Diagonalize()
            return allmatrices['P']*allmatrices['D'].OperationOnDiagonalM(exp)*allmatrices['P**-1']
        else:
            raise ValueError(
                "This operation only works for 2x2 Diagonalizable matrix for now")
    else:
        raise ValueError(
            "This operation only works for 2x2 diagonalizable matrix for now")

# def GaussElimination(ma,v1) -> Matrix:
#    return ma.echelonWithN(v1)


def CramerRule(ma: Matrix, v1: Vector) -> Vector:
    (m, n) = ma.dim
    ele = []
    determ = ma.det()
    if determ != 0:
        for i in range(n):
            m1 = Matrix(ma.elements)
            m1["C", i] = v1
            ele.append([m1.det()/determ])
    return Vector(ele)


# print(-1*expM(m1*pi) == Identity(2))
# print(logM(-1*expM(m1*pi)) == logM(Identity(2)))

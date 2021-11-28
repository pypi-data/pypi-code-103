"""
pymatrices Package :-

- A Python 3.x Package to implement Matrices and its properties...
"""

from copy import deepcopy as _dc
from itertools import permutations as _perm
from math import sqrt as _sqrt, cos as _cos, sin as _sin, acos as _acos

class matrix:
	"""Creates a Matrix using a 2-D list"""

	def __init__(self, matrix):
		self.__rows = len(matrix)
		self.__cols = len(matrix[0])

		for rows in matrix:
			if len(rows) != self.__cols:
				raise TypeError("Invalid Matrix")

		if not isinstance(matrix, list):
			tempMat = list(matrix)
		else:
			tempMat = matrix

		for i in range(len(matrix)):
			if not isinstance(matrix[i], list):
				tempMat[i] = list(matrix[i])

		self.__mat = tempMat

	@property
	def matrix(self):
		return self.__mat

	@property
	def order(self):
		return (self.__rows, self.__cols)

	@property
	def transpose(self):
		order, res = self.order, []

		for i in range(order[1]):
			temp = []

			for j in range(order[0]):
				temp.append(self.matrix[j][i])

			res.append(temp)

		return matrix(res)

	@property
	def primaryDiagonalValues(self):
		res = []

		for i in range(len(self.matrix)):
			for j in range(len(self.matrix[i])):
				if i == j:
					res.append(self.matrix[i][j])

		return res

	@property
	def secondaryDiagonalValues(self):
		order, res = self.order, []

		for i in range(len(self.matrix)):
			for j in range(len(self.matrix[i])):
				if i+j == (order[0]-1):
					res.append(self.matrix[i][j])

		return res

	def __repr__(self):
		minLen, order, res = len(f"{self.matrix[0][0]}"), self.order, "[ "

		for row in self.matrix:
			for val in row:
				if len(f"{val}") > minLen:
					minLen = len(f"{val}")

		for i in range(order[0]):
			for j in range(order[1]):
				strVal = f"{self.matrix[i][j]}"

				if (i == order[0]-1) and (j == order[1]-1):
					if (i != 0) and (j == 0):
						res += " "*(minLen+2-len(strVal)) + strVal + " ]"
					else:
						res += " "*(minLen-len(strVal)) + strVal + " ]"
				else:
					if (i != 0) and (j == 0):
						res += " "*(minLen+2-len(strVal)) + strVal + " "
					else:
						res += " "*(minLen-len(strVal)) + strVal + " "
			res += "\n"

		return res

	def __add__(self, other):
		if isinstance(other, matrix):
			if self.order == other.order:
				res, temp = [], []
				row, col = self.order

				for i in range(row):
					for j in range(col):
						sum_elem = self.matrix[i][j] + other.matrix[i][j]
						temp.append(sum_elem)

					res.append(temp)
					temp = []

				return matrix(res)
			else:
				raise ValueError("Order of the Matrices must be same")
		else:
			raise TypeError(f"can only add matrix (not '{type(other).__name__}') to matrix")

	def __sub__(self, other):
		if isinstance(other, matrix):
			if self.order == other.order:
				res, temp = [], []
				row, col = self.order

				for i in range(row):
					for j in range(col):
						sum_elem = self.matrix[i][j] - other.matrix[i][j]
						temp.append(sum_elem)

					res.append(temp)
					temp = []

				return matrix(res)
			else:
				raise ValueError("Order of the Matrices must be same")
		else:
			raise TypeError(f"can only subtract matrix (not '{type(other).__name__}') from matrix")

	def __mul__(self, other):
		assert isinstance(other, (matrix, int, float)), f"Can only multiply either matrix or int or float (not {type(other).__name__}) with matrix"

		if isinstance(other, matrix):
			sOrder, oOrder = self.order, other.order
			if sOrder[1] == oOrder[0]:
				res = []
				T_other = other.transpose
				tOrder = T_other.order

				for i in range(sOrder[0]):
					temp = []

					for j in range(tOrder[0]):
						sum_val = 0

						for k in range(tOrder[1]):
							sum_val += (self.matrix[i][k] * T_other.matrix[j][k])

						temp.append(sum_val)
					res.append(temp)
			else:
				raise ValueError("Matrices can't be multiplied.")
		elif isinstance(other, (int, float)):
			order, res = self.order, []

			for row in range(order[0]):
				temp = []

				for col in range(order[1]):
					temp.append(self.matrix[row][col]*other)

				res.append(temp)

		return matrix(res)

	def __truediv__(self, other):
		if isinstance(other, (int, float)):
			order, res = self.order, []

			for row in range(order[0]):
				temp = []

				for col in range(order[1]):
					temp.append(self.matrix[row][col]/other)

				res.append(temp)
			return matrix(res)
		else:
			raise ValueError("Matrix can only be divided by a number")

	def __eq__(self, other):
		if isinstance(other, matrix):
			sOrder = self.order

			if sOrder == other.order:
				for row in range(sOrder[0]):
					for col in range(sOrder[1]):
						if self.matrix[row][col] != other.matrix[row][col]:
							return False
				else:
					return True
			else:
				return False
		else:
			return False

	def __neg__(self):
		order, res = self.order, []

		for row in range(order[0]):
			temp = []

			for col in range(order[1]):
				temp.append(-self.matrix[row][col])

			res.append(temp)
		return matrix(res)

	def positionOf(self, value):
		row, col = self.order

		for i in range(row):
			for j in range(col):
				if self.matrix[i][j] == value:
					return (i+1, j+1)
		else:
			raise ValueError(f"There is no Element as {value} in the Matrix.")

	def minorOfValueAt(self, row, column):
		row -= 1; column -= 1

		mat = [self.matrix[i] for i in range(len(self.matrix)) if i != row]

		res = [[i[j] for j in range(len(i)) if j!=column] for i in mat]

		return matrix(res)

	def valueAt(self, row, column):
		return self.matrix[row-1][column-1]

def adjoint(matrix1):
	"""Returns the adjoint of matrix"""

	order, mat = matrix1.order, matrix1.matrix

	if order[0] == 2:
		return matrix([[mat[1][1], -mat[0][1]], [-mat[1][0], mat[0][0]]])
	else:
		res = [[((-1)**(i+j+2))*(mat[i][j])*(determinantOf(matrix1.minorOfValueAt(i+1, j+1))) for j in range(order[1])] for i in range(order[0])]

		return matrix(res)

def createByFilling(value, order):
	"""Creates a Matrix of order by Filling it with value"""

	rows, cols = order[0], order[1]
	res = [[value for __ in range(cols)] for _ in range(rows)]

	return matrix(res)

def createColumnMatrix(values):
	"""Creates a Column Matrix with values"""

	return matrix([[i] for i in values])

def createRowMatrix(values):
	"""Creates a Row Matrix with values"""

	return matrix([[i for i in values]])

def determinantOf(matrix):
	"""Returns the determinantOf of matrix"""

	order = matrix.order

	if order[0] == order[1]:
		mat = matrix.matrix

		if order[0] == 1:
			return mat[0][0]
		elif order[0] == 2:
			return (mat[1][1]*mat[0][0]) - (mat[1][0]*mat[0][1])
		else:
			M11 = mat[0][0]*(determinantOf(matrix.minorOfValueAt(1, 1)))
			M12 = mat[0][1]*(determinantOf(matrix.minorOfValueAt(1, 2)))
			M13 = mat[0][2]*(determinantOf(matrix.minorOfValueAt(1, 3)))

			return M11 - M12 + M13
	else:
		raise ValueError(f"can only find the determinant of square matrix, not '{order[0]}x{order[1]}' matrix.")

def eigenvaluesOf(matrix):
	"""Returns a list of the eigenvalues of the given matrix."""

	order, S1 = matrix.order, sum(matrix.primaryDiagonalValues)

	assert (order[0] in (1, 2, 3)) and (order[1] in (1, 2, 3)), "Maximum Order is 3x3"

	def F(a, b, c):
		return ((3*c/a)-((b**2)/(a**2)))/3

	def G(a, b, c, d):
		return (((2*(b**3))/(a**3))-((9*b*c)/(a**2))+(27*d/a))/27

	def H(g, f):
		return ((g**2)/4+(f**3)/27)

	if order[0] == 2:
		S2 = determinantOf(matrix)

		a, b, c = 1, -S1, S2

		disc = (b**2-4*a*c)**0.5

		return [(-b+disc)/(2*a), (-b-disc)/(2*a)]
	elif order[0] == 3:
		S2 = determinantOf(matrix.minorOfValueAt(1, 1))+determinantOf(matrix.minorOfValueAt(2, 2))+determinantOf(matrix.minorOfValueAt(3, 3))
		S3 = determinantOf(matrix)

		a, b, c, d = 1, -S1, S2, -S3

		if (a == 0 and b == 0):
			return [(-d*1)/c]

		elif (a == 0):
			D = c**2 - 4*b*d

			if D >= 0:
				sqrtD = _sqrt(D)
				x1, x2 = (-c+sqrtD)/(2*b), (-c-sqrtD)/(2*b)
			else:
				sqrtD = _sqrt(-D)
				x1, x2 = (-c+sqrtD*1j)/(2*b), (-c-sqrtD*1j)/(2*b)

			return [x1, x2]

		f, g = F(a, b, c), G(a, b, c, d)
		h = H(g, f)

		if (f==0) and (g==0) and (h==0):
			x = -((d/(1*a))**(1/3)) if (d/a)>=0 else (-d/(1*a))**(1/3)
			return [x]*3

		elif h <= 0:
			i = _sqrt(((g**2)/4)-h)
			j = i**(1/3)
			k = _acos(-(g/(2*i)))
			L, M, N, P = -j, _cos(k/3), _sqrt(3)*_sin(k/3), -(b/(3*a))

			return [round(i, 1) for i in [2*j*_cos(k/3)-(b/(3*a)), L*(M+N)+P, L*(M-N)+P]]

		elif h > 0:
			R = -(g/2)+_sqrt(h)
			S = R**(1/3) if R>=0 else -((-R)**(1/3))
			T = -(g/2)-_sqrt(h)
			U = (T**(1/3)) if T>=0 else -((-T)**(1/3))

			x1 = (S+U)-(b/(3*a))
			x2 = -(S+U)/2-(b/(3*a))+(S-U)*_sqrt(3)*0.5j
			x3 = -(S+U)/2-(b/(3*a))-(S-U)*_sqrt(3)*0.5j

			def compToInt(comp):
				imag = comp.imag

				if "e" in str(imag):
					str_imag = str(imag)
					e_ind = str_imag.find("e")
					str_exp = str_imag[e_ind+1:]
					exp = int(str_exp)

					return comp.real if exp <= -5 else comp
				elif 0<abs(imag)<=1:
					return comp.real

			return [x1, compToInt(x2), compToInt(x3)]

def eigenvectorsOf(matrix):
	"""Generates the eigenvectors of the given matrix."""

	res = []

	def __isallzero(L1):
		flag = True

		for i in L1:
			if i != 0:
				flag = False
				break

		return flag

	evals, order = eigenvaluesOf(matrix), matrix.order
	matobj = [_dc(matrix.matrix) for _ in range(order[0])]

	for eigval in evals:
		mat = matobj.pop()

		if isinstance(eigval, complex):
			for i in range(order[0]):
				for j in range(order[1]):
					if i == j:
						mat[i][j] = complex(mat[i][j]) - eigval
					else:
						mat[i][j] = complex(mat[i][j])
		else:
			for i in range(order[0]):
				for j in range(order[1]):
					if i == j:
						mat[i][j] -= int(eigval)

		veqns = list(map(__isallzero, mat))
		eqn1, eqn2 = tuple([mat[i] for i in range(order[0]) if veqns[i]==False])[:2]

		if len(eqn1) == 2:
			llim, ulim, flag = 0, 5, True

			while flag:
				vrange = _perm([_ for _ in range(llim, ulim+1)], 2)

				for a, b in vrange:
					if (int(eqn1[0]*a + eqn1[1]*b) == 0) and (int(eqn2[0]*a + eqn2[1]*b) == 0):
						res.append(createColumnMatrix((a, b)))
						flag = False
						break
					elif (int(eqn1[0] + eqn1[1]) == 0) and (int(eqn2[0] + eqn2[1]) == 0):
						res.append(createColumnMatrix((1, 1)))
						flag = False
						break
				else:
					llim -= 1
					ulim += 1

		elif len(eqn1) == 3:
			x = (eqn2[2]*eqn1[1]) - (eqn2[1]*eqn1[2])
			y = (eqn2[0]*eqn1[2]) - (eqn2[2]*eqn1[0])
			z = (eqn2[1]*eqn1[0]) - (eqn2[0]*eqn1[1])

			res.append(createColumnMatrix((x, y, z)))

	return res


def inverseOf(matrix):
	"""Returns the inverse of matrix"""

	det = determinantOf(matrix)

	if det != 0:
		return adjoint(matrix)/det
	else:
		raise TypeError("Matrix is Singular.")

def isDiagonal(matrix):
	"""Returns True if matrix is a 'Diagonal Matrix' else Returns False"""

	order, mat = matrix.order, matrix.matrix

	for row in range(order[0]):
		for col in range(order[1]):
			if row != col:
				if mat[row][col] != 0:
					return False
	else:
		return True

def I(order):
	"""Returns the Identity Matrix of the given order"""

	assert isinstance(order, int), f"order must be 'int' but got '{type(order).__name__}'"

	res = [[0 for _ in range(order)] for __ in range(order)]

	for i in range(order):
		for j in range(order):
			if i==j:
				res[i][j] = 1

	return matrix(res)

def O(order):
	"""Returns the Square Null Matrix of the given order"""

	assert isinstance(order, int), f"order must be 'int' but got '{type(order).__name__}'"

	res = [[0 for _ in range(order)] for __ in range(order)]

	return matrix(res)

def isIdempotent(matrix):
	"""Returns True if matrix is an 'Idempotent Matrix' else Returns False"""

	return True if matrix*matrix == matrix else False

def isIdentity(matrix):
	"""Returns True if matrix is an 'Identity Matrix' else Returns False"""

	return True if matrix == I(matrix.order[0]) else False

def isInvolutory(matrix):
	"""Returns True if matrix is an 'Involutory Matrix' else Returns False"""

	return True if matrix*matrix == I(matrix.order[0]) else False

def isNilpotent(matrix):
	"""Returns True if matrix is a 'Nilpotent Matrix' else Returns False"""

	res = matrix

	for i in range(1, matrix.order[0]+1):
		res *= matrix

		if isNull(res):
			return True
	else:
		return False

def isNull(matrix):
	"""Returns True if matrix is a 'Null Matrix' else Returns False"""

	for i in matrix.matrix:
		for j in i:
			if j != 0:
				return False
	else:
		return True

def isOrthogonal(matrix):
	"""Returns True if matrix is an 'Orthogonal Matrix' else Returns False"""
	order = matrix.order

	if order[0] == order[1]:
		if (matrix*matrix.transpose == I(order[0])) or (matrix.transpose*matrix == I(order[0])):
			return True
		else:
			return False
	else:
		return False

def isScalar(matrix):
	"""Returns True if matrix is a 'Scalar Matrix' else Returns False"""

	if isDiagonal(matrix):
		order, val, mat = matrix.order, matrix.matrix[0][0], matrix.matrix

		for row in range(order[0]):
			for col in range(order[1]):
				if row == col:
					if mat[row][col] != val:
						return False
		else:
			return True
	else:
		return False

def isSingular(matrix):
	"""Returns True if matrix is a 'Singular Matrix' else Returns False"""

	return True if determinantOf(matrix) == 0 else False

def isSquare(matrix):
	"""Returns True if matrix is a 'Square Matrix' else Returns False"""
	order = matrix.order

	return True if order[0] == order[1] else False

def isSymmetric(matrix):
	"""Returns True if matrix is a 'Symmetric Matrix' else Returns False"""

	return True if matrix == matrix.transpose else False

def isSkewSymmetric(matrix):
	"""Returns True if matrix is a 'Skew Symmetric Matrix' else Returns False"""

	return True if matrix == -matrix.transpose else False
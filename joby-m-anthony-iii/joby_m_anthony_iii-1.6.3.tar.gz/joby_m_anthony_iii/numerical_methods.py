#################################
## Preamble
# import necessary modules/tools
import math
import numba as nb
import numpy as np
import os
import pandas as pd
import scipy as sc
import sympy as sp
import sys
from types import FunctionType
#   #   #   #   #   #   #   #   #

#################################
## Universal Variables/Methods/Classes
# common functions
def diagonality(matrix):
	"""Determines if matrix is strictly, diagonally dominant.

	Parameters
	----------
	matrix : array
		Input matrix to be tested.

	Returns
	-------
	is_strict_diagonal_matrix : boolean
		Truth value whether matrix is strictly, diagonally dominant.

	Raises
	------
	IndexError
		Matrix of interest must be square.

	Warnings
	--------
	Will print to console either if strictly, diagonally dominant, or if matrix, `A` is not strictly, diagonally dominant which could lead to poor solution of 'Ax = b'.
	"""
	matrix_name, A = "A", np.array(matrix)
	if not(np.sum(np.shape(A)) - np.shape(A)[0] == np.shape(A)[0]):
		raise IndexError(f"ERROR! Matrix, {matrix_name} must be square!")
	i, diags, long = 0, np.zeros_like(A), np.zeros_like(A)
	while i < len(A):
		j = 0
		while j < len(A):
			aij = A[i][j]
			if i == j: long[i][j] = aij
			else: diags[i][j] = aij
			j += 1
		i += 1
	if np.sum(long) >= np.sum(diags):
		print(f"Information: Matrix, {matrix_name} is strictly, diagonally dominant.")
		is_strict_diagonal_matrix = True
	else:
		is_strict_diagonal_matrix = False
		print(f"Warning! Matrix, {matrix_name} is not strictly, diagonally dominant. Solution may be inaccurate.")
	return is_strict_diagonal_matrix

def eigen_values(matrix):
	"""Directly finds eigenvalues of matrix by its determinant. Not recommended for large, sparse matrices.

	Parameters
	----------
	matrix : array
		Matrix of interest.

	Returns
	-------
	lambdas : array
		Eigenvector containing roots.

	Raises
	------
	IndexError
		Matrix of interest must be square.
	"""
	# See Also
	# --------
	matrix_name, A = "A", np.array(matrix)
	if not(np.sum(np.shape(A)) - np.shape(A)[0] == np.shape(A)[0]):
		raise IndexError(f"ERROR! Matrix, {matrix_name} must be square!")
	sym_r = sp.Symbol("r")
	i, identityA = 0, np.zeros_like(A)
	while i < len(A):
		j = 0
		while j < len(A[0]):
			if i == j: identityA[i][j] = 1
			j += 1
		i += 1
	lambda_identity = identityA*sym_r
	determinant = sp.det(sp.Matrix(A - lambda_identity))
	roots = sp.solve(determinant)
	lambdas = []
	for r in roots:
		r = complex(r)
		if np.imag(r) == 0: r = np.real(r)
		lambdas.append(r)
	return lambdas
# preceded by eigen_values
def spectral_radius(matrix):
	"""Finds the spectral radius of matrix.

	Parameters
	----------
	matrix : array
		Matrix of interest.

	Returns
	-------
	rho : float
		Spectral radius.

	Raises
	------
	IndexError
		Matrix of interest must be square.

	See Also
	--------
	eigen_values() : Function to find eigenvector of A.
	"""
	matrix_name, A = "A", np.array(matrix)
	if not(np.sum(np.shape(A)) - np.shape(A)[0] == np.shape(A)[0]):
		raise IndexError(f"ERROR! Matrix, {matrix_name} must be square!")
	rho = np.max(np.abs(eigen_values(A)))
	return rho
# preceded by spectral_radius
@nb.jit(nopython=True)
class norms:
	def __init__(self, x, x0=()):
		"""
		Parameters
		----------
		x : array
			Newly approximated array.

		x0 : array, optional
			Previously approximated array.

		Yields
		------
		self.vec_name : string
			Connote symbol name as 'x'.

		self.x : array
			Newly approximated array.

		self.old_vec_name : string
			Connote symbol name as 'x0'.

		self.x0 : array
			Previously approximated array.

		Raises
		------
		IndexError
			If the input vectors are not the same length.
		"""
		self.vec_name, self.x = "x", np.array(x)
		self.old_vec_name, self.x0 = "x0", np.array(x0)
		if not(self.x0.shape[0] == 0 or len(x) == len(x0)):
			raise IndexError(f"ERROR! {self.vec_name}, and {self.old_vec_name} must be the same size!")

	def l_infinity(self):
		"""Maximum difference between absolute sum of i'th rows.

		Returns
		-------
		norm : float
			Scalar value.

		Yields
		------
		self.norm : float
			Scalar value.

		Raises
		------
		IndexError
			If the input vectors are not the same length.

		Notes
		-----
		Best thought as "actual" distance between vectors.

		Also calculates infinity norm of matrix(ces).

		Examples
		--------
		[x0] = (1, 1, 1)^(t)

		[x] = (1.2001, 0.99991, 0.92538)^(t)

		||x0 - x|| = max{|1 - 1.2001|, |1 - 0.99991|, |1 - 0.92538|}

		||x0 - x|| = 0.2001
		"""
		vec_name, x = self.vec_name, self.x
		old_vec_name, x0 = self.old_vec_name, self.x0
		# initialize loop
		norm_i = np.zeros_like(x)
		if x0.shape[0] == 0:
			if np.sum(x.shape) == x.shape[0]:
				for i in range(x.shape[0]):
					# evaluate and store norm, ||.||
					norm_i[i] = abs(x[i])
			elif np.sum(x.shape) > x.shape[0]:
				norm_ij = np.zeros_like(x)
				for i in range(x.shape[0]):
					for j in range(x.shape[1]):
						# evaluate and store norm, ||.||
						norm_ij[i][j] = abs(x[i][j])
					norm_i[i] = np.sum(norm_ij[i][:])
		elif len(x) == len(x0):
			if np.sum(x0.shape) == x0.shape[0]:
				for i in range(x0.shape[0]):
					norm_i[i] = abs(x[i] - x0[i])
			elif np.sum(x0.shape) > x0.shape[0]:
				if np.sum(x.shape) == np.sum(x0.shape):
					for i in range(x0.shape[0]):
						for j in range(x0.shape[1]):
							norm_ij = np.zeros_like(x)
							# evaluate and store norm, ||.||
							norm_ij[i][j] = abs(x[i][j] - x0[i][j])
						norm_i[i] = np.sum(norm_ij[i][:])
				elif np.sum(x.shape) == np.sum(x0.shape):
					for i in range(x0.shape[0]):
						# evaluate and store norm, ||.||
						norm_i[i] = abs(x[i] - x0[i])
		else:
			raise IndexError(f"ERROR! {vec_name}, and {old_vec_name} must be the same size!")
		# if no errors, then evaluate norm
		self.norm = np.amax(norm_i)
		# return the l_infinity norm
		return self.norm

	def l_two(self):
		"""Square root of sum of differences squared along i'th row.

		Returns
		-------
		norm : float
			Scalar value.

		Yields
		------
		self.norm : float
			Scalar value.

		Raises
		------
		IndexError
			If the input vectors are not the same length.

		See Also
		--------
		spectral_radius() : Function to find the spectral radius of vector.

		Examples
		--------
		[x0] = (1, 1, 1)^(t)

		[x] = (1.2001, 0.99991, 0.92538)^(t)

		||x0 - x|| = sqrt[ (1 - 1.2001)^2 \
			+ (1 - 0.99991)^2 + (1 - 0.92538)^2 ]

		||x0 - x|| = 0.21356
		"""
		vec_name, x = self.vec_name, self.x
		old_vec_name, x0 = self.old_vec_name, self.x0
		if x0.shape[0] == 0:
			# initialize loop
			norm_i = np.zeros_like(x)
			if np.sum(x.shape) == x.shape[0]:
				for i in range(len(x)):
					# evaluate and store norm, ||.||
					norm_i[i] += x[i]**2
				norm = math.sqrt(np.sum(norm_i))
			elif np.sum(x.shape) > x.shape[0]:
				x0 = np.reshape(x, (x.shape[0], x.shape[1]))
				xt = np.reshape(x, (x.shape[1], x.shape[0]))
				norm = math.sqrt(spectral_radius(x0*xt))
		elif len(x) == len(x0):
			if np.sum(x0.shape) > x0.shape[0]:
				x0 = np.reshape(x0, (x0.shape[0], x0.shape[1]))
				xt = np.reshape(x, (x0.shape[1], x0.shape[0]))
			else:
				x0 = np.reshape(x0, (len(x0), 1))
				xt = np.reshape(x, (1, len(x0)))
				# xt = np.reshape(x, (1, x.shape[0]))
			norm = math.sqrt(spectral_radius(x0*xt))
		else:
			raise IndexError(f"ERROR! {vec_name}, and {old_vec_name} must be the same size!")
		self.norm = norm
		return norm
# preceded by norms.()l_infinity() and norms().l_two()
def condition_number(matrix, norm_type="l_two"):
	"""Find the condition number of a given matrix and norm type.

	Parameters
	----------
	matrix : array
		Input matrix for analysis.

	norm_type : string, optional
		Selects norm comparison which is 'l_two' by default.

	Returns
	-------
	k : float
		Condition number of matrix, A.

	Warnings
	--------
	Will output evaluation of condition number and show in console.

	See Also
	--------
	norms().l_two() : Method that yields the l_2 norm.

	norms().l_infinity() : Method that yields the l_infinity norm.
	"""
	matrix_name, A = "A", np.array(matrix)
	i, A_inv = 0, np.zeros_like(A)
	while i < len(A):
		j = 0
		while j < len(A):
			aij = A[i][j]
			if aij != 0: A_inv[i][j] = 1/aij
			j += 1
		i += 1
	if norm_type == "l_infinity":
		norm, abnorm = norms(A).l_infinity(), norms(A_inv).l_infinity()
	elif norm_type == "l_two":
		norm, abnorm = norms(A).l_two(), norms(A_inv).l_two()
	k = norm*abnorm
	print(f"Information: Condition Number K({matrix_name}) = {k}")
	return k

def make_array(domain, function, variable=sp.Symbol("x")):
	"""Maps domain to range.

	Parameters
	----------
	domain : array
		Collection if input data.

	function : expression
		Function that maps the domain to range.

	variable : string, optional
		Sympy symbol or string representation of variable to respect in function.

	Returns
	-------
	g : tuple
		Mapped range from function.

	Warnings
	--------
	Prints to console the input expression, and that the expression was in fact used.
	"""
	if isinstance(function, (FunctionType, sp.Expr)):
		sym_function = sp.N(sp.sympify(function(variable)))
		function = sp.lambdify(variable, sym_function)
		print(f"Information: Input expression, {sym_function} used.")
	i, X, g = 0, np.array(domain), np.zeros_like(domain)
	while i < len(X):
		j = 0
		if np.sum(X.shape) > np.sum(X.shape[0]):
			while j < len(X[0]):
				g[i][j] = (function(X[i][j]))
				j += 1
		else: g[i] = function(X[i])
		i += 1
	return np.array(g)

def symmetry(matrix):
	"""Determines boolean truth value whether given matrix is symmetric.

	Parameters
	----------
	matrix : array
		Matrix of interest.

	Returns
	-------
	is_symmetric : bool
		True if symmetric, else False.

	Raises
	------
	IndexError
		Matrix of interest must be square.

	Warnings
	--------
	Console print that A is either symmetric or asymmetric.
	"""
	matrix_name, A = "A", np.array(matrix)
	if not(np.sum(np.shape(A)) - np.shape(A)[0] == np.shape(A)[0]):
		raise IndexError(f"ERROR! Matrix, {matrix_name} must be square!")
	i, At, is_symmetric = 0, np.transpose(A), False
	for ai in A:
		j = 0
		for aj in ai:
			if aj == At[i][j]: is_symmetric = True
			else:
				is_symmetric = False
				print(f"Warning! Matrix, {matrix_name} is not symmetric.")
				return is_symmetric
			j += 1
		i += 1
	if is_symmetric: print(f"Information: Matrix, {matrix_name} is symmetric.")
	return is_symmetric

def tridiagonality(matrix):
	"""Determine boolean truth value whether given matrix is tridiagonal.

	Parameters
	----------
	matrix : array
		Matrix of interest.

	Returns
	-------
	is_tridiagonal : bool
		True if tridiagonal, else False.

	Raises
	------
	IndexError
		Matrix of interest must be square.

	Warnings
	--------
	Prints to console that matrix is either tridiagonal or not.
	"""
	matrix_name, A = "A", np.array(matrix)
	if not(np.sum(np.shape(A)) - np.shape(A)[0] == np.shape(A)[0]):
		raise IndexError(f"ERROR! Matrix, {matrix_name} must be square!")
	diagonals = np.diagflat(np.diag(A))
	above = np.diagflat(np.diag(A, k=1), k=1)
	below = np.diagflat(np.diag(A, k=-1), k=-1)
	non_A = A - (diagonals + above + below)
	if np.sum(non_A) != 0:
		is_tridiagonal = False
		print(f"Warning! Matrix, {matrix_name} is not tridiagonal.")
	else:
		is_tridiagonal = True
		print(f"Information: Matrix, {matrix_name} is tridiagonal.")
	return is_tridiagonal
#   #   #   #   #   #   #   #   #


#################################
## Specific Functions
# --------------------
# eigenvalue solvers
class DirectSolver:
	def __init__(self, A, power, max_iter=100):
		"""
		Parameters
		----------
		A : tuple
			Characteristic matrix.

		power : int
			Signed power to which function error must be within.

		max_iter : int, optional
			Maximum iterations for which function may loop.

		Yields
		------
		self.A : tuple
			Either input functions or matrix of characteristic values.

		self.tol : float
			Specified tolerance to which method terminates.

		self.max_iter : int
			Maximum iterations allowed for method.

		self.is_diagonal : bool
			Truth value of whether matrix is diagonal.

		self.eigenvalues : tuple
			Eigenvalues of characteristic matrix, A.

		self.spectral_radius : float
			Spectral radius of characteristic matrix, A.

		self.condition_number : float
			Condition number of characteristic matrix, A.

		Raises
		------
		IndexError
			Matrix of interest must be square.

		ValueError
			If iterations constraint is not an integer.

		Warnings
		--------
		Not recommended to use eigen_values() to find eigenvalues of characteristic matrix, A; therefore, do not use eigen_values() if matrix, A is a large, sparse matrix if desiring quick calculations.

		See Also
		--------
		eigen_values() : Function to find eigenvalues of A.

		spectral_radius() : Function that finds the spectral radius of characteristic matrix, A.

		Notes
		-----
		Specified tolerance evaluated by `10**power`.

		`norm_type` may be either `'l_infinity'` or `'l_two'` but is 'l_infinity' by default.

		If `self.is_diagonal` is True, then matrix is diagonal. Else, not diagonal.
		"""
		matrix_name, A = "A", np.array(A)
		if np.sum(A.shape[0]) != np.sum(A.shape[1]): raise IndexError(f"ERROR! Matrix, {matrix_name} must be square!")
		if max_iter <= 0 or not isinstance(max_iter, (int, float)): raise ValueError(f"ERROR! Maximum iterations, N must be an integer greater than zero. {max_iter} was given and not understood.")
		self.A = A
		self.tol = float(10**power)
		self.max_iter = int(max_iter)
		self.is_diagonal = diagonality(A)
		self.is_tridiagonal = tridiagonality(A)
		# self.eigen_values = eigen_values(A)
		# self.spectral_radius = spectral_radius(A)
		# self.condition_number = condition_number(A, norm_type)

	def power_method(self, x):
		"""Approximate the dominant eigenvalue and associated eigenvector of matrix, A given some non-zero vector, x.

		Parameters
		----------
		x : array
			Numpy array.

		Returns
		-------
		pandas.DataFrame : dataframe
			Summarized dataframe from iterations.

		Yields
		------
		self.x : tuple
			Initial guess at eigenvector.

		self.iterations : tuple
			Collection of iterations through method.

		self.mu : tuple
			Collection of approximately largest eigenvalue.

		self.lambdas : tuple
			Collection of approximate eigenvectors.

		self.errors : tuple
			Collection of yielded norms.

		Raises
		------
		IndexError
			If x is neither n x 1 nor 1 x n array.
		"""
		A, tol, N = self.A, self.tol, self.max_iter
		vec_name, x = "x", np.array(x)
		if np.sum(x.shape) - np.sum(x.shape[0]) > 1: raise IndexError(f"Systems vector, {vec_name} must be n x 1 or 1 x n array!")
		self.x = np.reshape(x,(len(x),1))
		mu = [norms(x).l_infinity()]
		x = x/mu[-1]
		k, eigenvectors, errors = 1, [x], [1]
		while errors[-1] > tol and k <= N:
			y = np.matmul(A, x)
			for yi in y:
				if np.abs(yi) == norms(y).l_infinity():
					yp = float(yi)
			mu.append(yp)
			eigenvectors.append(y/yp)
			errors.append(norms(x, eigenvectors[-1]).l_infinity())
			x = eigenvectors[-1]
			k += 1
		self.iterations = np.array(range(k))
		self.mu = np.array(mu)
		self.lambdas = np.array(eigenvectors)
		self.errors = np.array(errors)
		return pd.DataFrame(data={"Iterations": self.iterations, "Mu": self.mu, "Lambdas": self.lambdas, "Errors": self.errors})

	def inverse_power_method(self, x, q):
		"""Approximate eigenvalue closest to target, q and associated eigenvector of matrix, A given some non-zero vector, x.

		Parameters
		----------
		x : array
			Numpy array.

		q : float
			Target to which the closest eigenvalue of matrix will be found.

		Returns
		-------
		pandas.DataFrame : dataframe
			Summarized dataframe from iterations.

		Yields
		------
		self.x : tuple
			Initial guess at eigenvector.

		self.iterations : tuple
			Collection of iterations through method.

		self.mu : tuple
			Collection of approximately largest eigenvalue.

		self.lambdas : tuple
			Collection of approximate eigenvectors.

		self.errors : tuple
			Collection of yielded norms.

		Raises
		------
		IndexError
			If x is neither n x 1 nor 1 x n array.
		"""
		A, tol, N = self.A, self.tol, self.max_iter
		vec_name, x = "x", np.array(x)
		if np.sum(x.shape) - np.sum(x.shape[0]) > 1: raise IndexError(f"Systems vector, {vec_name} must be n x 1 or 1 x n array!")
		self.x = np.reshape(x,(len(x),1))
		self.q = float(q)
		A = np.linalg.inv(A-q*np.identity(len(A)))
		mu = [1/norms(x).l_infinity() + q]
		k, eigenvectors, errors = 1, [x], [1]
		while errors[-1] > tol and k <= N:
			y = np.matmul(A, x)
			for yi in y:
				if np.abs(yi) == norms(y).l_infinity():
					yp = float(yi)
			mu.append(1/yp + q)
			eigenvectors.append(y/yp)
			errors.append(norms(x, x0=eigenvectors[-1]).l_infinity())
			x = eigenvectors[-1]
			k += 1
		self.iterations = np.array(range(k))
		self.mu = np.array(mu)
		self.lambdas = np.array(eigenvectors)
		self.errors = np.array(errors)
		return pd.DataFrame(data={"Iterations": self.iterations, "Mu": self.mu, "Lambdas": self.lambdas, "Errors": self.errors})

	def qr_algorithm(self):
		"""Approximate dominant eigenvalue and associated eigenvector of matrix, A.

		Source: https://www.youtube.com/watch?v=FAnNBw7d0vg

		Returns
		-------
		pandas.DataFrame : dataframe
			Summarized dataframe from iterations.

		Yields
		------
		self.iterations : tuple
			Collection of iterations through method.

		self.lambdas : tuple
			Collection of approximate eigenvectors.

		self.errors : tuple
			Collection of yielded norms.
		"""
		A, tol, N = self.A, self.tol, self.max_iter
		k, eigenvectors, errors = 1, [np.diag(A)], [1]
		while errors[-1] > tol and k <= N:
			Q = np.zeros_like(A, dtype=float)
			R = np.zeros_like(A, dtype=float)
			QI = []
			for j in range(len(A[0])):
				ai = np.array(np.zeros(len(A)))
				for i in range(len(A)):
					ai[i] = A[i][j]
				ai_perp = 0
				for i in range(j):
					R[i][j] = np.dot(ai, QI[i])
					ai_perp += R[i][j]*QI[i]
				ai -= ai_perp
				R[j][j] = np.sqrt(np.sum(ai**2))
				qi = ai/R[j][j]
				QI.append(qi)
				i = 0
				for q in qi:
					Q[i][j] = q
					i += 1
			A = np.matmul(R, Q)
			eigenvectors.append(np.diag(A))
			err = np.average([norms(np.diag(A, k=-1)).l_infinity(), norms(np.diag(A, k=1)).l_infinity()])
			errors.append(err)
			k += 1
		self.iterations = np.array(range(k))
		self.lambdas = np.array(eigenvectors)
		self.errors = np.array(errors)
		return pd.DataFrame(data={"Iterations": self.iterations, "Lambdas": self.lambdas, "Errors": self.errors})

	def steepest_descent(self, x, b):
		"""Approximate solution vector, x given matrix, A initial guess vector, x, and vector, b.

		Parameters
		----------
		x : array
			Numpy array.

		b : array
			Input numpy array.

		Returns
		-------
		pandas.DataFrame : dataframe
			Summarized dataframe from iterations.

		Yields
		------
		self.x : tuple
			Initial guess at eigenvector.

		self.b : tuple
			Input numpy array.

		self.iterations : tuple
			Collection of iterations through method.

		self.lambdas : tuple
			Collection of approximate eigenvectors.

		self.errors : tuple
			Collection of yielded norms.

		Raises
		------
		IndexError
			If x is neither n x 1 nor 1 x n array.

		IndexError
			If b is neither n x 1 nor 1 x n array.
		"""
		A, tol, N = self.A, self.tol, self.max_iter
		vec_name, x = "x", np.array(x)
		if np.sum(x.shape) - np.sum(x.shape[0]) > 1: raise IndexError(f"Systems vector, {vec_name} must be n x 1 or 1 x n array!")
		self.x = np.reshape(x,(len(x),1))
		vec_name, b = "b", np.array(b)
		if np.sum(b.shape) - np.sum(b.shape[0]) > 1: raise IndexError(f"Systems vector, {vec_name} must be n x 1 or 1 x n array!")
		self.b = np.reshape(b,(len(b),1))
		k, eigenvectors, errors = 1, [x], [1]
		while errors[-1] > tol and k <= N:
			r = b - np.matmul(A, x)
			alpha = float(np.matmul(r.T, r)[0]/np.matmul(np.matmul(r.T, A), r)[0])
			x1 = x + alpha*r
			eigenvectors.append(x1)
			errors.append(norms(x1, x).l_infinity())
			x = x1
			k += 1
		self.iterations = np.array(range(k))
		self.lambdas = np.array(eigenvectors)
		self.errors = np.array(errors)
		return pd.DataFrame(data={"Iterations": self.iterations, "Lambdas": self.lambdas, "Errors": self.errors})

	def conjugate_gradient(self, x, b, C=None):
		"""Approximate solution vector given matrix, A, initial guess vector, x, and vector, b.

		Parameters
		----------
		x : array
			Numpy array.

		b : vector
			Input numpy array.

		C : None or matrix, optional
			Preconditioning matrix.

		Returns
		-------
		pandas.DataFrame : dataframe
			Summarized dataframe from iterations.

		Yields
		------
		self.x : tuple
			Initial guess at eigenvector.

		self.b : tuple
			Input numpy array.

		self.iterations : tuple
			Collection of iterations through method.

		self.lambdas : tuple
			Collection of approximate eigenvectors.

		self.errors : tuple
			Collection of yielded norms.

		Raises
		------
		IndexError
			If x is neither n x 1 nor 1 x n array.

		IndexError
			If b is neither n x 1 nor 1 x n array.
		"""
		A, tol, N = self.A, self.tol, self.max_iter
		vec_name, x = "x", np.array(x)
		if np.sum(x.shape) - np.sum(x.shape[0]) > 1: raise IndexError(f"Systems vector, {vec_name} must be n x 1 or 1 x n array!")
		self.x = np.reshape(x,(len(x),1))
		vec_name, b = "b", np.array(b)
		if np.sum(b.shape) - np.sum(b.shape[0]) > 1: raise IndexError(f"Systems vector, {vec_name} must be n x 1 or 1 x n array!")
		self.b = np.reshape(b,(len(b),1))
		self.C = C
		r0 = b - np.matmul(A, x)
		if type(C) == type(None):
			do_precondition = True
			v0 = r0
		else:
			do_precondition = False
			Minv = np.linalg.inv(C*np.transpose(C))
			v0 = np.matmul(Minv, r0)
		k, eigenvectors, errors = 1, [x], [1]
		while errors[-1] > tol and k <= N:
			if do_precondition:
				alpha = float(np.matmul(r0.T, r0)[0]/np.matmul(np.matmul(v0.T, A)[0], v0)[0])
			else:
				alpha = float(np.matmul(np.matmul(r0.T, Minv), r0)[0]/np.matmul(np.matmul(v0.T, A), v0)[0])
			x1 = x + alpha*v0
			eigenvectors.append(x1)
			errors.append(norms(x1, x).l_infinity())
			r1 = r0 - alpha*np.matmul(A, v0)
			if do_precondition:
				s1 = float(np.matmul(r1.T, r1)[0]/np.matmul(r0.T, r0)[0])
			else: s1 = float(np.matmul(np.matmul(r1.T, Minv)[0], r1)[0]/np.matmul(np.matmul(r0.T, Minv)[0], r0)[0])
			x, r0 = x1, r1
			if do_precondition: v0 = r1 + s1*v0
			else: v0 = np.matmul(Minv, r1) + s1*v0
			k += 1
		self.iterations = np.array(range(k))
		self.eigenvectors = np.array(eigenvectors)
		self.errors = np.array(errors)
		return pd.DataFrame(data={"Iterations": self.iterations, "Lambdas": self.eigenvectors, "Errors": self.errors})
# --------------------

# --------------------
# iterative techniques
class SingleVariableIteration:
	def __init__(self, function, a, b, power=-6, variable=sp.Symbol("x"), iter_guess=True, k=0):
		"""
		Parameters
		----------
		function : expression
			Input function.

		a : float
			Left-hand bound of interval.

		b : float
			Right-hand bound of interval.

		power : float, optional
			Signed, specified power of tolerance until satisfying method.

		variable : symbol, optional
			Respected variable in derivative. Assumed to be 'x' if not stated.

		iter_guess : bool or integer, optional
			Boolean value of `True` by default. If integer, iterate for that integer.

		k : float, optional
			Absolute maximum slope of function.

		Yields
		------
		self.function : expression
			Input function.

		self.a : float
			Left-hand bound of interval.

		self.b : float
			Right-hand bound of interval.

		self.tol : float
			Tolerance to satisfy method.

		self.variable : symbol, optional
			Respected variable in derivative. Assumed to be `'x'` if not stated.

		self.iter_guess : bool or integer, optional
			Boolean value of `True` by default. If integer, iterate for that integer.

		self.k : float, optional
			Absolute maximum slope of functon. Assumed 0 if not defined.

		Raises
		------
		TypeError
			If input expression cannot be understood as lambda or sympy expression nor as string.

		Notes
		-----
		self.tol evaluated by: `10**power`.
		"""
		if isinstance(function, (FunctionType, sp.Expr)):
			sym_function = sp.N(sp.sympify(function(variable)))
			function = sp.lambdify(variable, sym_function)
			print(f"Information: Input expression, {sym_function} used.")
		# elif isinstance(f, (sp.Expr)):
		# 	f = sp.lambdify(variable, f)
		# 	self.function = f
		# 	print("sympy expression converted to lambda function.")
		elif isinstance(function, (str)):
			g = lambda x: eval(function)
			function = sp.lambdify(variable, g(variable))
			print("String expression converted to lambda function.")
		else: raise TypeError("Unknown input.")
		self.function, self.variable = function, variable
		self.a, self.b, self.tol = float(a), float(b), float(10**power)
		self.iter_guess, self.k = iter_guess, k

	def find_k(self):
		"""Find greatest integer for maximum iterations for tolerance.

		Returns
		-------
		k : float
			Maximum possible slope of input function.

		Yields
		------
		self.k : float
			Maximum possible slope of input function.

		Warnings
		--------
		Prints to console the input expression, and that the expression was in fact used.
		"""
		a, b, variable = self.a, self.b, self.variable
		sym_function = sp.N(sp.sympify(self.function(variable)))
		function = sp.lambdify(variable, sym_function)
		print(f"Information: Input expression, {sym_function} used.")
		k = self.k
		# determine form of derivative
		df = sp.lambdify(variable, sp.diff(sym_function))
		for alpha in np.linspace(a, b, 1000):
			df_alpha = abs(df(alpha))
			if df_alpha > k: k = df_alpha
		self.k = k
		return k

	def max_iterations(self, method, p0=0):
		"""Find greatest integer for maximum iterations for tolerance.

		Parameters
		----------
		method : string
			Selection of iterative method for iterations are needed.

		p0 : float, optional
			Initial guess for function solution.

		Returns
		-------
		max_iter : integer
			Maximum number of iterations required for specified tolerance.

		Yields
		------
		self.max_iter : integer
			Maximum number of iterations required for specified tolerance.

		Raises
		------
		ValueError
			Prescribed method is not an available option.

		Warnings
		--------
		Informs user the maximum number of iterations for method.

		Notes
		-----
		Will round away from zero to higher integers.

		Examples
		--------
		If `method == 'bisection'` & a=1, b=2, and tol=-3, then:

		`max_iter` >= -log(`tol`/(`b` - `a`))/log(2)

		`max_iter` >= -log((10**(-3)/(2 - 1))/log(2)

		`max_iter` >= 9.96

		`max_iter` = 10

		Else, if a=1, b=2, tol=-3, p0=1.5, nd k=0.9, then:
		`max_iter` >= log(`tol`/max('p0' - `a`, `b` - `p0`))/log(k)

		`max_iter` >= log(10**(-3)/max(1.5 - 1, 2 - 1.5))/log(0.9)

		`max_iter` >= log(10**(-3)/0.5)/log(0.9)

		`max_iter` >= 58.98

		`max_iter` >= 59
		"""
		a, b, tol, k = self.a, self.b, self.tol, self.k
		p0 = float(p0)
		if method == "bisection":
			max_iter = math.ceil(-math.log(tol/(b - a))/math.log(2))
		elif method in ("fixed_point", "newton_raphson", "secant_method", "false_position"):
			max_iter = math.ceil(-math.log(tol/max(p0 - a, b - p0))/math.log(k))
		else: raise ValueError(f"ERROR! I am sorry. The desired method must be: 'bisection', 'fixed_point', 'newton_raphson', 'secant_method', or 'false_position'.")
		self.max_iter = max_iter
		print(f"Information: With the inputs, I will terminate the technique after so many iterations, N = {max_iter}")
		return max_iter

	# next 5 functions preceded by find_k & max_iterations

	def bisection(self):
		"""Given f(x) in [a, b] find x within tolerance. Is a root-finding method: f(x) = 0.

		Returns
		-------
		pandas.DataFrame : dataframe
			Summarized dataframe from iterations.

		Yields
		------
		self.iterations : tuple
			Collection of iterations through method.

		self.approximations : tuple
			Collection of evaluated points, p.

		self.errors : tuple
			Collection of propogated error through method.

		Raises
		------
		ValueError
			If input for desired iterations was assigned not an integer.

		ValueError
			If initial guesses did not evaluate to have opposite signs.

		TypeError
			If input expression cannot be understood as lambda or sympy expression nor as string.

		Warnings
		--------
		Print to console if solution was found, or state that solution did not converge with given guess or prescribed tolerance.

		Notes
		-----
		Relying on the Intermediate Value Theorem, this is a bracketed, root-finding method. Generates a sequence {p_n}^{inf}_{n=1} to approximate a zero of f(x), p and converges by O(1 / (2**N)).

		Examples
		--------
		If  f(x) = x**3 + 4*x**2 = 10

		=>  f(x) = x**3 + 4*x**2 - 10 = 0
		"""
		f, a, b, tol = self.function, self.a, self.b, self.tol
		iter_guess = self.iter_guess
		# calculate if expression
		if isinstance(f, (FunctionType, sp.Expr)):
			sym_function = sp.N(sp.sympify(f(self.variable)))
			f = sp.lambdify(self.variable, sym_function)
			# check if f(a) and f(b) are opposite signs
			if f(a)*f(b) < 0:
				if iter_guess == True:
					# if left unassigned, guess
					N = self.max_iterations("bisection")
				elif isinstance(iter_guess, (int, float)):
					# if defined as integer, use
					N = int(iter_guess)
				# else, break for bad assignment
				else: raise ValueError(f"ERROR! Maximum iterations, N must be an integer greater than zero. {iter_guess} was given and not understood.")
				# initialize
				k, approximations, errors = 0, [f(a)], [1]
				# exit by whichever condition is TRUE first
				while errors[-1] >= tol and k <= N:
					x = (b - a)/2
					p = a + x 	# new value, p
					approximations.append(p)
					if f(a)*f(p) > 0: a = p 	# adjust next bounds
					else: b = p
					errors.append(abs(x)) 	# error of new value, p
					k += 1 	# iterate to k + 1
				if k <= N: print("Congratulations! Solution found!")
				else: print("Warning! Solution could not be found with initial guess or tolerance.")
				self.iterations = np.array(range(k))
				self.approximations = np.array(approximations)
				self.errors = np.array(errors)
				return pd.DataFrame(data={"Iterations": self.iterations, "Approximations": self.approximations, "Errors": self.errors})
			# abort if f(a) is not opposite f(b)
			else: raise ValueError(f"ERROR! Interval bounds, [a, b] = [{a}, {b}] must yield opposite signs in function, {sym_function}.")
		# abort if not expression
		else: raise TypeError("ERROR! The input function must be an expression.")

	def false_position(self, p0, p1):
		"""Given f(x) and initial guesses, p0 and p1 in [a, b] find x within tolerance.

		Root-finding problem: f(x) = 0. 

		!!! Use lowest k !!!

		Parameters
		----------
		p0 : float
			First initial guess.

		p1 : float
			Second initial guess.

		Returns
		-------
		pandas.DataFrame : dataframe
			Summarized dataframe from iterations.

		Yields
		------
		self.iterations : tuple
			Collection of iterations through method.

		self.approximations : tuple
			Collection of evaluated points, p.

		self.errors : tuple
			Collection of propogated error through method.

		Raises
		------
		ValueError
			If input for desired iterations was assigned not an integer.

		ValueError
			If initial guesses did not evaluate to have opposite signs.

		TypeError
			If input expression cannot be understood as lambda or sympy expression nor as string.

		Warnings
		--------
		Print to console if solution was found, or state that solution did not converge with given guess or prescribed tolerance.

		Notes
		-----
		Check that |g'(x)| <= (leading coefficient of g'(x)) for all x in [a, b].

		Theorem:
		1) Existence of a fixed-point:
			If g in C[a,b] and g(x) in C[a, b] for all x in [a, b], then function, g has a fixed point in [a, b].

		2) Uniqueness of a fixed point:
			If g'(x) exists on [a, b] and a positive constant, k < 1 exist with {|g'(x)| <= k  |  x in (a, b)}, then there is exactly one fixed-point, p in [a, b].

		Converges by O(linear) if g'(p) != 0, and O(quadratic) if g'(p) = 0 and g''(p) < M, where M = g''(xi) that is the error function.

		Examples 
		--------
		If  g(x) = x**2 - 2

		Then	p = g(p) = p**2 - 2

		=>  p**2 - p - 2 = 0
		"""
		f, a, b, tol = self.function, self.a, self.b, self.tol
		iter_guess, k = self.iter_guess, self.k
		p0, p1 = float(p0), float(p1)
		self.p0, self.p1 = p0, p1
		# calculate if expression
		if isinstance(f, (FunctionType, sp.Expr)):
			sym_function = sp.N(sp.sympify(f(self.variable)))
			f = sp.lambdify(self.variable, sym_function)
			# check if f(a) and f(b) are opposites signs
			if f(p0)*f(p1) < 0:
				if iter_guess == True and k == 0:
					# if left unassigned, guess
					N = self.max_iterations("false position", p0=p0)
				elif iter_guess == True and k != 0:
					# if left unassigned, guess
					N = self.max_iterations("false position", k=k, p0=p0)
				elif isinstance(iter_guess, (int, float)):
					# if defined as integer, use
					N = int(iter_guess)
				# else, break for bad assignment
				else: raise ValueError(f"ERROR! Maximum iterations, N must be an integer greater than zero. {iter_guess} was given and not understood.")
				# initialize
				k, approximations, errors = 0, [f(a)], [1]
				# exit by whichever condition is TRUE first
				while errors[-1] >= tol and k <= N:
					q0, q1 = f(p0), f(p1)
					p = p1 - q1*(p1 - p0)/(q1 - q0) 	# new value, p
					approximations.append(p)
					errors.append(abs(p - p0)) 	# error of new value, p
					if f(p)*q1 < 0: p0 = p1 	# adjust next bounds
					p1 = p
					k += 1 	# iterate to k + 1
				if k <= N: print("Congratulations! Solution found!")
				else: print("Warning! Solution could not be found with initial guess or tolerance.")
				self.iterations = np.array(range(k))
				self.approximations = np.array(approximations)
				self.errors = np.array(errors)
				return pd.DataFrame(data={"Iterations": self.iterations, "Approximations": self.approximations, "Errors": self.errors})
			# abort if f(a) is not opposite f(b)
			else: raise ValueError(f"ERROR! Interval bounds, [a, b] = [{a}, {b}] must yield opposite signs in function, {sym_function}.")
		# abort if not expression
		else: raise TypeError("ERROR! The input function must be an expression.")

	def fixed_point(self, p0):
		"""Given f(x) and initial guess, p0 in [a, b] find x within tolerance.

		Root-finding problem: f(x) = 0. 

		!!! Use lowest k !!!

		Parameters
		----------
		p0 : float
			Initial guess.

		Returns
		-------
		pandas.DataFrame : dataframe
			Summarized dataframe from iterations.

		Yields
		------
		self.iterations : tuple
			Collection of iterations through method.

		self.approximations : tuple
			Collection of evaluated points, p.

		self.errors : tuple
			Collection of propogated error through method.

		Raises
		------
		ValueError
			If input for desired iterations was assigned not an integer.

		ValueError
			If initial guesses did not evaluate to have opposite signs.

		TypeError
			If input expression cannot be understood as lambda or sympy expression nor as string.

		Warnings
		--------
		Print to console if solution was found, or state that solution did not converge with given guess or prescribed tolerance.

		Notes
		-----
		Check that |g'(x)| <= (leading coefficient of g'(x)) for all x in [a, b].

		Theorem:
		1) Existence of a fixed-point:
			If g in C[a, b] and g(x) in C[a, b] for all x in [a, b], then function, g has a fixed point in [a, b].

		2) Uniqueness of a fixed point:
			If g'(x) exists on [a, b] and a positive constant, k < 1 exist with {|g'(x)| <= k  |  x in (a, b)}, then there is exactly one fixed-point, `p` in [a, b].

		Converges by O(linear) if g'(p) != 0, and O(quadratic) if g'(p) = 0 and g''(p) < M, where M = g''(xi) that is the error function.

		Examples 
		--------
		If  g(x) = x**2 - 2

		Then	p = g(p) = p**2 - 2
		
		=>  p**2 - p - 2 = 0
		"""
		f, a, b, tol = self.function, self.a, self.b, self.tol
		iter_guess, k = self.iter_guess, self.k
		p0 = float(p0)
		self.p0 = p0
		# calculate if expression
		if isinstance(f, (FunctionType, sp.Expr)):
			sym_function = sp.N(sp.sympify(f(self.variable)))
			f = sp.lambdify(self.variable, sym_function)
			if iter_guess == True and k == 0:
				# if left unassigned, guess
				N = self.max_iterations("fixed point", p0=p0)
			elif iter_guess == True and k != 0:
				# if left unassigned, guess
				N = self.max_iterations("fixed point", k=k, p0=p0)
			elif isinstance(iter_guess, (int, float)):
				# if defined as integer, use
				N = int(iter_guess)
			# else, break for bad assignment
			else: raise ValueError(f"ERROR! Maximum iterations, N must be an integer greater than zero. {iter_guess} was given and not understood.")
			# initialize
			k, approximations, errors = 0, [f(a)], [1]
			# exit by whichever condition is TRUE first
			while errors[-1] >= tol and k <= N:
				p = f(p0) 	# new value, p
				approximations.append(p)
				errors.append(abs((p - p0)/p0)) # error of new value, p
				p0 = p 	# set future previous value
				k += 1 	# iterate to k + 1
			if k <= N: print("Congratulations! Solution found!")
			else: print("Warning! Solution could not be found with initial guess or tolerance.")
			self.iterations = np.array(range(k))
			self.approximations = np.array(approximations)
			self.errors = np.array(errors)
			return pd.DataFrame(data={"Iterations": self.iterations, "Approximations": self.approximations, "Errors": self.errors})
		# abort if not expression
		else: raise TypeError("ERROR! The input function must be an expression.")

	def newton_raphson(self, p0):
		"""Given f(x) and initial guess, p0 in [a, b], find x within tolerance.

		Root-finding problem: f(x) = 0. 

		!!! Use lowest k !!!

		Parameters
		----------
		p0 : float
			Initial guess.

		Returns
		-------
		pandas.DataFrame : dataframe
			Summarized dataframe from iterations.

		Yields
		------
		self.iterations : tuple
			Collection of iterations through method.

		self.approximations : tuple
			Collection of evaluated points, p.

		self.errors : tuple
			Collection of propogated error through method.

		Raises
		------
		ValueError
			If input for desired iterations was assigned not an integer.

		ValueError
			If initial guesses did not evaluate to have opposite signs.

		TypeError
			If input expression cannot be understood as lambda or sympy expression nor as string.

		Warnings
		--------
		Print to console if solution was found, or state that solution did not converge with given guess or prescribed tolerance.

		Notes
		-----
		f'(x) != 0.

		Not root-bracketed.

		Initial guess must be close to real solution; else, will converge to different root or oscillate (if symmetric).

		Check that |g'(x)| <= (leading coefficient of g'(x)) for all x in [a, b].

		Technique based on first Taylor polynomial expansion of f about p0 and evaluated at x = p. |p - p0| is assumed small; therefore, 2nd order Taylor term, the error, is small.

		Newton-Raphson has quickest convergence rate.

		This method can be viewed as fixed-point iteration.

		Theorem:
		1) Existence of a fixed-point:
			If g in C[a, b] and g(x) in C[a, b] for all x in [a, b], then function, g has a fixed point in [a, b].

		2) Uniqueness of a fixed point:
			If g'(x) exists on [a, b] and a positive constant, `k` < 1 exist with {|g'(x)| <= k  |  x in (a, b)}, then there is exactly one fixed-point, `p` in [a, b].

		Converges by O(linear) if g'(p) != 0, and O(quadratic) if g'(p) = 0 and g''(p) < M, where M = g''(xi) that is the error function.

		Examples 
		--------
		If  g(x) = x**2 - 2

		Then	p = g(p) = p**2 - 2

		=>  p**2 - p - 2 = 0
		"""
		f, a, b, tol = self.function, self.a, self.b, self.tol
		iter_guess, k = self.iter_guess, self.k
		p0 = float(p0)
		self.p0 = p0
		# calculate if expression
		if isinstance(f,(FunctionType, sp.Expr)):
			sym_function = sp.N(sp.sympify(f(self.variable)))
			f = sp.lambdify(self.variable, sym_function)
			# determine form of derivative
			df = sp.lambdify(self.variable, sp.diff(sym_function))
			if iter_guess == True and k == 0:
				# if left unassigned, guess
				N = self.max_iterations("newton raphson", p0=p0)
			elif iter_guess == True and k != 0:
				# if left unassigned, guess
				N = self.max_iterations("newton raphson", k=k, p0=p0)
			elif isinstance(iter_guess, int):
				# if defined as integer, use
				N = iter_guess
			# else, break for bad assignment
			else: raise ValueError(f"ERROR! Maximum iterations, N must be an integer greater than zero. {iter_guess} was given and not understood.")
			# initialize
			k, approximations, errors = 0, [f(a)], [1]
			# exit by whichever condition is TRUE first
			while errors[-1] >= tol and k <= N:
				fp0 = f(p0)
				dfp0 = df(p0)
				p = p0 - (fp0/dfp0)	 # new value, p
				approximations.append(p)
				errors.append(abs(p - p0)) 	# error of new value, p
				p0 = p 	# set future previous value
				k += 1 	# iterate to k + 1
			if k <= N: print("Congratulations! Solution found!")
			else: print("Warning! Solution could not be found with initial guess or tolerance.")
			self.iterations = np.array(range(k+1))
			self.approximations = np.array(approximations)
			self.errors = np.array(errors)
			return pd.DataFrame(data={"Iterations": self.iterations, "Approximations": self.approximations, "Errors": self.errors})
		# abort if not expression
		else: raise TypeError("ERROR! The input function must be an expression.")

	def secant_method(self, p0, p1):
		"""Given f(x) and initial guesses, p0 and p1 in [a, b], find x within tolerance.
		Root-finding problem: f(x) = 0. 

		!!! Use lowest k !!!

		Parameters
		----------
		p0 : float
			First initial guess.

		p1 : float
			Second initial guess.

		Returns
		-------
		pandas.DataFrame : dataframe
			Summarized dataframe from iterations.

		Yields
		------
		self.iterations : tuple
			Collection of iterations through method.

		self.approximations : tuple
			Collection of evaluated points, p.

		self.errors : tuple
			Collection of propogated error through method.

		Raises
		------
		ValueError
			If input for desired iterations was assigned not an integer.

		ValueError
			If initial guesses did not evaluate to have opposite signs.

		TypeError
			If input expression cannot be understood as lambda or sympy expression nor as string.

		Warnings
		--------
		Print to console if solution was found, or state that solution did not converge with given guess or prescribed tolerance.

		Notes
		-----
		Not root-bracketed.

		Bypasses need to calculate derivative (as in Newton-Raphson).

		Check that |g'(x)| <= (leading coefficient of g'(x)) for all x in [a, b].

		Theorem:
		1) Existence of a fixed-point:
			If g in C[a, b] and g(x) in C[a, b] for all x in [a, b], then function, g has a fixed point in [a, b].

		2) Uniqueness of a fixed point:
			If g'(x) exists on [a, b] and a positive constant, `k` < 1 exist with {|g'(x)| <= k  |  x in (a, b)}, then there is exactly one fixed-point, `p` in [a, b].

		Converges by O(linear) if g'(p) != 0, and O(quadratic) if g'(p) = 0 and g''(p) < M, where M = g''(xi) that is the error function.

		Examples 
		--------
		If  g(x) = x**2 - 2

		Then	p = g(p) = p**2 - 2

		=>  p**2 - p - 2 = 0
		"""
		f, a, b, tol = self.function, self.a, self.b, self.tol
		iter_guess, k = self.iter_guess, self.k
		p0, p1 = float(p0), float(p1)
		self.p0, self.p1 = p0, p1
		# calculate if expression
		if isinstance(f, (FunctionType, sp.Expr)):
			sym_function = sp.N(sp.sympify(f(self.variable)))
			f = sp.lambdify(self.variable, sym_function)
			# check if f(a) and f(b) are opposite signs
			if f(p0)*f(p1) < 0:
				if iter_guess == True and k == 0:
					# if left unassigned, guess
					N = self.max_iterations("secant method", p0=p0)
				elif iter_guess == True and k != 0:
					# if left unassigned, guess
					N = self.max_iterations("secant method", k=k, p0=p0)
				elif isinstance(iter_guess, (int, float)):
					# if defined as integer, use
					N = (iter_guess)
				# else, break for bad assignment
				else: raise ValueError(f"ERROR! Maximum iterations, N must be an integer greater than zero. {iter_guess} was given and not understood.")
				# initialize
				k, approximations, errors = 0, [f(a)], [1]
				# exit by whichever condition is TRUE first
				while errors[-1] >= tol and k <= N:
					q0, q1 = f(p0), f(p1)
					# new value, p
					p = p1 - q1*(p1 - p0)/(q1 - q0)
					approximations.append(p)
					errors.append(abs(p - p0)) 	# error of new value
					p0, p1 = p1, p 	# set future previous values
					k += 1 	# iterate to k + 1
				if k <= N: print("Congratulations! Solution found!")
				else: print("Warning! Solution could not be found with initial guess or tolerance.")
				self.iterations = np.array(range(k))
				self.approximations = np.array(approximations)
				self.errors = np.array(errors)
				return pd.DataFrame(data={"Iterations": self.iterations, "Approximations": self.approximations, "Errors": self.errors})
			# abort if f(a) is not opposite f(b)
			else: raise ValueError(f"ERROR! Interval bounds, [a, b] = [{a}, {b}] must yield opposite signs in function, {sym_function}.")
		# abort if not expression
		else: raise TypeError("ERROR! The input function must be an expression.")

class MultiVariableIteration:
	def __init__(self, A, x0, b, power=-6, max_iter=100, norm_type="l_infinity"):
		"""
		Parameters
		----------
		A : tuple
			Either input functions or matrix of characteristic values.

		x0 : tuple
			Either collection of symbols or initial guesses for system of equations.

		b : tuple
			Input vector.

		power : float, optional
			Signed, specified power of tolerance until satisfying method.

		max_iter : integer, optional
			Number of iterations.

		norm_type : string, optional
			String representation of desired norm function. `'l_infinity'` by default.

		Yields
		------
		self.A : tuple
			Either input functions or matrix of characteristic values.

		self.x0 : tuple
			Either collection of symbols or initial guesses for system of equations.

		self.b : tuple
			Input vector.

		self.tol : float
			Specified tolerance to which method terminates.

		self.max_iter : int
			Maximum iterations allowed for method.

		self.norm_type : string
			String representation of desired norm function.

		self.is_diagonal : bool
			Truth value of whether matrix is diagonal.

		self.is_symmetric : bool
			Truth value of whether matrix is symmetric.

		self.is_tridiagonal : bool
			Truth value of whether matrix is tridiagonal.

		self.eigen_values : tuple
			Eigenvalues of characteristic matrix, A.

		self.spectral_radius : float
			Spectral radius of characteristic matrix, A.

		self.condition_number : float
			Condition number of characteristic matrix, A. 

		Raises
		------
		IndexError
			Matrix of interest must be square.

		IndexError
			If x0 is neither n x 1 nor 1 x n array.

		IndexError
			If b is neither n x 1 nor 1 x n array.

		ValueError
			If iterations constraint is not an integer.

		ValueError
			If desired norm method was neither `'l_infinity'` nor `'l_two'`.

		Warnings
		--------
		Not recommended to use eigen_values() to find eigenvalues of characteristic matrix, A; therefore, if desiring quick calculations, do not use if matrix, A is a large, sparse matrix.

		See Also
		--------
		eigen_values() : Function to find eigenvalues of matrix, A.

		spectral_radius() : Function to find the spectral radius of characteristic matrix, A.

		Notes
		-----
		Specified tolerance evaluated by: `10**power`.

		norm_type may be either `'l_infinity'` or `'l_two'`. Is 'l_infinity' by default.

		If `self.is_diagonal` is True, then matrix is diagonal. Else, not diagonal.
		"""
		matrix_name, vec_name, sys_name = "A", "x0", "b"
		A, x0, b = np.array(A), np.array(x0), np.array(b)
		if np.sum(A.shape[0]) != np.sum(A.shape[1]): raise IndexError(f"ERROR! Matrix, {matrix_name} must be square!")
		if np.sum(x0.shape) - np.sum(x0.shape[0]) > 1: raise IndexError(f"Systems vector, {vec_name} must be n x 1 or 1 x n array!")
		if np.sum(b.shape) - np.sum(b.shape[0])> 1: raise IndexError(f"Systems vector, {sys_name} must be n x 1 or 1 x n array!")
		if max_iter <= 0 or not isinstance(max_iter, (int, float)): ValueError(f"ERROR! Maximum iterations, N must be an integer greater than zero. {max_iter} was given and not understood.")
		if norm_type != "l_infinity" and norm_type != "l_two": raise ValueError("ERROR! Desired norm type was not understood. Please choose 'l_infinity' or 'l_two'.")
		n = len(x0)
		self.A = A
		self.x0 = np.reshape(x0,(n,1))
		self.b = np.reshape(b,(n,1))
		self.tol = float(10**power)
		self.max_iter = int(max_iter)
		self.norm_type = norm_type
		self.is_diagonal = diagonality(A)
		self.is_symmetric = symmetry(A)
		self.is_tridiagonal = tridiagonality(A)
		# self.eigen_values = eigen_values(A)
		# self.spectral_radius = spectral_radius(A)
		# self.condition_number = condition_number(A, norm_type)

	def __find_xk(self, x):
		return np.matmul(self.T, x) + self.c

	def find_omega(self, omega=0):
		"""Given the characteristic matrix and solution vector, determine if prescribed omega is the optimum choice.

		Parameters
		----------
		omega : float, optional
			Relaxation parameter.

		Returns
		-------
		omega : float
			If found, is the optimum choice of omega.

		Yields
		------
		self.user_omega : float
			Supplied/default omega.

		self.is_tridiagonal : bool
			Truth value of whether matrix, A is tridiagonal.

		self.best_omega : float
			If found, is the optimum choice of omega.

		Warnings
		--------
		If 0 < omega < 2, then method will converge regardless of choice for x0. Will inform user that matrix, A is not tridiagonal, but will proceed with calculation all the same. If matrix, A is poorly defined and not found to be positive definite, then user is informed but calculation proceeds. If an optimal omega cannot be found, then `self.best_omega` assigned from supplied/default omega.

		See Also
		--------
		tridiagonality() : Determines if matrix, A is tridiagonal or not.

		spectral_radius() : Uses the spectral radius of Gauss-Seidel's T-matrix to calculate omega.

		Notes
		-----
		Unless specified, omega will be 0 and chosen, if possible.
		"""
		matrix_name = "A"
		A, x0, omega = np.array(self.A), np.array(self.x0), float(omega)
		self.user_omega = omega
		xn = sp.Matrix(np.reshape(np.zeros_like(x0), (len(x0), 1)))
		xt = sp.Matrix(np.reshape(np.zeros_like(x0), (1, len(x0))))
		i = 0
		for x in np.array(x0): xn[i], xt[i] = x, x; i += 1
		y = xt*sp.Matrix(A)*xn
		if y[0] > 0: state = True
		else: state = False
		if self.is_symmetric and state: theorem_6_22 = True
		else: theorem_6_22 = False
		i, theorem_6_25 = 1, True
		while i <= len(A) and theorem_6_25 == True:
			Ai = sp.Matrix(A[:i,:i])
			if sp.det(Ai) > 0: theorem_6_25 = True
			else : theorem_6_25 = False
			i += 1
		if theorem_6_22 or theorem_6_25:
			if 0 < omega and omega < 2: print("According to Ostrowski-Reich's Theorem, the successive relaxation technique will converge.")
			if self.is_tridiagonal:
				D = np.diagflat(np.diag(A))
				L = np.diagflat(np.diag(A, k=-1), k=-1)
				U = np.diagflat(np.diag(A, k=1), k=1)
				DL = D - L
				i, DL_inv = 0, np.zeros_like(DL)
				while i < len(DL_inv):
					j = 0
					while j < len(DL_inv[0]):
						dl = DL[i][j]
						if dl != 0: DL_inv[i][j] = 1/(dl)
						j += 1
					i += 1
				Tg = DL_inv*U
				omega = 2 / (1 + math.sqrt(1 - spectral_radius(Tg)))
				print(f"I believe {omega} would be the best choice.")
			else:
				print(f"Warning! Matrix, {matrix_name} is not tridiagonal.")
				print(f"Assigning supplied omega, {omega} as `self.best_omega`.")
		else:
			print(f"Warning! Matrix, {matrix_name} is not positive definite.")
			print(f"Assigning supplied omega, {omega} as `self.best_omega`.")
		self.best_omega = omega
		return omega

	def gauss_seidel(self):
		"""Given A*x = b, use `self.norm_type` to find x via the Gauss-Seidel Method.

		Returns
		-------
		pandas.DataFrame : dataframe
			Summarized dataframe from iterations.

		Yields
		-------
		self.iterations : tuple
			Running collection of iterations through method.

		self.approximations : tuple
			Finally evaluated solution.

		self.errors : tuple
			Aggregate of yielded norms.

		Warnings
		--------
		Prints to console whether or not a solution was found within the specified tolerance with the supplied, initial guess.

		See Also
		--------
		norms.l_infinity() : Will find the l_infinity norm between x0 and xi.

		norms.l_two() : Will find the l_2 norm between x0 and xi.

		Notes
		-----
		gauss_seidel():
			[x]_(k) = ( (D - L)^(-1) * U ) * [x]_(k - 1) + ( (D - L)^(-1) )*[b]
		"""
		A, x0, b, tol, N = self.A, self.x0, self.b, self.tol, self.max_iter
		norm_type, norm = self.norm_type, tol*10
		# A = np.zeros((N, N))
		# np.fill_diagonal(A, ai)
		# A = A + np.diagflat(bi, 1)
		# A = A + np.diagflat(ci, -1)
		# x0 = np.zeros(N)
		# b = np.array(di)
		# A1, A2 = np.zeros((n, n)), np.zeros((n, n))
		# np.fill_diagonal(A1, np.diagonal(A))
		# A1 = A1 - np.tril(A, k=-1)
		# i = 0
		# while i < n:
		# 	j = 0
		# 	while j <= i:
		# 		a1ij = A1[i][j]
		# 		if a1ij != 0:
		# 			A2[i][j] = 1/a1ij
		# 		j += 1
		# 	i += 1
		# self.T = np.matmul(A2, np.triu(A, k=1))
		# self.c = np.matmul(A2, b)
		k, n, approximations, errors = 1, len(x0), [x0], [norm]
		while errors[-1] > tol and k <= N:
			i, xi = 0, np.zeros_like(x0)
			while i < n:
				j, y1, y2 = 0, 0., 0.
				while j <= i-1:
					y1 += A[i][j]*xi[j]
					j += 1
				j = i + 1
				while j < n:
					y2 += A[i][j]*x0[j]
					j += 1
				xi[i] = (-y1 - y2 + b[i])/A[i][i]
				i += 1
			# xi = self.__find_xk(x0)
			if norm_type == "l_infinity":
				norm = norms(xi, x0).l_infinity()
			elif norm_type == "l_two":
				norm = norms(xi, x0).l_two()
			approximations.append(xi)
			errors.append(norm)
			x0 = xi
			k += 1
		if k <= N: print("Congratulations! Solution found!")
		else: print("Warning! Solution could not be found with initial guess or tolerance.")
		# m, n = len(approximations[0]), len(approximations)
		# j, x = 0, np.zeros((m,n))
		# while j < n:
		# 	i = 0
		# 	while i < m:
		# 		x[i][j] = float(approximations[j][i])
		# 		i += 1
		# 	j += 1
		self.iterations = np.array(range(k))
		self.approximations = np.array(approximations)
		self.errors = np.array(errors)
		return pd.DataFrame(data={"Iterations": self.iterations, "Approximations": self.approximations, "Error": self.errors})

	def jacobi(self):
		"""Given A*x = b, use `self.norm_type` to find x via the Jacobi Method.

		Returns
		-------
		pandas.DataFrame : dataframe
			Summarized dataframe from iterations.

		Yields
		-------
		self.iterations : tuple
			Collection of iterations through method.

		self.approximations : tuple
			Collection of approximated, iterative solutions.

		self.errors : tuple
			Collection of yielded norms.

		Warnings
		--------
		Prints to console whether or not a solution was found within the specified tolerance with the supplied, initial guess.

		See Also
		--------
		norms.l_infinity() : Will find the l_infinity norm between x0 and xi.

		norms.l_two() : Will find the l_2 norm between x0 and xi.

		Notes
		-----
		jacobi():
		[x]_(k) = ( D^(-1)*(L + U) ) * [x]_(k - 1) + ( D^(-1) ) * [b]
		"""
		A, x0, b, tol, N = self.A, self.x0, self.b, self.tol, self.max_iter
		norm_type, norm = self.norm_type, tol*10
		k, n, approximations, errors = 1, len(x0), [x0], [norm]
		while errors[-1] > tol and k <= N:
			i, xi = 0, np.zeros_like(x0)
			while i < n:
				j, y = 0, 0.
				while j < n:
					if j != i:
						y += A[i][j]*x0[j]
					j += 1
				xi[i] = (-y + b[i])/A[i][i]
				i += 1
			if norm_type == "l_infinity":
				norm = norms(xi, x0).l_infinity()
			elif norm_type == "l_two":
				norm = norms(xi, x0).l_two()
			approximations.append(xi)
			errors.append(norm)
			x0 = xi
			k += 1
		if k <= N: print("Congratulations! Solution found!")
		else: print("Warning! Solution could not be found with initial guess or tolerance.")
		# m, n = len(approximations[0]), len(approximations)
		# X_matrix, j = np.zeros((m,n)), 0
		# while j < n:
		# 	i = 0
		# 	while i < m:
		# 		X_matrix[i][j] = float(approximations[j][i])
		# 		i += 1
		# 	j += 1
		self.iterations = np.array(range(k))
		self.approximations = np.array(approximations)
		self.errors = np.array(errors)
		return pd.DataFrame(data={"Iterations": self.iterations, "Approximations": self.approximations, "Error": self.errors})

	# def newton_raphson(self, functions, symbols, x0, powers, max_iter=100, norm_type=None):
	# 	"""Given an array of functions, symbols, and initial guesses, employ the Newton-Raphson Method to find solution within tolerance.

	# 	Root-finding problem: f(x) = 0. 

	# 	!!! Use lowest k !!!

	# 	Parameters
	# 	----------

	# 	functions

	# 	symbols

	# 	x0

	# 	powers

	# 	max_iter

	# 	nomr_type

	# 	p0 : float
	# 		Initial guess.

	# 	k : float, optional
	# 		Absolute maximum slope of function.

	# 	Yields
	# 	-------
	# 	self.iterations : tuple
	# 		Collection of iterations through method.

	# 	self.approximations : tuple
	# 		Collection of approximated, iterative solutions.

	# 	self.errors : tuple
	# 		Collection of yielded norms.

	# 	Raises
	# 	------
	# 	__bad_iter : string
	# 	If input for desired iterations was assigned not an integer.

	# 	__must_be_expression : string
	# 		If input `f` was of array, list, tuple, etcetera...

	# 	Warns
	# 	-----
	# 	__solution_found : string
	# 		Inform user that solution was indeed found.

	# 	__solution_not_found : string
	# 		If initial guess or tolerance were badly defined.

	# 	Notes
	# 	-----
	# 	f'(x) != 0.

	# 	Not root-bracketed.

	# 	Initial guess must be close to real solution; else, will converge to different root or oscillate (if symmetric).

	# 	Check that |g'(x)| <= (leading coefficient of g'(x)) for all x in [a, b].

	# 	Technique based on first Taylor polynomial expansion of `f` about `p0` and evaluated at x = p. |p - p0| is assumed small; therefore, 2nd order Taylor term, the error, is small.

	# 	Newton-Raphson has quickest convergence rate.

	# 	This method can be viewed as fixed-point iteration.

	# 	Theorem:
	# 	1) Existence of a fixed-point:
	# 		If g in C[a, b] and g(x) in C[a, b] for all x in [a, b], then function, g has a fixed point in [a, b].

	# 	2) Uniqueness of a fixed point:
	# 		If g'(x) exists on [a, b] and a positive constant, `k` < 1 exist with {|g'(x)| <= k  |  x in (a, b)}, then there is exactly one fixed-point, `p` in [a, b].

	# 	Converges by O(linear) if g'(p) != 0, and O(quadratic) if g'(p) = 0 and g''(p) < M, where M = g''(xi) that is the error function.

	# 	Examples 
	# 	--------
	# 	If  g(x) = x**2 - 2

	# 	Then	p = g(p) = p**2 - 2

	# 	=>  p**2 - p - 2 = 0
	# 	"""
	# 	def jacobian(g, sym_x, x):
	# 		n = len(x)
	# 		jacMatrix = np.zeros((n, n))
	# 		for i in range(0, n):
	# 			for j in range(0, n):
	# 				J_ij = sp.diff(g[i](*sym_x), sym_x[j])
	# 				temp = sp.lambdify(sym_x, J_ij)(*x)
	# 				if isinstance(temp, type(np.array([1]))): temp = temp[0]
	# 				jacMatrix[i][j] = temp
	# 		return
	# 	norm_type = self.norm_type
	# 	functions, x0, b, norm = self.A, self.x0, self.b, self.tol*10
	# 	xi = np.zeros_like(x0)
	# 	X0, error = [], []
	# 	k, n = 0, len(x0)
	# 	for symbol in symbols:
	# 		if isinstance(symbol, (str, type(sp.Symbol("x")))): continue
	# 		else: raise TypeError(f"All elements of `symbols` must be of type string or symbol: {symbol} was neither.")
	# 	if max_iter <= 0 or not isinstance(max_iter, (int, float)): ValueError(f"ERROR! Maximum iterations, N must be an integer greater than zero. {max_iter} was given and not understood.")
	# 	if norm_type == None:
	# 		tol = []
	# 		for p in powers: tol.append(10**p)
	# 	else: tol = 10**powers
	# 	functions, x0 = np.reshape(functions, (1, n))[0], np.reshape(x0, (n, 1))
	# 	X0.append(x0)
	# 	error.append(tol)
	# 	for k in range(1, max_iter):
	# 		J = jacobian(functions, symbols, x0)
	# 		xk, g = np.zeros_like(x0), np.zeros_like(x0)
	# 		for i in range(0, n): 
	# 			g[i] = sp.lambdify(symbols, functions[i](*symbols))(*x0)
	# 		y0 = np.linalg.solve(J, -g)
	# 		xk = x0 + y0
	# 		if norm_type == "l_two":
	# 			boolean = []
	# 			for i in range(0, n-1):
	# 				if abs(xk[i] - x0[i])[0] <= tol[i]: boolean.append(1)
	# 				else: boolean.append(0)
	# 			x0 = xk
	# 			if sum(boolean) < n: continue
	# 			else: break
	# 		elif norm_type == "l_infinity":
	# 			norm = norms.l_infinity(xk, x0)
	# 			error.append(norm)
	# 			X0.append(xk)
	# 			tol_exit = 0
	# 			for tl in tol:
	# 				if norm <= tl: tol_exit += 0
	# 				else: tol_exit += 1
	# 			if tol_exit == 0:
	# 				self.iterations = np.array(range(k))
	# 				self.approximations = np.array(X0)
	# 				self.errors = np.array(error)
	# 				return pd.DataFrame(data={"Iterations": self.iterations, "Approximations": self.approximations, "Error": self.errors})
	# 			else: x0 = xk
	# 		else: raise ValueError("ERROR! Desired norm type was not understood. Please choose 'l_infinity' or 'l_two'.")
	# 	return x0

	def successive_relaxation(self, omega=None):
		"""Given A*x = b, use `self.norm_type` to find vector, x via the Successive Relaxtion Method. Is Successive Over-Relaxation if omega > 1, Successive Under-Relaxation if omega < 1, and is Gauss-Seidel if omega = 1.

		Parameters
		----------
		omega : None or float, optional
			Relaxation parameter.

		Returns
		-------
		pandas.DataFrame : dataframe
			Summarized dataframe from iterations.

		Yields
		-------
		self.iterations : tuple
			Collection of iterations through method.

		self.approximations : tuple
			Collection of approximated, iterative solutions.

		self.errors : tuple
			Collection of yielded norms.

		Warnings
		--------
		Prints to console optimal choice of omega, regardless of assignment, and whether or not a solution was found within the specified tolerance with the supplied, initial guess.

		See Also
		--------
		norms.l_infinity() : Will find the l_infinity norm between x0 and xi.

		norms.l_two() : Will find the l_2 norm between x0 and xi.

		find_omega() : Will analyze system of equation to find an optimal omega, if possible, and inform user.

		gauss_seidel() : Technique is Gauss-Seidel's modified by omega.

		Notes
		-----
		gauss_seidel():
			[x]_(k) = ( (D - L)^(-1) * U ) * [x]_(k - 1) + ( (D - L)^(-1) )*[b]

		successive_relaxation():
			[x]_(k) = ( (D - wL)^(-1) * ((1 - w)*D + w*U) ) * [x]_(k - 1) + w*( (D - w*L)^(-1) )*[b]

		omega will be analyzed independent of assigned value which will be used if not specified in assignment.
		"""
		if omega == None:
			try: w = self.user_omega
			except AttributeError:
				try: w = self.best_omega
				except AttributeError:
					# w = super().find_omega(A, x0)
					w = self.find_omega()
					print(f"Warning! Omega was not given; therefore, I attempted to choose one, {w}.")
				else: print(f"Warning! Using `self.best_omega` = {w}.")
			else: print(f"Warning! Using `self.user_omega` = {w}.")
			if w <= 0: raise ValueError("Either a positive omega was not given, or I could not choose one.")
		elif omega != None and isinstance(omega, (int, float)):
			# omega = find_omega(A, x0, w)
			w = self.find_omega(omega=omega)
			print(f"Warning! omega = {omega} given. Which is not optimum: {w}")
			w = omega
		else: raise ValueError(f"ERROR! Either a positive omega was not given, or I could not choose one.")
		A, x0, b, tol, N = self.A, self.x0, self.b, self.tol, self.max_iter
		norm_type, norm = self.norm_type, tol*10
		k, n, approximations, errors = 0, len(x0), [x0], [norm]
		while norm > tol and k <= N:
			i, xi = 0, np.zeros_like(x0)
			# xgs = super().gauss_seidel(x0)
			xgs = self.gauss_seidel()["Approximations"].values[-1]
			while i < n:
				xi[i] = (1 - w)*x0[i] + w*xgs[i]
				i += 1
			if norm_type == "l_infinity":
				norm = norms(xi, x0).l_infinity()
			elif norm_type == "l_two":
				norm = norms(xi, x0).l_two()
			approximations.append(xi)
			errors.append(norm)
			x0 = xi
			k += 1
		if k <= N: print("Congratulations! Solution found!")
		else: print("Warning! Solution could not be found with initial guess or tolerance.")
		# m, n = len(approximations[0]), len(approximations)
		# X_matrix, j = np.zeros((m,n)), 0
		# while j < n:
		# 	i = 0
		# 	while i < m:
		# 		X_matrix[i][j] = float(approximations[j][i])
		# 		i += 1
		# 	j += 1
		self.iterations = np.array(range(k))
		self.approximations = np.array(approximations)
		self.errors = np.array(errors)
		return pd.DataFrame(data={"Iterations": self.iterations, "Approximations": self.approximations, "Error": self.errors})
# --------------------

# --------------------
# interpolations
class cubic_spline:
	def __init__(self, domain, function):
		self.domain, self.function = domain, function

	def clamped(self, variable=sp.Symbol("x"), fp=0):
		"""Given a domain and range, construct a spline polynomial within interval by some condition.

		Parameters
		----------
		X : array
			Input domain.

		f : array or expression
			Desired/Found range of interest.

		x : symbol
			Respected variable in derivative of equation. Assumed to be `'x'` if not stated.

		fp : array or expression
			Derivative at each point in `f`.

		Returns
		-------
		Y : array
			Finally evaluated solutions.

		splines_j : list
			Aggregate of splines on each interval.

		spline : string
			Totally constructed spline polynomial.

		Raises
		------
		bad_X : string
			If {`X`} is neither n x 1 nor 1 x n array.

		bad_f : string
			If `f` is not an expression or function and is not an n x 1 or 1 x n array.

		bad_data : string
			If {`X`} and {`f`} are of unequal length.
		
		bad_fp : string
			If `fp` is not an expression or function and is not an n x 1 or 1 x n array.

		missing_fp : string
			Output message that derivative data or expression is missing.

		See Also
		--------
		make_array() : Translates input expression to array from given `X`.

		endpoint() : Relies on another technique to find derivatives at endpoints if not explicitly provided by data, `fp` nor an expression.

		midpoint() : Finds the derivatives at points within the bounds of the endpoints.

		diagonality() : Determines whether input matrix is strictly, diagonally dominant.

		Notes
		-----
		`fp` will be calculated if not specified.

		Method uses many, low-ordered polynomials to fit larger data sets. This minimizes computational load, which conversely greatly increases for larger data sets that yield high-ordered polynomials.

		General form: 
		Sj(x) = aj + bj(x - xj) + cj(x - xj)^2 + dj(x - xj)^3

		Clamped splines fit the constructed polynomial to the given data and its der
		ivatives at either endpoint.

		If selected `condition` is `'natural'`, then `fp = 0`, because derivative is assumed to be straight line outside of data set.

		Definitions of cubic spline conditions:
		a) S(x) is a cubic polynomial, Sj(x) on sub-interval [x_(j), x_(j + 1)] for each j = 0, 1, ..., n - 1;

		b) Sj(x_(j)) = f(x_(j)) and Sj(x_(j + 1)) = f(x_(j + 1)) for each j = 0, 1, ..., n - 1;

		c) S_(j + 1)(x_(j + 1)) = Sj(x_(j + 1)) for each j = 0, 1, ..., n - 2;

		d) S_(j + 1)'(x_(j + 1)) = Sj'(x_(j + 1)) for each j = 0, 1, ..., n - 2;

		e) One of the following conditions is satisfied:
			1) S''(x0) = S''(xn) = 0				->  `'natural'`
			
			2) S'(x0) = f'(x0) and S'(xn) = f'(xn)  ->  `'clamped'`
		"""
		def algorithm(g, gp):
			Y, YP = np.array(g), np.array(gp)
			# STEP 1:   build list, h_i
			i, H = 0, np.zeros(n)
			while i < n:
				H[i] = X[i+1] - X[i]
				i += 1
			# STEP 2:   define alpha list endpoints
			A, AP, ALPHA = Y, YP, np.zeros(m)
			ALPHA[0] = 3*(A[1] - A[0])/H[0] - 3*AP[0]
			ALPHA[n] = 3*AP[n] - 3*(A[n] - A[n-1])/H[n-1]
			# STEP 3:   build list, alpha_i
			i = 1
			while i <= n-1:
				ALPHA[i] = 3/H[i]*(A[i+1] - A[i]) - 3/H[i-1]*(A[i] - A[i-1])
				i += 1
			# Algorithm 6.7 to solve tridiagonal
			# STEP 4:   define l, mu, and z first points
			L, MU, Z, C = np.zeros(m), np.zeros(m), np.zeros(m), np.zeros(m)
			L[0], MU[0] = 2*H[0], 0.5
			Z[0] = ALPHA[0]/L[0]
			# STEP 5:   build lists l, mu, and z
			i = 1
			while i <= n-1:
				L[i] = 2*(X[i+1] - X[i-1]) - H[i-1]*MU[i-1]
				MU[i] = H[i]/L[i]
				Z[i] = (ALPHA[i] - H[i-1]*Z[i-1])/L[i]
				i += 1
			# STEP 6:   define l, z, and c endpoints
			L[n] = H[n-1]*(2-MU[i-1])
			Z[n] = (ALPHA[n] - H[n-1]*Z[n-1])/L[n]
			C[n] = Z[n]
			# STEP 7:   build lists c, b, and d
			i, j, B, D = 1, 0, np.zeros(n), np.zeros(n)
			while i <= n:
				j = n-i
				C[j] = Z[j] - MU[j]*C[j+1]
				B[j] = (A[j+1] - A[j])/H[j] - H[j]*(C[j+1] + 2*C[j])/3
				D[j] = (C[j+1] - C[j])/(3*H[j])
				i += 1
			return Y, A, B, C, D
		sym_X, sym_function, sym_fp = "self.X", "self.f", "fp"
		bad_X = "Input domain, " + sym_X + " was neither an n x 1 nor a 1 x n array."
		bad_f = "Input range, " + sym_function + " was neither function nor expression and not an n x 1 or 1 x n array."
		bad_data = "Arrays " + sym_X + " and " + sym_function + " must be of equal length."
		bad_fp = "Derivative range was neither function nor expression and not an n x 1 or 1 x n array."
		bad_fp_data = "Arrays " + sym_X + ", " + sym_function + ", and " + sym_fp + " must be of equal length."
		missing_fp = "Missing derivative data or expression."
		f, X = self.function, self.domain
		if np.sum(X.shape) > np.sum(X.shape[0]): raise ValueError("ERROR! " + bad_X)
		if not isinstance(f, (FunctionType, sp.Expr)):
			if np.sum(f.shape) > np.sum(f.shape[0]): raise ValueError("ERROR! " + bad_f)
			elif len(X) != len(f): raise ValueError(bad_data)
			else: g = f
		elif isinstance(f, (FunctionType, sp.Expr)):
			g = make_array(X, f)
		if np.sum(fp.shape) != 0:
			if not isinstance(fp, (FunctionType, sp.Expr)):
				if np.sum(fp.shape) > np.sum(fp.shape[0]): raise ValueError("ERROR! " + bad_fp)
				elif len(X) != len(fp): raise ValueError("ERROR! " + bad_fp_data)
				else: gp = fp
			elif isinstance(fp, (FunctionType, sp.Expr)): gp = make_array(X, fp)
		elif fp == 0:
			if isinstance(f,(FunctionType, sp.Expr)):
				sym_function = sp.N(sp.sympify(f(variable)))
				f = sp.lambdify(variable, sym_function)
				fp = sp.diff(sym_function)
				gp = make_array(X, fp)
			elif not isinstance(f,(FunctionType, sp.Expr)):
				gp = []
				if len(X) > 2:
					gp.append(endpoint(X, f, X[1]-X[0], "three", "left"))
					i, n = 1, len(f) - 1
					while i < n: 
						gp.append(midpoint(X, f, X[i]-X[i-1], "three", i))
						i += 1
					gp.append(endpoint(X, f, X[-2]-X[-1], "three", "right"))
				elif len(X) > 5:
					gp.append(endpoint(X, f, X[1]-X[0], "five", "left"))
					i, n = 1, len(X) - 1
					while i < n: 
						gp.append(midpoint(X, f, X[i]-X[i-1], "five", i))
						i += 1
					gp.append(endpoint(X, f, X[-2]-X[-1], "five", "right"))
			else: raise ValueError("ERROR! " + missing_fp)
		m = len(X)
		n = m - 1
		Y, A, B, C, D = algorithm(g, gp)
		j, splines_j = 0, []
		while j <= n-1:
			xj, aj, bj, cj, dj = X[j], A[j], B[j], C[j], D[j]
			sj = aj + bj*(variable - xj) + cj*(variable - xj)**2 + dj*(variable - xj)**3
			splines_j.append(sj)
			j += 1
		spline = sp.simplify(sum(splines_j))
		return Y, splines_j, spline

	def natural(self, variable=sp.Symbol("x")):
		"""Given a domain and range, construct a spline polynomial within interval by some condition.

		Parameters
		----------
		X : array
			Input domain.

		f : array or expression
			Desired/Found range of interest.

		Returns
		-------
		Y : array
			Finally evaluated solutions.

		splines_j : list
			Aggregate of splines on each interval.

		spline : string
			Totally constructed spline polynomial.

		Raises
		------
		bad_X : string
			If {`X`} is neither n x 1 nor 1 x n array.

		bad_f : string
			If `f` is not an expression or function and is not an n x 1 or 1 x n array.

		bad_data : string
			If {`X`} and {`f`} are of unequal length.

		See Also
		--------
		make_array() : Translates input expression to array from given `X`.

		diagonality() : Determines whether input matrix is strictly, diagonally dominant.

		Notes
		-----
		Method uses many, low-ordered polynomials to fit larger data sets. This minimizes computational load, which conversely greatly increases for larger data sets that yield high-ordered polynomials.

		General form: 
		Sj(x) = aj + bj(x - xj) + cj(x - xj)^2 + dj(x - xj)^3

		Clamped splines fit the constructed polynomial to the given data and its der
		ivatives at either endpoint.

		If selected `condition` is `'natural'`, then `fp = 0`, because derivative is assumed to be straight line outside of data set.

		Definitions of cubic spline conditions:
		a) S(x) is a cubic polynomial, Sj(x) on sub-interval [x_(j), x_(j + 1)] for each j = 0, 1, ..., n - 1;

		b) Sj(x_(j)) = f(x_(j)) and Sj(x_(j + 1)) = f(x_(j + 1)) for each j = 0, 1, ..., n - 1;

		c) S_(j + 1)(x_(j + 1)) = Sj(x_(j + 1)) for each j = 0, 1, ..., n - 2;

		d) S_(j + 1)'(x_(j + 1)) = Sj'(x_(j + 1)) for each j = 0, 1, ..., n - 2;

		e) One of the following conditions is satisfied:
			1) S''(x0) = S''(xn) = 0				->  `'natural'`
			
			2) S'(x0) = f'(x0) and S'(xn) = f'(xn)  ->  `'clamped'`
		"""
		def algorithm(g):
			Y = g
			# STEP 1:   build list, h_i
			H, i = np.zeros(n), 0
			while i < n:
				H[i] = X[i+1] - X[i]
				i += 1
			# STEP 2:   build list, alpha_i
			A, ALPHA = Y, np.zeros(m)
			i = 1
			while i <= n-1:
				ALPHA[i] = 3/H[i]*(A[i+1] - A[i]) - 3/H[i-1]*(A[i] - A[i-1])
				i += 1
			# Algorithm 6.7 to solve tridiagonal
			# STEP 3:   define l, mu, and z first points
			L, MU, Z, C = np.zeros(m), np.zeros(m), np.zeros(m), np.zeros(m)
			L[0], MU[0], Z[0] = 1, 0, 0
			# STEP 4:   build lists l, mu, and z
			i = 1
			while i <= n-1:
				L[i] = 2*(X[i+1] - X[i-1]) - H[i-1]*MU[i-1]
				MU[i] = H[i]/L[i]
				Z[i] = (ALPHA[i] - H[i-1]*Z[i-1])/L[i]
				i += 1
			# STEP 5:   define l, z, and c endpoints
			L[n], Z[n], C[n] = 1, 0, 0
			# STEP 6:   build lists c, b, and d
			i, j, B, D = 1, 0, np.zeros(n), np.zeros(n)
			while i <= n:
				j = n-i
				C[j] = Z[j] - MU[j]*C[j+1]
				B[j] = (A[j+1] - A[j])/H[j] - H[j]*(C[j+1] + 2*C[j])/3
				D[j] = (C[j+1] - C[j])/(3*H[j])
				i += 1
			return Y, A, B, C, D
		sym_X, sym_function = "self.X", "self.f"
		bad_X = "Input domain, " + sym_X + " was neither an n x 1 nor a 1 x n array."
		bad_f = "Input range, " + sym_function + " was neither function nor expression and not an n x 1 or 1 x n array."
		bad_data = "Arrays " + sym_X + " and " + sym_function + " must be of equal length."
		X, f = np.array(self.domain), self.function
		if np.sum(X.shape) > np.sum(X.shape[0]): raise ValueError("ERROR! " + bad_X)
		if not isinstance(f, (FunctionType, sp.Expr)):
			f = np.array(f)
			if np.sum(f.shape) > np.sum(f.shape[0]): raise ValueError("ERROR! " + bad_f)
			elif len(X) != len(f): raise ValueError("ERROR! " + bad_data)
			else: g = f
		elif isinstance(f, (FunctionType, sp.Expr)):
			g = make_array(X, f)
		m = len(X)
		n = m - 1
		Y, A, B, C, D = algorithm(g)
		j, splines_j = 0, []
		while j <= n-1:
			xj, aj, bj, cj, dj = X[j], A[j], B[j], C[j], D[j]
			sj = aj + bj*(variable - xj) + cj*(variable - xj)**2 + dj*(variable - xj)**3
			splines_j.append(sj)
			j += 1
		spline = sp.simplify(sum(splines_j))
		return Y, splines_j, spline

def hermite(X, FX, x=sp.Symbol("x"), FP=0):
	"""Given a domain and range, construct a Hermetic polynomial.

	Parameters
	----------
	X : array
		Input domain.

	FX : array
		Desired/Found range of interest.

	x : symbol
		Respected variable in derivative of equation. Assumed to be `'x'` if not stated.

	FP : array or expression
		Derivative at each point in `FX`.

	Returns
	-------
	polynomial : expression
		Lambdified Hermetic polynomial.

	Raises
	------
	bad_X : string
		If {`X`} is neither n x 1 nor 1 x n array.

	bad_FX : string
		If {`FX`} is neither n x 1 nor 1 x n array.

	bad_data : string
		If {`X`} and {`FX`} are of unequal length.

	bad_FP : string
		If `FP` is not an expression or function and is not an n x 1 or 1 x n array.

	bad_FP_data : string
		If {`X`}, {`FX`}, or {`FP`} are of unequal lengths.

	missing_FP : string
		If `FP = 0` and `FX` is not an expression, then missing derivative data or expression.

	Warns
	-----
	made_poly : string
		Displays the string form of the equation.

	See Also
	--------
	make_array() : Prints string that expression was used to make array.

	Notes
	-----
	`FP` calculated if not specified.

	Slow computation time for larger data sets.

	Oscullating curve incorporates Taylor and Lagrangian polynomials to kiss the data and match each data point's derivatives. Which fits the curve to the shape of the data and its trend.
	"""
	sym_X, sym_FX, sym_FP = "X", "FX", "FP"
	bad_X = "Input domain, " + sym_X + " was neither an n x 1 nor a 1 x n array."
	bad_FX = "Input range, " + sym_FX + " was neither an n x 1 nor a 1 x n array."
	bad_data = "Arrays " + sym_X + " and " + sym_FX + " must be of equal length."
	bad_FP = "Derivative range was neither function nor expression and not an n x 1 or 1 x n array."
	bad_FP_data = "Arrays " + sym_X + ", " + sym_FX + ", and " + sym_FP + " must be of equal length."
	missing_FP = "Missing derivative data or expression."
	made_poly = "I have found your requested polynomial! P = "
	if np.sum(X.shape) > np.sum(X.shape[0]): raise ValueError("ERROR! " + bad_X)
	if not isinstance(FX, (FunctionType, sp.Expr)):
		if np.sum(FX.shape) > np.sum(FX.shape[0]): raise ValueError("ERROR! " + bad_FX)
		elif len(X) != len(FX): raise ValueError("ERROR! " + bad_data)
	elif isinstance(FX,(FunctionType, sp.Expr)): g = make_array(X, FX)
	if FP != 0:
		if not isinstance(FP, (FunctionType, sp.Expr)):
			if np.sum(FP.shape) > np.sum(FP.shape[0]): raise ValueError("ERROR! " + bad_FP)
			if len(X) != len(FP): raise ValueError("ERROR! " + bad_FP_data)
		elif isinstance(FP,(FunctionType, sp.Expr)): FP = make_array(X, FP)
	elif FP == 0:
		if isinstance(FX,(FunctionType, sp.Expr)):
			fp = sp.lambdify(x, sp.diff(FX(x)))
			gp = make_array(X, fp)
		else: print("Warning! " + missing_FP)
	n = len(X)
	i, Q, Z = 0, np.zeros((2*n+1,2*n+1)), np.zeros((2*n+1,1))
	while i < n:
		Z[2*i], Z[2*i + 1] = X[i], X[i]
		Q[2*i][0], Q[2*i + 1][0] = g[i], g[i]
		Q[2*i + 1][1] = gp[i]
		if i != 0: Q[2*i][1] = (Q[2*i][0] - Q[2*i - 1][0]) \
			/ (Z[2*i] - Z[2*i - 1])
		i += 1
	i = 2
	while i < 2*n + 1:
		j = 2
		while j <= i:
			Q[i][j] = (Q[i][j - 1] - Q[i - 1][j - 1]) \
			/ (Z[i] - Z[i - j])
			j += 1
		i += 1
	i, y, terms = 0, 1, []
	while i < n:
		j, xi = 2*i, (x - X[i])
		qjj, qj1 = Q[j][j], Q[j + 1][j + 1]
		terms.append(qjj*y)
		y = y*xi
		terms.append(qj1*y)
		y = y*xi
		i += 1
	polynomial = sp.lambdify(x, sp.simplify(sum(terms)))
	print("Congratulations! ", made_poly + str(polynomial(x)))
	return polynomial

def lagrange(X, Y, x=sp.Symbol("x")):
	"""Given a domain and range, construct a Lagrangian polynomial.

	Parameters
	----------
	X : array
		Input domain.

	Y : array or expression
		Desired/Found range of interest.

	x : symbol
		Respected variable in derivative of equation. Assumed to be `'x'` if not stated.

	Returns
	-------
	yn : list
		Aggregate of Lagrangian terms.

	sp.lambdify(x, polynomial) : expression
		Lambdified Lagrangian polynomial.

	bound : list
		Propogation of error through construction.

	sum(bound)
		Total error.

	Raises
	------
	bad_X : string
		If {`X`} is neither n x 1 nor 1 x n array.

	bad_Y : string
		If {`Y`} is neither n x 1 nor 1 x n array.

	bad_data : string
		If {`X`} and {`Y`} are of unequal length.

	Warns
	-----
	made_poly : string
		Displays the string form of the equation.

	See Also
	--------
	make_array() : Prints string that expression was used to make array.

	Notes
	--------
	Polynomial will quickly begin to oscillate for larger data sets.

	Finds a polynomial of degree n-1.

	Polynomial is of the following form:
	P(x) = f(x0)L_(n,0)(x) + ... + f(xn)L_(n,n)(x), where

	L_(n,k) = prod_(i=0, i!=k)^(n) (x - xi)/(xk - xi)

	Examples
	--------
	A Lagrange polynomial between (2,4) and (5,1) would be found as follows:
	L_(0)(x) = (x - 5)/(2 - 5) = -(x - 5)/3

	L_(1)(x) = (x - 2)/(5 - 2) = (x - 2)/3

	=>  P(x)	= (4)*(-(x - 5)/3) + (1)*((x - 2)/3)
				= -x + 6
	"""
	def term(xk, yk, x):
		num, den, L_k = [], [], []
		for xl in X:
			if xl != xk:
				num.append(x-xl)
				den.append(xk-xl)
		L_k = (np.divide(np.prod(num), np.prod(den)))
		return L_k * yk
	def error(n, xi, x):
		i, roots, g, xi_error = 0, [], [], []
		while i <= n:
			root = X[i]
			roots.append(x - root)
			g = np.prod(roots)
			k = 0
			while k <= n:
				xi = sp.simplify(sp.diff(xi))
				k += 1
			dxi = np.abs(xi.evalf(subs={x: root})/(math.factorial(k)))
			xi_error.append(np.abs(dxi))
			xi_err = np.max(xi_error)
			g_prime = sp.diff(g)
			r = sp.solve(g_prime)
			if i == 0:
				r = g_prime
				gx = g.evalf(subs={x: r})
			elif i == 1:
				gx = g.evalf(subs={x: r[0]})
			else:
				R = []
				for s in r:
					if not isinstance(s, complex):
						R.append(g.evalf(subs={x: s}))
				gx = np.amax(np.abs(R))
			i += 1
		return np.abs(xi_err*gx)
	sym_X, sym_Y = "X", "Y"
	bad_X = "Input domain, " + sym_X + " was neither an n x 1 nor a 1 x n array."
	bad_Y = "Input range, " + sym_Y + " was neither an n x 1 nor a 1 x n array."
	bad_data = "Arrays " + sym_X + " and " + sym_Y + " must be of equal length."
	made_poly = "I have found your requested polynomial! P = "
	if np.sum(X.shape) > np.sum(X.shape[0]): raise ValueError("ERROR! " + bad_X)
	if not isinstance(Y,(FunctionType, sp.Expr)):
		if np.sum(Y.shape) > np.sum(Y.shape[0]): raise ValueError("ERROR! " + bad_Y)
		elif len(X) != len(Y): raise ValueError("ERROR! " + bad_data)
	elif isinstance(Y,(FunctionType, sp.Expr)): Y = make_array(X, Y)
	k, yn, bound = 0, [], []
	for xk in X:
		yn.append(term(xk, Y[k], x))
		bound.append(error(k, sp.simplify(sum(yn)), x))
		k += 1
	polynomial = sp.simplify(sum(yn))
	print("Congratulations! ", made_poly, str(polynomial))
	return yn, sp.lambdify(x, polynomial), bound, sum(bound)

class least_squares:
	def linear(X_i, Y_i, n, variable=sp.Symbol("x")):
		"""Given a domain and range, construct some polynomial.

		Parameters
		----------
		X_i : array
			Input domain.

		Y_i : array or expression
			Desired/Found range of interest.

		n : int
			Degree of polynomial.

		Returns
		-------
		P : expression
			Lambdified linear least square polynomial.

		E : float
			Total error.

		Raises
		------
		bad_X : string
			If {`X_i`} is neither n x 1 nor 1 x n array.

		bad_Y : string
			If {`Y_i`} is neither n x 1 nor 1 x n array.

		bad_data : string
			If {`X_i`} and {`Y_i`} are of unequal length.

		bad_n : string
			If prescribed `n` is not an integer or is zero.

		Warns
		-----
		made_poly : string
			Displays the string form of the equation.
		"""
		def poly(X):
			terms, k = [], 0
			for x in X:
				terms.append(x*(variable**k))
				k += 1
			p = sp.simplify(sum(terms))
			err, i = 0, 0
			for x_i in X_i:
				px = p.subs(variable, x_i)
				err += (Y_i[i] - px)**2
				i += 1
			return p, err
		sym_X_i, sym_Y_i = "X_i", "Y_i"
		bad_X = "Input domain, " + sym_X_i + " was neither an n x 1 nor a 1 x n array."
		bad_Y = "Input range, " + sym_Y_i + " was neither an n x 1 nor a 1 x n array."
		bad_data = "Arrays " + sym_X_i + " and " + sym_Y_i + " must be of equal length."
		bad_n = "Degree of polynomial must be integer and non-zero."
		made_poly = "I have found your requested polynomial! P = "
		if np.sum(X_i.shape) > np.sum(X_i.shape[0]): raise ValueError("ERROR! " + bad_X)
		if isinstance(Y_i, (FunctionType, sp.Expr)):
			Y_i = make_array(X_i, Y_i)
		if np.sum(Y_i.shape) > np.sum(Y_i.shape[0]): raise ValueError("ERROR! " + bad_Y)
		if len(X_i) != len(Y_i): raise ValueError("ERROR! " + bad_data)
		if not isinstance(n,(int)) or n == 0: raise ValueError("ERROR! " + bad_n)
		m = len(X_i)
		A, x = np.zeros((n+1, n+1)), np.zeros((n+1,1))
		i, b = 0, np.zeros_like(x)
		while i <= n:
			j = 0
			while j <= n:
				a_ij, k = 0, 0
				while k < m:
					a_ij += (X_i[k])**(i + j)
					k += 1
				A[i][j] = a_ij
				j += 1
			b_i, k = 0, 0
			while k < m:
				b_i += Y_i[k]*(X_i[k]**(i))
				k += 1
			b[i] = b_i
			i += 1
		x = np.transpose(np.linalg.solve(A, b))
		k, X, terms = 0, x[0], []
		for x in X:
			terms.append(x*(variable**k))
			k += 1
		polynomial = sp.simplify(sum(terms))
		print("Congratulations! ", made_poly, str(polynomial))
		P = sp.lambdify(variable, polynomial)
		i, E = 0, 0
		for x_i in X_i:
			E += (Y_i[i] - P(x_i))**2
			i += 1
		return P, E

	def power(X, Y):
		"""Given a domain and range, yield the coefficients for an equation of the form `y = A*(x^B)`.

		Parameters
		----------
		X : array
			Input domain.

		Y : array or expression
			Desired/Found range of interest.

		Returns
		-------
		A : float
			Leading coefficient.

		B : float
			Exponent.

		Raises
		------
		bad_X : string
			If {`X`} is neither n x 1 nor 1 x n array.

		bad_Y : string
			If {`Y`} is neither n x 1 nor 1 x n array.

		bad_data : string
			If {`X`} and {`Y`} are of unequal length.

		Warns
		-----
		made_poly : string
			Displays the string form of the equation.
		"""
		sym_X, sym_Y = "X", "Y"
		bad_X = "Input domain, " + sym_X + " was neither an n x 1 nor a 1 x n array."
		bad_Y = "Input range, " + sym_Y + " was neither an n x 1 nor a 1 x n array."
		bad_data = "Arrays " + sym_X + " and " + sym_Y + " must be of equal length."
		bad_n = "Degree of polynomial must be integer and non-zero."
		made_poly = "I have found your requested polynomial! P = "
		X, Y = np.array(X), np.array(Y)
		if np.sum(X.shape) > np.sum(X.shape[0]): raise ValueError("ERROR! " + bad_X)
		if isinstance(Y, (FunctionType, sp.Expr)):
			Y = make_array(X, Y)
		if np.sum(Y.shape) > np.sum(Y.shape[0]): raise ValueError("ERROR! " + bad_Y)
		if len(X) != len(Y): raise ValueError("ERROR! " + bad_data)
		n = len(X)
		q1, q2, q3, q4 = [], [], [], []
		for i in range(n):
			xi, yi = X[i], Y[i]
			q1.append(np.log(xi)*np.log(yi))
			q2.append(np.log(xi))
			q3.append(np.log(yi))
			q4.append(np.log(xi)**2)
		num = n*np.sum(q1) - np.sum(q2)*np.sum(q3)
		den = n*np.sum(q4) - (np.sum(q2))**2
		b = num/den
		a = math.exp((np.sum(q3) - b*np.sum(q2))/n)
		return a, b

def linear_interpolation(x0, y0, x1, y1, x):
	return y0 + (x - x0)*(y1 - y0)/(x1 - x0)

def newton_difference(X, FX, x0, variable=sp.Symbol("x"), direction=0):
	"""Given a domain and range, construct some polynomial by Newton's Divided Difference.

	Parameters
	----------
	X : array
		Input domain.

	FX : array or expression
		Desired/Found range of interest.

	x0 : float
		Point about which polynomial is evaluated.

	direction : string
		`'forward'` or `'backward'` construction. Will be chosen automatically if not specified.

	Returns
	-------
	p : expression
		Lambdified constructed polynomial.

	p(x0) : float
		Evaluation of `p` at `x`.

	Raises
	------
	bad_X : string
		If {`X_i`} is neither n x 1 nor 1 x n array.

	bad_FX : string
		If {`FX`} is neither n x 1 nor 1 x n array.

	bad_data : string
		If {`X`} and {`FX`} are of unequal length.

	bad_direction : string
		If `direction` is neither `'forward'` nor `'backward'`.

	Warns
	-----
	made_poly : string
		Displays the string form of the equation.

	See Also
	--------
	make_array() : Prints string that expression was used to make array.

	Notes
	-----
	Direction will be chosen if not specified.

	Polynomials best made with even spacing in `X`; although, this is not completely necessary.
	"""
	def fterm(i, j):
		fij = (fxn[i][j] - fxn[i-1][j])/(fxn[i][0] - fxn[i-j][0])
		return fij
	sym_X, sym_FX = "X", "FX"
	bad_X = "Input domain, " + sym_X + " was neither an n x 1 nor a 1 x n array."
	bad_FX = "Input range, " + sym_FX + " was neither an n x 1 nor a 1 x n array."
	bad_data = "Arrays " + sym_X + " and " + sym_FX + " must be of equal length."
	bad_direction = "Supplied direction was not understood. Please specify 'forward' or 'backward', or let me choose."
	made_poly = "I have found your requested polynomial! P = "
	X, x0 = np.array(X), float(x0)
	if not isinstance(FX,(FunctionType, sp.Expr)):
		FX = np.array(FX)
		if np.sum(X.shape) > np.sum(X.shape[0]): raise ValueError("ERROR! " + bad_X)
		if np.sum(FX.shape) > np.sum(FX.shape[0]): raise ValueError("ERROR! " + bad_FX)
		if len(X) != len(FX): raise ValueError("ERROR! " + bad_data)
	if isinstance(FX,(FunctionType, sp.Expr)): FX = make_array(X, FX)
	if direction == 0:
		if x0 <= np.median(X): direction = "forward"
		else: direction = "backward"
	elif direction != "forward" and direction != "backward": raise ValueError(bad_direction)
	m = len(X)
	n = m + 1
	fxn, coeff, term, poly = np.zeros((m,n)), [], [], []
	m, n = m - 1, n - 1	 # change m and n from length to index
	j, fxn[:,0], fxn[:,1] = 1, X, FX
	while j < m:
		i = 1
		while i < m:
			fk = fterm(i, j)
			fxn[i][j+1] = fk
			if direction == "forward" and i == j:
				coeff.append(fk)
			if direction == "backward" and i == m - 1:
				coeff.append(fk)
			i += 1
		j += 1
	for c in coeff:
		k = coeff.index(c)
		term.append(variable - X[k])
		poly.append(c*np.prod(term))
	if direction == "forward": polynomial = sp.simplify(sum(poly) + FX[0])
	if direction == "backward": polynomial = sp.simplify(sum(poly) + FX[m])
	print("Congratulations! ", made_poly, str(polynomial))
	p = sp.lambdify(variable, polynomial)
	return p, p(x0)
# --------------------

# --------------------
# numerical differentiation and integration
class simpson:

	def open(f, X, h=0, a=0, b=0, variable=sp.Symbol("x")):
		"""Find the integral of a function within some interval, using Simpson's Rule.

		Parameters
		----------
		f : expression
			Polynomial equation that defines graphical curve.

		X : list
			Domain over which `f` is evaluated.

		h : float
			Step-size through interval.

		a : float
			Left-hand bound of interval.

		b : float
			Right-hand bound of interval.

		Returns
		-------
		XJ : list
			Values of domain at which `f` was analyzed.

		YJ : list
			Evaluations of `f` from domain.

		F : float
			Total area under curve, `f`.

		Raises
		------
		bad_X : string
			If {`X_i`} is neither n x 1 nor 1 x n array.

		bad_f : string
			If {`f`} is not an expression.

		Warns
		-----
		__func_func : string
			Evaluate input expression for Newton difference approximation.

		Notes
		-----
		`X = 0` if not a list nor n x 1 or 1 x n array.

		Unless specified and if `X` is defined, `a` and `b` will be the minimum and maximum, respectively, of `X`.

		Theorem:
		Let f be in C4[a,b], n be even, h = (b-a)/n, and xj = a + jh for j = 0, 1, ..., n. There exists a mu in (a,b) for which the quadrature for n sub-intervals can be written with its error term as:
		int_(a)^(b)f(x)dx = h[f(a) + 2*[sum_(j=1)^(n/2 - 1){f(x_(2j))}] + 4*[sum_(j=1)^(n/2){f(x_(2j-1))}] + f(b)]/3 - (b-a)*(h^4)f''''(mu)/180.

		Where: (b-a)*(h^4)f''''(mu)/180 -> O(h^4)
		"""
		X = np.array(X)
		sym_X, sym_function = "X", "f"
		bad_X = "Input domain, " + sym_X + " was neither an n x 1 nor a 1 x n array."
		bad_f = "Input range, " + sym_function + " must be expression, not list or tuple."
		if np.sum(X.shape) > np.sum(X.shape[0]): raise ValueError("ERROR! " + bad_X)
		if not isinstance(f,(FunctionType, sp.Expr)):
			if np.sum(f.shape) > np.sum(f.shape[0]): raise ValueError("ERROR! " + bad_X)
			else: raise ValueError("ERROR! " + bad_f)
		if isinstance(f,(FunctionType, sp.Expr)):
			sym_function = sp.N(sp.sympify(f(variable)))
			f = sp.lambdify(variable, sym_function)
			print(f"Information: Input expression, {sym_function} used.")
		if h == 0: h = X[1]-X[0]
		if a == 0: a = min(X)
		if b == 0: b = max(X)
		h, a, b = float(h), float(a), float(b)
		n = math.ceil((b-a)/h)
		XJ1, XJ2, XJ, = [], [], []
		YJ1, YJ2, YJ, = [], [], []
		XJ.append(a); YJ.append(f(a))
		j, z1 = 1, 0
		while j <= (n/2)-1:
			xj = a + 2*j*h
			yj = f(xj)
			XJ1.append(xj); YJ1.append(yj)
			z1 += yj
			j += 1
		k, z2 = 1, 0
		while k <= n/2:
			xj = a + (2*k - 1)*h
			yj = f(xj)
			XJ2.append(xj); YJ2.append(yj)
			z2 += yj
			k += 1
		l = 0
		while l < np.array(XJ1).shape[0]:
			XJ.append(XJ2[l]); YJ.append(YJ2[l])
			XJ.append(XJ1[l]); YJ.append(YJ1[l])
			l += 1
		XJ.append(XJ2[l]); YJ.append(YJ2[l])
		XJ.append(b); YJ.append(f(b))
		F = h/3*(f(a) + 2*z1 + 4*z2 + f(b))
		return XJ, YJ, F

	def closed(f, X, h=0, a=0, b=0, variable=sp.Symbol("x")):
		"""Find the integral of a function within some interval, using Simpson's Rule.

		Parameters
		----------
		f : expression
			Polynomial equation that defines graphical curve.

		X : list
			Domain over which `f` is evaluated.

		h : float
			Step-size through interval.

		a : float
			Left-hand bound of interval.

		b : float
			Right-hand bound of interval.

		Returns
		-------
		XJ : list
			Values of domain at which `f` was analyzed.

		YJ : list
			Evaluations of `f` from domain.

		F : float
			Total area under curve, `f`.

		Raises
		------
		bad_X : string
			If {`X_i`} is neither n x 1 nor 1 x n array.

		bad_f : string
			If {`f`} is not an expression.

		Warns
		-----
		__func_func : string
			Evaluate input expression for Newton difference approximation.

		Notes
		-----
		`X = 0` if not a list nor n x 1 or 1 x n array.

		Unless specified and if `X` is defined, `a` and `b` will be the minimum and maximum, respectively, of `X`.

		Theorem:
		Let f be in C4[a,b], n be even, h = (b-a)/n, and xj = a + jh for j = 0, 1, ..., n. There exists a mu in (a,b) for which the quadrature for n sub-intervals can be written with its error term as:
		int_(a)^(b)f(x)dx = h[f(a) + 2*[sum_(j=1)^(n/2 - 1){f(x_(2j))}] + 4*[sum_(j=1)^(n/2){f(x_(2j-1))}] + f(b)]/3 - (b-a)*(h^4)f''''(mu)/180.

		Where: (b-a)*(h^4)f''''(mu)/180 -> O(h^4)
		"""
		X = np.array(X)
		sym_X, sym_function = "X", "f"
		bad_X = "Input domain, " + sym_X + " was neither an n x 1 nor a 1 x n array."
		other_bad_X = "Input domain, " + sym_X + " must be only 4 elements!"
		bad_f = "Input range, " + sym_function + " must be expression, not list or tuple."
		if np.sum(X.shape) > np.sum(X.shape[0]): raise ValueError("ERROR! " + bad_X)
		if np.sum(X.shape[0]) != 4: raise ValueError("ERROR! " + other_bad_X)
		if not isinstance(f,(FunctionType, sp.Expr)):
			f = np.array(f)
			if np.sum(f.shape) == np.sum(f.shape[0]) and np.sum(f.shape) == 4: Y = np.array(f)
			elif np.sum(f.shape) > np.sum(f.shape[0]): raise ValueError("ERROR! " + bad_X)
			else: raise ValueError("ERROR! " + bad_f)
		if h == 0: h = X[1]-X[0]
		if a == 0: a = min(X)
		if b == 0: b = max(X)
		if isinstance(f,(FunctionType, sp.Expr)): 
			sym_function = sp.N(sp.sympify(f(variable)))
			f = sp.lambdify(variable, sym_function)
			print(f"Information: Input expression, {sym_function} used.")
			Y = make_array(X, f)
			if a < np.min(X): Y[0] = f(a)
			if b > np.max(X): Y[3] = f(b)
		h, a, b = float(h), float(a), float(b)
		F = 3*h/8*(Y[0] + 3*(Y[1] + Y[2]) + Y[3])
		return X, Y, F

class trapezoidal:

	def open(f, X, h=0, a=0, b=0, variable=sp.Symbol("x")):
		"""Find the integral of a function within some interval, using Trapezoidal Rule.

		Parameters
		----------
		f : expression
			Polynomial equation that defines graphical curve.

		X : list
			Domain over which `f` is evaluated.

		h : float
			Step-size through interval.

		a : float
			Left-hand bound of interval.

		b : float
			Right-hand bound of interval.

		Returns
		-------
		XJ : list
			Values of domain at which `f` was analyzed.

		YJ : list
			Evaluations of `f` from domain.

		F : float
			Total area under curve, `f`.

		Raises
		------
		bad_X : string
			If {`X_i`} is neither n x 1 nor 1 x n array.

		bad_f : string
			If {`f`} is not an expression.

		Warns
		-----
		__func_func : string
			Evaluate input expression for Newton difference approximation.

		Notes
		-----
		`X = 0` if not a list nor n x 1 or 1 x n array.

		Unless specified and if `X` is defined, `a` and `b` will be the minimum and maximum, respectively, of `X`.

		Theorem:
		Let f be in C2[a,b], h = (b-a)/n, and xj = a + jh for j = 0, 1, ..., n. There exists a mu in (a,b) for which the quadrature for n sub-intervals can be written with its error term as:
		int_(a)^(b)f(x)dx = h[f(a) + 2*[sum_(j=1)^(n - 1){f(xj)}] + f(b)]/2 - (b-a)*(h^2)f''(mu)/12.

		Where: (b-a)*(h^2)f''(mu)/12 -> O(h^2)
		"""
		X = np.array(X)
		sym_X, sym_function = "X", "f"
		bad_X = "Input domain, " + sym_X + " was neither an n x 1 nor a 1 x n array."
		bad_f = "Input range, " + sym_function + " must be expression, not list or tuple."
		if np.sum(X.shape) > np.sum(X.shape[0]): raise ValueError("ERROR! " + bad_X)
		if not isinstance(f,(FunctionType, sp.Expr)):
			if np.sum(X.shape) > np.sum(X.shape[0]): raise ValueError("ERROR! " + bad_X)
			else: raise ValueError("ERROR! " + bad_f)
		if isinstance(f,(FunctionType, sp.Expr)):
			sym_function = sp.N(sp.sympify(f(variable)))
			f = sp.lambdify(variable, sym_function)
			print(f"Information: Input expression, {sym_function} used.")
		if h == 0: h = X[1]-X[0]
		if a == 0: a = min(X)
		if b == 0: b = max(X)
		h, a, b = float(h), float(a), float(b)
		XJ, YJ = [], []
		XJ.append(a); YJ.append(f(a))
		j, n, z = 1, math.ceil((b-a)/h), 0
		while j <= n-1:
			x_j = a + j*h
			XJ.append(x_j)
			y_j = f(x_j)
			YJ.append(y_j)
			z += y_j
			j += 1
		XJ.append(b); YJ.append(f(b))
		F = h/2*(f(a) + 2*z + f(b))
		return XJ, YJ, F

	def closed(f, X, h=0, a=0, b=0, variable=sp.Symbol("x")):
		"""Find the integral of a function within some interval, using Trapezoidal Rule.

		Parameters
		----------
		f : expression
			Polynomial equation that defines graphical curve.

		X : list
			Domain over which `f` is evaluated.

		h : float
			Step-size through interval.

		a : float
			Left-hand bound of interval.

		b : float
			Right-hand bound of interval.

		Returns
		-------
		XJ : list
			Values of domain at which `f` was analyzed.

		YJ : list
			Evaluations of `f` from domain.

		F : float
			Total area under curve, `f`.

		Raises
		------
		bad_X : string
			If {`X_i`} is neither n x 1 nor 1 x n array.

		bad_f : string
			If {`f`} is not an expression.

		Warns
		-----
		__func_func : string
			Evaluate input expression for Newton difference approximation.

		Notes
		-----
		`X = 0` if not a list nor n x 1 or 1 x n array.

		Unless specified and if `X` is defined, `a` and `b` will be the minimum and maximum, respectively, of `X`.

		Theorem:
		Let f be in C2[a,b], h = (b-a)/n, and xj = a + jh for j = 0, 1, ..., n. There exists a mu in (a,b) for which the quadrature for n sub-intervals can be written with its error term as:
		int_(a)^(b)f(x)dx = h[f(a) + 2*[sum_(j=1)^(n - 1){f(xj)}] + f(b)]/2 - (b-a)*(h^2)f''(mu)/12.

		Where: (b-a)*(h^2)f''(mu)/12 -> O(h^2)
		"""
		X = np.array(X)
		sym_X, sym_function = "X", "f"
		bad_X = "Input domain, " + sym_X + " was neither an n x 1 nor a 1 x n array."
		other_bad_X = "Input domain, " + sym_X + " must be only 2 elements!"
		bad_f = "Input range, " + sym_function + " must be expression, not list or tuple."
		if np.sum(X.shape) > np.sum(X.shape[0]): raise ValueError("ERROR! " + bad_X)
		if np.sum(X.shape[0]) != 2: raise ValueError("ERROR! " + other_bad_X)
		if not isinstance(f,(FunctionType, sp.Expr)):
			f = np.array(f)
			if np.sum(f.shape) == np.sum(f.shape[0]) and np.sum(f.shape) == 2: Y = np.array(f)
			elif np.sum(X.shape) > np.sum(X.shape[0]): raise ValueError("ERROR! " + bad_X)
			else: raise ValueError("ERROR! " + bad_f)
		if h == 0: h = X[1]-X[0]
		if a == 0: a = min(X)
		if b == 0: b = max(X)
		if isinstance(f,(FunctionType, sp.Expr)): 
			sym_function = sp.N(sp.sympify(f(variable)))
			f = sp.lambdify(variable, sym_function)
			print(f"Information: Input expression, {sym_function} used.")
			Y = make_array(X, f)
			if a < np.min(X): Y[0] = f(a)
			if b > np.max(X): Y[1] = f(b)
		h, a, b = float(h), float(a), float(b)
		F = h/2*(Y[0] + Y[1])
		return X, Y, F

def endpoint(X, Y, h, point_type, which_end):
	"""Find the derivative at an endpoint of data set.

	Parameters
	----------
	X : list
		Domain of collected data.

	Y : array or expression
		Range of collected data.

	h : float
		Step-size through interval.

	point_type : string
		Determines if 3 or 5 pt. method is used.

	which_end : string
		Dictates whether evaluated point is left or right most data point.

	Returns
	-------
	dY : float
		Evaluated derivative at point.

	Raises
	------
	bad_X : string
		If {`X`} is neither n x 1 nor 1 x n array.

	bad_Y : string
		If {`Y`} is not an expression.

	bad_data : string
		If `X` and `Y` are of unequal length.

	See Also
	--------
	make_array() : Prints string that expression was used to make array.

	Notes
	-----
	5 point is more accurate than 3 point; however, round-off error increases.
	"""
	sym_X, sym_Y = "X", "Y"
	bad_X = "Input domain, " + sym_X + " was neither an n x 1 nor a 1 x n array."
	bad_Y = "Input range, " + sym_Y + " was neither an n x 1 nor a 1 x n array."
	bad_data = "Arrays " + sym_X + " and " + sym_Y + " must be of equal length."
	if not isinstance(Y,(FunctionType, sp.Expr)):
		if np.sum(X.shape) > np.sum(X.shape[0]): raise ValueError("ERROR! " + bad_X)
		if np.sum(Y.shape) > np.sum(Y.shape[0]): raise ValueError("ERROR! " + bad_Y)
		if len(X) != len(Y): raise ValueError("ERROR! " + bad_data)
	if isinstance(Y,(FunctionType, sp.Expr)): Y = make_array(X, Y)
	h, dY = float(h), 0
	if which_end == "left":
		i = 0
		if point_type == "three":
			dY = (-3*Y[i] + 4*Y[i+1] - Y[i+2])/(2*h)
		if point_type == "five":
			dY = (-25*Y[i] + 48*Y[i+1] \
				- 36*Y[i+2] + 16*Y[i+3] \
					- 3*Y[i+4])/(12*h)
	if which_end == "right":
		i = -1
		if point_type == "three":
			dY = (-3*Y[i] + 4*Y[i-1] - Y[i-2])/(2*h)
		if point_type == "five":
			dY = (-25*Y[i] + 48*Y[i-1] \
				- 36*Y[i-2] + 16*Y[i-3] \
					- 3*Y[i-4])/(12*h)
	return dY

def gaussian_legendre(function, a, b):
	return sc.integrate.quad(function, a, b)

def integrate(function, a, b):
	return sc.integrate.quad(function, a, b)

def midpoint(X, Y, h, point_type, i):
	"""Find derivative information at some point within data set.

	Parameters
	----------
	X : list
		Domain of collected data.

	Y : array or expression
		Range of collected data.

	h : float
		Step-size through interval.

	point_type : string
		Determines if 3 or 5 pt. method is used.

	i : int
		Index at which point is to be evaluated.

	Returns
	-------
	dY : float
		Evaluated derivative at point.

	Raises
	------
	bad_X : string
		If {`X`} is neither n x 1 nor 1 x n array.

	bad_Y : string
		If {`Y`} is not an expression.

	bad_data : string
		If `X` and `Y` are of unequal length.

	bad_i : string
		`i` must be an integer and non-zero for indexing.

	bad_type : string
		If `point_type` was not an acceptable option.

	See Also
	--------
	make_array() : Prints string that expression was used to make array.

	Notes
	-----
	5 point is more accurate than 3 point; however, round-off error increases.
	"""
	sym_X, sym_Y = "X", "Y"
	bad_X = "Input domain, " + sym_X + " was neither an n x 1 nor a 1 x n array."
	bad_Y = "Input range, " + sym_Y + " was neither an n x 1 nor a 1 x n array."
	bad_data = "Arrays " + sym_X + " and " + sym_Y + " must be of equal length."
	bad_i = "Index must be an integer."
	bad_type = "I am sorry. The selected type was not understood. Please select: 'three', 'five', or '2nd_derivative'."
	if not isinstance(Y,(FunctionType, sp.Expr)):
		if np.sum(X.shape) > np.sum(X.shape[0]): raise ValueError("ERROR! " + bad_X)
		if np.sum(Y.shape) > np.sum(Y.shape[0]): raise ValueError("ERROR! " + bad_Y)
		if len(X) != len(Y): raise ValueError("ERROR! " + bad_data)
	if isinstance(Y,(FunctionType, sp.Expr)): Y = make_array(X, Y)
	if not isinstance(i,int): raise ValueError("ERROR! " + bad_i)
	h, dY = float(h), 0
	if point_type == "three":
		dY = (Y[i+1] - Y[i-1])/(2*h)
	if point_type == "five":
		dY = (Y[i-2] - 8*Y[i-1] \
			+ 8*Y[i+1] - Y[i+2])/(12*h)
	if point_type == "2nd_derivative":
		dY = (Y[i-1] - 2*Y[i] + Y[i+1])/(h**2)
	else: raise ValueError("ERROR! " + bad_type)
	return dY

def richard_extrapolation(function, x0, h, order, direction=0, variable=sp.Symbol("x")):
	"""Results in higher-accuracy of derivative at point in function with lower-order formulas to minimize round-off error and increase O(h) of truncation error.

	Parameters
	----------
	function : expression
		Polynomial over which derivative must be calculated.

	x0 : float
		Point about which extrapolation centers

	h : float
		Step-size through interval.

	order : int
		Order for rate of convergence.

	direction : string
		`'forward'` or `'backward'` construction.

	Returns
	-------
	p : expression
		Lambdified constructed polynomial.

	p(x0) : float
		Evaluation of `p` at `x`.

	Raises
	------
	bad_function : string
		If `function` is not an expression.

	bad_order : string
		`order` must be an integer and non-zero.

	bad_direction : string
		If `direction` is neither `'forward'` nor `'backward'`.

	Warns
	-----
	__func_func : string
		Evaluate input expression for Newton difference approximation.

	See Also
	--------
	newton_difference() : Newton Difference method to build extrapolation for function's derivative and order of error.
	"""
	sym_function = "function"
	bad_function = "Function, " + sym_function + " must be expression."
	bad_order = "Expected integer."
	bad_direction = "Supplied direction was not understood. Please specify 'forward' or 'backward'."
	made_poly = "I have found your requested polynomial! P = "
	if not isinstance(function,(FunctionType, sp.Expr)): 
		raise TypeError("ERROR! " + bad_function)
	if isinstance(function,(FunctionType, sp.Expr)):
		sym_function = sp.N(sp.sympify(function(variable)))
		function = sp.lambdify(variable, sym_function)
		print(f"Information: Input expression, {sym_function} used.")
	if not isinstance(order,int): raise TypeError("ERROR! " + bad_order)
	if direction != 0 and direction != "forward" and direction != "backward": raise ValueError("ERROR! " + bad_direction)
	def f(h):
		x = x0 + h
		return x, function(x)
	x0, h = float(x0), float(h)
	i, X, FX = 0, [], []
	while i < order:
		dx = h / (2**order) * (2**i)
		x_i, fx_i = f(dx)
		X.append(x_i); FX.append(fx_i)
		i += 1
	m = len(X)
	n = m + 1
	return newton_difference(X, FX, x0, direction)
# --------------------

# --------------------
# differential equations
class __ode(object):
	"""Assign common attributes to objects.
	"""
	def __init__(self, function, a, b, alpha, variables=(sp.Symbol("t"), sp.Symbol("y")), steps=100):
		"""
		Parameters
		----------
		function : expression
			Time derivative of function to approximate.

		a : float
			Initial time.

		b : float
			Final time.

		alpha : float
			Initial value at a.

		variables : tuple, optional
			Collection of symbolic or string variables to respect in function.

		steps : int or float, optional
			Maximum number of time steps to discretize domain.

		Yields
		------
		self.function : expression
			Time derivative of function to approximate.

		self.a : float
			Initial time.

		self.b : float
			Final time.

		self.alpha : float
			Initial value at a.

		self.variables : tuple, optional
			Collection of symbolic or string variables to respect in function.

		self.steps : int or float, optional
			Maximum number of time steps to discretize domain.

		Raises
		------
		ValueError
			If time steps constraint is not an integer.

		TypeError
			If input expression cannot be understood as lambda or sympy expression nor as string.

		Notes
		-----
		Make sure the independent variable is the first element of `variables`!
		"""
		if steps <= 0 or not isinstance(steps, (int, float)): raise ValueError(f"ERROR! Number of time steps, N must be an integer greater than zero. {steps} was given and not understood.")
		if np.sum(np.array(function).shape) > 0:
			F = []
			for f in function:
				if isinstance(f, (FunctionType, sp.Expr)):
					try:
						sym_function = sp.N(sp.sympify(f(variables[0])))
						f = sp.lambdify(variables[0], sym_function)
						print(f"Information: Input expression, {sym_function} used.")
					except:
						sym_function = sp.N(sp.sympify(f(*variables)))
						f = sp.lambdify(variables, sym_function)
						print(f"Information: Input expression, {sym_function} used.")
				elif isinstance(f, (str)):
					g = lambda x: eval(f)
					f = sp.lambdify(*variables, g(*variables))
					print("String expression converted to lambda function.")
				else: raise TypeError("Unknown input.")
				F.append(f)
			function = F
		else:
			if isinstance(function, (FunctionType, sp.Expr)):
				sym_function = sp.N(sp.sympify(function(*variables)))
				function = sp.lambdify(variables, sym_function)
				print(f"Information: Input expression, {sym_function} used.")
			elif isinstance(function, (str)):
				g = lambda x: eval(function)
				function = sp.lambdify(*variables, g(*variables))
				print("String expression converted to lambda function.")
			else: raise TypeError("Unknown input.")
		self.function = function
		self.a, self.b = a, b
		self.alpha = alpha
		self.variables = np.array(variables)
		self.steps = int(steps + 1)

class ivp(__ode):
	"""Class containing Initial Value Problem methods.
	"""
	def __init__(self, function, a, b, alpha, variables=(sp.Symbol("t"), sp.Symbol("y")), steps=100):
		"""
		Parameters
		----------
		function : expression
			Time derivative of function to approximate.

		a : float
			Initial time.

		b : float
			Final time.

		alpha : float
			Initial value at a.

		variables : tuple, optional
			Collection of symbolic or string variables to respect in function.

		steps : int or float, optional
			Maximum number of time steps to discretize domain.

		Attributes
		----------
		forward_euler()

		improved_euler()

		backward_euler()

		crank_nicholson()

		runge_kutta()

		Yields
		------
		self.function : expression
			Time derivative of function to approximate.

		self.a : float
			Initial time.

		self.b : float
			Final time.

		self.alpha : float
			Initial value at a.

		self.variables : tuple, optional
			Collection of symbolic or string variables to respect in function.

		self.steps : int or float, optional
			Maximum number of time steps to discretize domain.

		Raises
		------
		ValueError
			If time steps constraint is not an integer.

		TypeError
			If input expression cannot be understood as lambda or sympy expression nor as string.

		Notes
		-----
		Make sure the independent variable is the first element of `variables`!
		"""
		super().__init__(function, a, b, alpha, variables=variables, steps=steps)

	def forward_euler(self):
		"""March forward through time to approximate Initial Value Problem differential equation between endpoints a and b.

		Returns
		-------
		pandas.Dataframe() : dataframe
			Dataframe of method iterations and time domains, range of approximations for input function, and iterative increments.

		Yields
		------
		self.step_size : float
			Domain step size.

		self.iterations : tuple
			Collection of steps through method.

		self.domain : tuple
			Discretized domain between endpoints a and b for so many steps.

		self.range : tuple
			Range mapped from method through discretized domain between endpoints a and b for so many steps.

		self.increments : tuple
			Collection of increments between steps.

		Raises
		------
		TypeError
			If input expression cannot be understood as lambda or sympy expression nor as string.
		"""
		if np.sum(np.array(self.function).shape) > 0:
			F = []
			for f in self.function:
				if isinstance(f, (FunctionType, sp.Expr)):
					try:
						sym_function = sp.N(sp.sympify(f(self.variables[0])))
						f = sp.lambdify(self.variables[0], sym_function)
						# print(f"Information: Input expression, {sym_function} used.")
					except:
						sym_function = sp.N(sp.sympify(f(*self.variables)))
						f = sp.lambdify(self.variables, sym_function)
						# print(f"Information: Input expression, {sym_function} used.")
				elif isinstance(f, (str)):
					g = lambda x: eval(f)
					f = sp.lambdify(*self.variables, g(*self.variables))
					# print("String expression converted to lambda function.")
				else: raise TypeError("Unknown input.")
				F.append(f)
			function = F
		else:
			if isinstance(self.function, (FunctionType, sp.Expr)):
				try:
					sym_function = sp.N(sp.sympify(self.function(self.variables[0])))
					function = sp.lambdify(self.variables[0], sym_function)
					# print(f"Information: Input expression, {sym_function} used.")
				except:
					sym_function = sp.N(sp.sympify(self.function(*self.variables)))
					function = sp.lambdify(self.variables, sym_function)
					# print(f"Information: Input expression, {sym_function} used.")
			elif isinstance(self.function, (str)):
				g = lambda x: eval(self.function)
				function = sp.lambdify(*self.variables, g(*self.variables))
				# print("String expression converted to lambda function.")
			else: raise TypeError("Unknown input.")
		a, b, alpha = self.a, self.b, self.alpha
		variables, N = self.variables, self.steps
		h, t, w0 = float((b - a)/N), a, alpha
		self.step_size = h
		Y, increments = [w0], [0]
		for i in range(1, N):
			w = w0 + h*function(t, w0)
			Y.append(w)
			increments.append(w - w0)
			t, w0 = a + i*h, w
		self.iterations = np.array(range(N))
		self.domain = np.array(np.arange(a, t+h, h))
		self.range = np.array(Y)
		self.increments = np.array(increments)
		return pd.DataFrame(data={"Iterations": self.iterations, "Domain": self.domain, "Range": self.range, "Increments": self.increments})

	def improved_euler(self):
		"""Approximate solution of Initial Value Problem differential equation given initial time, initial value, and final time.

		Returns
		-------
		pandas.Dataframe() : dataframe
			Dataframe of method iterations and time domains, range of approximations for input function, and iterative increments.

		Yields
		------
		self.step_size : float
			Domain step size.

		self.iterations : tuple
			Collection of steps through method.

		self.domain : tuple
			Discretized domain between endpoints a and b for so many steps.

		self.range : tuple
			Range mapped from method through discretized domain between endpoints a and b for so many steps.

		self.increments : tuple
			Collection of increments between steps.

		Raises
		------
		TypeError
			If input expression cannot be understood as lambda or sympy expression nor as string.

		See Also
		--------
		runge_kutta()

		Notes
		-----
		Is 2nd-Order Runge-Kutta method where endpoint a = b = 0.5 and lambda = 1.
		"""
		if np.sum(np.array(self.function).shape) > 0:
			F = []
			for f in self.function:
				if isinstance(f, (FunctionType, sp.Expr)):
					try:
						sym_function = sp.N(sp.sympify(f(self.variables[0])))
						f = sp.lambdify(self.variables[0], sym_function)
						# print(f"Information: Input expression, {sym_function} used.")
					except:
						sym_function = sp.N(sp.sympify(f(*self.variables)))
						f = sp.lambdify(self.variables, sym_function)
						# print(f"Information: Input expression, {sym_function} used.")
				elif isinstance(f, (str)):
					g = lambda x: eval(f)
					f = sp.lambdify(*self.variables, g(*self.variables))
					# print("String expression converted to lambda function.")
				else: raise TypeError("Unknown input.")
				F.append(f)
			function = F
		else:
			if isinstance(self.function, (FunctionType, sp.Expr)):
				try:
					sym_function = sp.N(sp.sympify(self.function(self.variables[0])))
					function = sp.lambdify(self.variables[0], sym_function)
					# print(f"Information: Input expression, {sym_function} used.")
				except:
					sym_function = sp.N(sp.sympify(self.function(*self.variables)))
					function = sp.lambdify(self.variables, sym_function)
					# print(f"Information: Input expression, {sym_function} used.")
			elif isinstance(self.function, (str)):
				g = lambda x: eval(self.function)
				function = sp.lambdify(*self.variables, g(*self.variables))
				# print("String expression converted to lambda function.")
			else: raise TypeError("Unknown input.")
		a, b, alpha = self.a, self.b, self.alpha
		variables, N = self.variables, self.steps
		h, t, w0 = float((b - a)/N), a, alpha
		self.step_size = h
		ea, eb, lam = 1/2, 1/2, 1
		Y, increments = [w0], [0]
		for i in range(1, N):
			w = w0 + h*(ea*function(t, w0) + eb*function(t + lam*h, w0 + lam*h*function(t, w0)))
			Y.append(w)
			increments.append(np.abs(w - w0))
			t, w0 = a + i*h, w
		self.iterations = np.array(range(N))
		self.domain = np.array(np.arange(a, t+h, h))
		self.range = np.array(Y)
		self.increments = np.array(increments)
		return pd.DataFrame(data={"Iterations": self.iterations, "Domain": self.domain, "Range": self.range, "Increments": self.increments})

	def backward_euler(self):
		"""Use information at next time step to approximate Initial Value Problem differential equation between endpoints a and b.

		Returns
		-------
		pandas.Dataframe() : dataframe
			Dataframe of method iterations and time domains, range of approximations for input function, and iterative increments.

		Yields
		------
		self.step_size : float
			Domain step size.

		self.iterations : tuple
			Collection of steps through method.

		self.domain : tuple
			Discretized domain between endpoints a and b for so many steps.

		self.range : tuple
			Range mapped from method through discretized domain between endpoints a and b for so many steps.

		self.increments : tuple
			Collection of increments between steps.

		Raises
		------
		TypeError
			If input expression cannot be understood as lambda or sympy expression nor as string.

		See Also
		--------
		SingleVariableIteration.newton_raphson()
		"""
		if np.sum(np.array(self.function).shape) > 0:
			F = []
			for f in self.function:
				if isinstance(f, (FunctionType, sp.Expr)):
					try:
						sym_function = sp.N(sp.sympify(f(self.variables[0])))
						f = sp.lambdify(self.variables[0], sym_function)
						# print(f"Information: Input expression, {sym_function} used.")
					except:
						sym_function = sp.N(sp.sympify(f(*self.variables)))
						f = sp.lambdify(self.variables, sym_function)
						# print(f"Information: Input expression, {sym_function} used.")
				elif isinstance(f, (str)):
					g = lambda x: eval(f)
					f = sp.lambdify(*self.variables, g(*self.variables))
					# print("String expression converted to lambda function.")
				else: raise TypeError("Unknown input.")
				F.append(f)
			function = F
		else:
			if isinstance(self.function, (FunctionType, sp.Expr)):
				try:
					sym_function = sp.N(sp.sympify(self.function(self.variables[0])))
					function = sp.lambdify(self.variables[0], sym_function)
					# print(f"Information: Input expression, {sym_function} used.")
				except:
					sym_function = sp.N(sp.sympify(self.function(*self.variables)))
					function = sp.lambdify(self.variables, sym_function)
					# print(f"Information: Input expression, {sym_function} used.")
			elif isinstance(self.function, (str)):
				g = lambda x: eval(self.function)
				function = sp.lambdify(*self.variables, g(*self.variables))
				# print("String expression converted to lambda function.")
			else: raise TypeError("Unknown input.")
		a, b, alpha = self.a, self.b, self.alpha
		variables, N = self.variables, self.steps
		h, t, w0 = float((b - a)/N), a, alpha
		self.step_size = h
		Y, increments = [w0], [0]
		for i in range(1, N):
			t = a + i*h
			# w = w0 + h*function(t + h, w0 + h*function(t, w0))
			w = lambda x: x - (w0 + h*function(t + h, x))
			sys.stdout =  open(os.devnull, "w")
			foo = SingleVariableIteration(w, t, t+h, iter_guess=100)
			w = foo.newton_raphson(w0)["Approximations"].values[-1]
			sys.stdout = sys.__stdout__
			Y.append(w)
			increments.append(np.abs(w - w0))
			# t, w0 = a + i*h, w
			w0 = w
		self.iterations = np.array(range(N))
		self.domain = np.array(np.arange(a, t+h, h))
		self.range = np.array(Y)
		self.increments = np.array(increments)
		return pd.DataFrame(data={"Iterations": self.iterations, "Domain": self.domain, "Range": self.range, "Increments": self.increments})

	def trapezoidal(self, power=-6, M=100):
		"""Use information at next time step to approximate Initial Value Problem differential equation between endpoints a and b.

		Parameters
		----------
		power : int or float, optional
			Signed power to which function error must be within.

		M : int or float, optional
			Maximum iterations for Newton-Raphson loop.

		Returns
		-------
		pandas.Dataframe() : dataframe
			Dataframe of method iterations and time domains, range of approximations for input function, and iterative increments.

		Yields
		------
		self.step_size : float
			Domain step size.

		self.iterations : tuple
			Collection of steps through method.

		self.domain : tuple
			Discretized domain between endpoints a and b for so many steps.

		self.range : tuple
			Range mapped from method through discretized domain between endpoints a and b for so many steps.

		self.increments : tuple
			Collection of increments between steps.

		Raises
		------
		TypeError
			If input expression cannot be understood as lambda or sympy expression nor as string.
		"""
		if np.sum(np.array(self.function).shape) > 0:
			F = []
			for f in self.function:
				if isinstance(f, (FunctionType, sp.Expr)):
					try:
						sym_function = sp.N(sp.sympify(f(self.variables[0])))
						f = sp.lambdify(self.variables[0], sym_function)
						# print(f"Information: Input expression, {sym_function} used.")
					except:
						sym_function = sp.N(sp.sympify(f(*self.variables)))
						f = sp.lambdify(self.variables, sym_function)
						# print(f"Information: Input expression, {sym_function} used.")
				elif isinstance(f, (str)):
					g = lambda x: eval(f)
					f = sp.lambdify(*self.variables, g(*self.variables))
					# print("String expression converted to lambda function.")
				else: raise TypeError("Unknown input.")
				F.append(f)
			function = F
		else:
			if isinstance(self.function, (FunctionType, sp.Expr)):
				try:
					sym_function = sp.N(sp.sympify(self.function(self.variables[0])))
					function = sp.lambdify(self.variables[0], sym_function)
					# print(f"Information: Input expression, {sym_function} used.")
				except:
					sym_function = sp.N(sp.sympify(self.function(*self.variables)))
					function = sp.lambdify(self.variables, sym_function)
					# print(f"Information: Input expression, {sym_function} used.")
			elif isinstance(self.function, (str)):
				g = lambda x: eval(self.function)
				function = sp.lambdify(*self.variables, g(*self.variables))
				# print("String expression converted to lambda function.")
			else: raise TypeError("Unknown input.")
		a, b, alpha = self.a, self.b, self.alpha
		variables, N = self.variables, self.steps
		h, t, w0, tol = float((b - a)/N), a, alpha, 10**power
		self.step_size = h
		fpy = sp.lambdify(variables, sp.diff(function(*variables), variables[0]))
		Y, increments = [w0], [0]
		for i in range(1, N):
			k1 = w0 + h*function(t, w0)/2
			j, wj0, FLAG = 1, k1, False
			while FLAG == False:
				wj1 = wj0 - (wj0 - h/2*function(t + h, wj0) - k1)/(\
					1 - h/2*fpy(t + h, wj0))
				if np.abs(wj1 - wj0) <= tol:
					w = wj1
					FLAG = True
				else:
					wj0 = wj1
					j += 1
					if j > M: FLAG = True
			# f = lambda x: x - h/2*function(t + h, x) - k1
			# foo = SingleVariableIteration(f, a, b, power, variable=variables, iter_guess=M)
			# w = foo.newton_raphson(k1)["Approximations"][-1]
			Y.append(w)
			increments.append(np.abs(w - w0))
			t, w0 = a + i*h, w
		self.iterations = np.array(range(N))
		self.domain = np.array(np.arange(a, t+h, h))
		self.range = np.array(Y)
		self.increments = np.array(increments)
		return pd.DataFrame(data={"Iterations": self.iterations, "Domain": self.domain, "Range": self.range, "Increments": self.increments})

	def runge_kutta(self):
		"""Approximate solution of initial value problem.

		Returns
		-------
		pandas.Dataframe() : dataframe
			Dataframe of method iterations and time domains, range of approximations for input function, and iterative increments.

		Yields
		------
		self.step_size : float
			Domain step size.

		self.iterations : tuple
			Collection of steps through method.

		self.domain : tuple
			Discretized domain between endpoints a and b for so many steps.

		self.range : tuple
			Range mapped from method through discretized domain between endpoints a and b for so many steps.

		self.increments : tuple
			Collection of increments between steps.

		Raises
		------
		TypeError
			If input expression cannot be understood as lambda or sympy expression nor as string.
		"""
		if np.sum(np.array(self.function).shape) > 0:
			F = []
			for f in self.function:
				if isinstance(f, (FunctionType, sp.Expr)):
					try:
						sym_function = sp.N(sp.sympify(f(self.variables[0])))
						f = sp.lambdify(self.variables[0], sym_function)
						# print(f"Information: Input expression, {sym_function} used.")
					except:
						sym_function = sp.N(sp.sympify(f(*self.variables)))
						f = sp.lambdify(self.variables, sym_function)
						# print(f"Information: Input expression, {sym_function} used.")
				elif isinstance(f, (str)):
					g = lambda x: eval(f)
					f = sp.lambdify(*self.variables, g(*self.variables))
					# print("String expression converted to lambda function.")
				else: raise TypeError("Unknown input.")
				F.append(f)
			function = F
		else:
			if isinstance(self.function, (FunctionType, sp.Expr)):
				try:
					sym_function = sp.N(sp.sympify(self.function(self.variables[0])))
					function = sp.lambdify(self.variables[0], sym_function)
					# print(f"Information: Input expression, {sym_function} used.")
				except:
					sym_function = sp.N(sp.sympify(self.function(*self.variables)))
					function = sp.lambdify(self.variables, sym_function)
					# print(f"Information: Input expression, {sym_function} used.")
			elif isinstance(self.function, (str)):
				g = lambda x: eval(self.function)
				function = sp.lambdify(*self.variables, g(*self.variables))
				# print("String expression converted to lambda function.")
			else: raise TypeError("Unknown input.")
		a, b, alpha = self.a, self.b, self.alpha
		variables, N = self.variables, self.steps
		h, t, w0 = float((b - a)/N), a, alpha
		self.step_size = h
		Y, increments = [w0], [0]
		for i in range(1, N):
			k1 = h*function(t, w0)
			k2 = h*function(t + h/2, w0 + k1/2)
			k3 = h*function(t + h/2, w0 + k2/2)
			k4 = h*function(t + h, w0 + k3)
			w = w0 + (k1 + 2*k2 + 2*k3 + k4) / 6
			Y.append(w)
			increments.append(w - w0)
			t, w0 = a + i*h, w
		self.iterations = np.array(range(N))
		self.domain = np.array(np.arange(a, t+h, h))
		self.range = np.array(Y)
		self.increments = np.array(increments)
		return pd.DataFrame(data={"Iterations": self.iterations, "Domain": self.domain, "Range": self.range, "Increments": self.increments})

class bvp(__ode):
	"""Class containing Boundary Value Problem methods.
	"""
	def __init__(self, function, a, b, alpha, beta, variables=(sp.Symbol("x"), sp.Symbol("y"), sp.Symbol("yp")), steps=100):
		"""
		Parameters
		----------
		function : expression
			Time derivative of function to approximate.

		a : float
			Initial time.

		b : float
			Final time.

		alpha : float
			Initial value at a.

		beta : float
			Initial value at b.

		variables : tuple, optional
			Collection of symbolic or string variables to respect in function.

		steps : int or float, optional
			Maximum number of time steps to discretize domain.

		Attributes
		----------
		linear_shooting_method()

		finite_difference_method()

		Yields
		------
		self.function : expression
			Time derivative of function to approximate.

		self.a : float
			Initial time.

		self.b : float
			Final time.

		self.alpha : float
			Initial value at a.

		self.beta : float
			Initial value at b.

		self.variables : tuple, optional
			Collection of symbolic or string variables to respect in function.

		self.steps : int or float, optional
			Maximum number of time steps to discretize domain.

		Raises
		------
		ValueError
			If time steps constraint is not an integer.

		TypeError
			If input expression cannot be understood as lambda or sympy expression nor as string.

		Notes
		-----
		Make sure the independent variable is the first element of `variables`!
		"""
		super().__init__(function, a, b, alpha, variables=variables, steps=steps)
		self.beta = beta

	def linear_shooting_method(self):
		"""Solve a Boundary Value Problem differential equation with 2 Initial Value Problem differential equations.

		Returns
		-------
		pandas.Dataframe() : dataframe
			Dataframe of method iterations and time domains, range of approximations for input function, and iterative increments.

		Yields
		------
		self.step_size : float
			Domain step size.

		self.iterations : tuple
			Collection of steps through method.

		self.domain : tuple
			Discretized domain between endpoints a and b for so many steps.

		self.range : tuple
			Range mapped from method through discretized domain between endpoints a and b for so many steps.

		self.derivatives : tuple
			Collection of derivatives at each step.

		Raises
		------
		TypeError
			If input expression cannot be understood as lambda or sympy expression nor as string.
		"""
		# Parameters
		# ----------
		# f : expression
		# 	Equation to which derivative will be made.

		# a : int or float
		# 	Initial time.

		# b : int or float
		# 	Final time.
		
		# alpha : float
		# 	Initial value of solution y(t = a).

		# beta : float
		# 	Initial value of solution y(t = b).

		# h : float
		# 	Domain step-size.

		# Returns
		# -------
		# pandas.Dataframe() : dataframe
		# 	Dataframe of method iterations and time domains & range of approximations for input function and its time derivative.

		if np.sum(np.array(self.function).shape) > 0:
			F = []
			for f in self.function:
				if isinstance(f, (FunctionType, sp.Expr)):
					try:
						sym_function = sp.N(sp.sympify(f(self.variables[0])))
						f = sp.lambdify(self.variables[0], sym_function)
						# print(f"Information: Input expression, {sym_function} used.")
					except:
						sym_function = sp.N(sp.sympify(f(*self.variables)))
						f = sp.lambdify(self.variables, sym_function)
						# print(f"Information: Input expression, {sym_function} used.")
				elif isinstance(f, (str)):
					g = lambda x: eval(f)
					f = sp.lambdify(*self.variables, g(*self.variables))
					# print("String expression converted to lambda function.")
				else: raise TypeError("Unknown input.")
				F.append(f)
			function = F
		else:
			if isinstance(self.function, (FunctionType, sp.Expr)):
				try:
					sym_function = sp.N(sp.sympify(self.function(self.variables[0])))
					function = sp.lambdify(self.variables[0], sym_function)
					# print(f"Information: Input expression, {sym_function} used.")
				except:
					sym_function = sp.N(sp.sympify(self.function(*self.variables)))
					function = sp.lambdify(self.variables, sym_function)
					# print(f"Information: Input expression, {sym_function} used.")
			elif isinstance(self.function, (str)):
				g = lambda x: eval(self.function)
				function = sp.lambdify(*self.variables, g(*self.variables))
				# print("String expression converted to lambda function.")
			else: raise TypeError("Unknown input.")
		a, b, alpha, beta = self.a, self.b, self.alpha, self.beta
		variables, N = self.variables, self.steps
		h = float((b - a)/N)
		self.step_size = h
		u1, u2, v1, v2 = [alpha], [0], [0], [1]
		p, q, r, ypp = function
		for i in range(N):
			x = a + i*h
			k11 = h*u2[i]
			k12 = h*(p(x)*u2[i] + q(x)*u1[i] + r(x))
			k21 = h*(u2[i] + k12/2)
			k22 = h*(p(x + h/2)*(u2[i] + k12/2) + q(x + h/2)*(u1[i] + k11/2) + r(x + h/2))
			k31 = h*(u2[i] + k22/2)
			k32 = h*(p(x + h/2)*(u2[i] + k22/2) + q(x + h/2)*(u1[i] + k21/2) + r(x + h/2))
			k41 = h*(u2[i] + k32)
			k42 = h*(p(x + h)*(u2[i] + k32) + q(x + h)*(u1[i] + k31) + r(x + h))
			u1.append(u1[i] + (k11 + 2*k21 + 2*k31 + k41)/6)
			u2.append(u2[i] + (k12 + 2*k22 + 2*k32 + k42)/6)
			###############################
			k11 = h*v2[i]
			k12 = h*(p(x)*v2[i] + q(x)*v1[i])
			k21 = h*(v2[i] + k12/2)
			k22 = h*(p(x + h/2)*(v2[i] + k12/2) + q(x + h/2)*(v1[i] + k11/2))
			k31 = h*(v2[i] + k22/2)
			k32 = h*(p(x + h/2)*(v2[i] + k22/2) + q(x + h/2)*(v1[i] + k21/2))
			k41 = h*(v2[i] + k32)
			k42 = h*(p(x + h)*(v2[i] + k32) + q(x + h)*(v1[i] + k31))
			v1.append(v1[i] + (k11 + 2*k21 + 2*k31 + k41)/6)
			v2.append(v2[i] + (k12 + 2*k22 + 2*k32 + k42)/6)
		w1, w2 = [alpha], [(beta - u1[-1])/v1[-1]]
		for i in range(1, N+1):
			w1.append(u1[i] + w2[0]*v1[i])
			w2.append(u2[i] + w2[0]*v2[i])
			x = a + i*h
		# return pd.DataFrame(data={"Iterations": range(N+1), "Domain": np.linspace(a, b, N+1), "Range": w1, "W2": w2})
		self.iterations = np.array(range(N+1))
		self.domain = np.array(np.linspace(a, b, N+1))
		self.range = np.array(w1)
		self.derivatives = np.array(w2)
		return pd.DataFrame(data={"Iterations": self.iterations, "Domain": self.domain, "Range": self.range, "Derivatives": self.derivatives})

	def finite_difference_method(self, solver_method="gauss_seidel"):
		"""Solve a Boundary Value Problem differential equation with 2 Initial Value Problem differential equations.

		Parameters
		----------
		solver_method : str, optional
			Unless specified, system of equations will be solved by the 'gauss_seidel' method.

		Returns
		-------
		pandas.Dataframe() : dataframe
			Dataframe of method iterations and time domains, range of approximations for input function, and iterative increments.

		Yields
		------
		self.step_size : float
			Domain step size.

		self.iterations : tuple
			Collection of steps through method.

		self.domain : tuple
			Discretized domain between endpoints a and b for so many steps.

		self.range : tuple
			Range mapped from method through discretized domain between endpoints a and b for so many steps.

		self.derivatives : tuple
			Collection of derivatives at each step.

		Raises
		------
		TypeError
			If input expression cannot be understood as lambda or sympy expression nor as string.

		ValueError
			Prescribed method is not an available option.

		See Also
		--------
		MultiVariableIteration.gauss_seidel()

		MultiVariableIteration.successive_relaxation()

		MultiVariableIteration.jacobi()
		"""
		# Parameters
		# ----------
		# f : expression
		# 	Equation to which derivative will be made.

		# a : int or float
		# 	Initial time.

		# b : int or float
		# 	Final time.
		
		# alpha : float
		# 	Initial value of solution y(t = a).

		# beta : float
		# 	Initial value of solution y(t = b).

		# h : float
		# 	Domain step-size.

		# Returns
		# -------
		# pandas.Dataframe() : dataframe
		# 	Dataframe of method iterations and time domains & range of approximations for input function and its time derivative.

		if np.sum(np.array(self.function).shape) > 0:
			F = []
			for f in self.function:
				if isinstance(f, (FunctionType, sp.Expr)):
					try:
						sym_function = sp.N(sp.sympify(f(self.variables[0])))
						f = sp.lambdify(self.variables[0], sym_function)
						# print(f"Information: Input expression, {sym_function} used.")
					except:
						sym_function = sp.N(sp.sympify(f(*self.variables)))
						f = sp.lambdify(self.variables, sym_function)
						# print(f"Information: Input expression, {sym_function} used.")
				elif isinstance(f, (str)):
					g = lambda x: eval(f)
					f = sp.lambdify(*self.variables, g(*self.variables))
					# print("String expression converted to lambda function.")
				else: raise TypeError("Unknown input.")
				F.append(f)
			function = F
		else:
			if isinstance(self.function, (FunctionType, sp.Expr)):
				try:
					sym_function = sp.N(sp.sympify(self.function(self.variables[0])))
					function = sp.lambdify(self.variables[0], sym_function)
					# print(f"Information: Input expression, {sym_function} used.")
				except:
					sym_function = sp.N(sp.sympify(self.function(*self.variables)))
					function = sp.lambdify(self.variables, sym_function)
					# print(f"Information: Input expression, {sym_function} used.")
			elif isinstance(self.function, (str)):
				g = lambda x: eval(self.function)
				function = sp.lambdify(*self.variables, g(*self.variables))
				# print("String expression converted to lambda function.")
			else: raise TypeError("Unknown input.")
		a, b, alpha, beta = self.a, self.b, self.alpha, self.beta
		variables, N = self.variables, self.steps
		h = float((b - a)/N)
		self.step_size = h
		ai, bi, ci, di = [], [], [], []
		p, q, r, ypp = function
		x = a + h
		ai.append(2 + (h**2)*q(x))
		bi.append(-1 + (h/2)*p(x))
		di.append(-(h**2)*r(x) + (1 + (h/2)*p(x))*alpha)
		for i in range(2, N):
			x = a + i*h
			ai.append(2 + (h**2)*q(x))
			bi.append(-1 + (h/2)*p(x))
			ci.append(-1 - (h/2)*p(x))
			di.append(-(h**2)*r(x))
		x = b - h
		ai.append(2 + (h**2)*q(x))
		ci.append(-1 - (h/2)*p(x))
		di.append(-(h**2)*r(x) + (1 - (h/2)*p(x))*beta)
		A = np.zeros((N, N))
		np.fill_diagonal(A, ai)
		A = A + np.diagflat(bi, 1)
		A = A + np.diagflat(ci, -1)
		x0 = np.zeros(N)
		c = np.array(di)
		foo = MultiVariableIteration(A, x0, c, max_iter=1000)
		if solver_method == "gauss_seidel":
			foo.gauss_seidel()
		elif solver_method == "successive_relaxation":
			foo.successive_relaxation()
		elif solver_method == "jacobi":
			foo.jacobi()
		else: raise ValueError("ERROR! The desired method must be: 'gauss_seidel', 'successive_relaxation', or 'jacobi'.")
		approximations = foo.approximations[-1]
		approximations = np.insert(approximations, 0, alpha)
		approximations = np.append(approximations, beta)
		# return pd.DataFrame(data={"Iterations": range(len(np.linspace(a, b, N+2))), "Domain": np.linspace(a, b, N+2), "Range": approximations}), foo.iterations, foo.errors
		self.iterations = np.array(range(N+2))
		self.domain = np.array(np.linspace(a, b, N+2))
		self.range = np.array(approximations)
		return pd.DataFrame(data={"Iterations": self.iterations, "Domain": self.domain, "Range": self.range}), foo.iterations, foo.errors
# --------------------
#   #   #   #   #   #   #   #   #


#################################
## Test
# test compile of module.
class test:					 # test class
	def test():				 # test function
		"""Was the module loaded correctly?

		Raises
		------
		success : string
			Prints a message of successful function call.
		"""
		success = "Test complete."
		sys.exit(success)
#   #   #   #   #   #   #   #   #


#################################
## End of Code
# test.test()	 # "Test complete."
#   #   #   #   #   #   #   #   #
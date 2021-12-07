from math import sin, cos, atan2, sqrt
from random import randint
from vector.assistive_functions import get_normal, get_unit


class Vec2d:
	def __get_xy(self, *args) -> list[float]:
		args = args[0]
		number_of_args = len(args)

		if number_of_args == 0:
			return [0, 0]  # no arguments
		elif number_of_args == 2:
			x, y = args
			return [x, y]  # both x and y passed in
		elif number_of_args == 1:  # one argument
			arg_type = type(args[0])

			if arg_type is float or arg_type is int:  # single int or float argument
				return [args[0], args[0]]
			if arg_type is list or arg_type is tuple:
				if len(args[0]) == 1:
					return [args[0][0], args[0][0]]
				return [args[0][0], args[0][1]]  # single list argument
			if arg_type is Vec2d:
				return [args[0].x, args[0].y]

		raise TypeError(f'Invalid Input: {args}')

	def __init__(self, *args) -> None:
		self.__elements = self.__get_xy(args)


	#region Properties

	#---------------------- X
	@property
	def x(self):
		return self.__elements[0]
	@x.setter
	def x(self, val):
		self.__elements[0] = val

	#---------------------- Y
	@property
	def y(self):
		return self.__elements[1]
	@y.setter
	def y(self, val):
		self.__elements[1] = val

	#---------------------- W
	@property
	def w(self):
		return self.__elements[0]
	@w.setter
	def w(self, val):
		self.__elements[0] = val

	#---------------------- H
	@property
	def h(self):
		return self.__elements[1]
	@h.setter
	def h(self, val):
		self.__elements[1] = val

	#---------------------- Magnitude
	@property
	def length(self):
		return self.get_magnitude()


	#endregion


	#region Creation methods

	@staticmethod
	def random_unit():
		return Vec2d(get_unit(), get_unit())

	@staticmethod
	def random_pos():
		return Vec2d(get_normal(), get_normal())

	@staticmethod
	def from_angle(angle):
		return Vec2d(cos(angle), sin(angle))

	@staticmethod
	def zero():
		return Vec2d()

	#endregion


	#region General manipulation methods

	def as_floats(self):
		return list(self.__elements)

	def as_ints(self):
		return [int(self.x), int(self.y)]

	def set(self, *args):
		x, y = self.__get_xy(args)
		self.__elements = [x, y]

	def copy(self):
		return Vec2d(self.x, self.y)

	def clear(self):
		self.x = self.y = 0

	#endregion


	#region Mathematical manipulation methods

	def rotate(self, a):
		x, y = self.as_floats()
		ca = cos(a)
		sa = sin(a)

		self.x = (ca * x) + (-sa * y)
		self.y = (sa * x) + (ca * y)

	def dist_sqrt(self, *args):
		x, y = self.__get_xy(args)
		return sqrt((self.x - x)**2 + (self.y - y)**2)

	def dist(self, *args):
		x, y = self.__get_xy(args)
		return (self.x - x)**2 + (self.y - y)**2

	def get_heading_angle(self):
		return atan2(self.x, self.y)

	def get_magnitude(self):
		return sqrt(self.x**2 + self.y**2)

	def normalise(self):
		mag = self.length
		if mag == 0 : return
		self.idiv(mag)

	def normalised(self):
		v = self.copy()
		mag = v.length
		if mag == 0 : return
		v.idiv(mag)
		return v

	def clamp(self, *args):
		max_x, max_y = self.__get_xy(args)

		if self.x > max_x : self.x = max_x
		if self.y > max_y : self.y = max_y

		if self.x < -max_x : self.x = -max_x
		if self.y < -max_y : self.y = -max_y

	def iadd(self, *args):
		x, y = self.__get_xy(args)
		self.x += x
		self.y += y

	def isub(self, *args):
		x, y = self.__get_xy(args)
		self.x -= x
		self.y -= y

	def imult(self, *args):
		x, y = self.__get_xy(args)
		self.x *= x
		self.y *= y

	def idiv(self, *args):
		x, y = self.__get_xy(args)
		self.x /= x
		self.y /= y

	def ilerp(self, *args, t=0.5):
		x, y = self.__get_xy(args)

		x = self.x + t * (x - self.x)
		y = self.y + t * (y - self.y)

		self.set(x, y)

	def add(self, *args):
		x, y = self.__get_xy(args)
		return Vec2d(x + self.x, y + self.y)

	def sub(self, *args):
		x, y = self.__get_xy(args)
		return Vec2d(self.x - x, self.y - y)

	def mult(self, *args):
		x, y = self.__get_xy(args)
		return Vec2d(self.x * x, self.y * y)

	def div(self, *args):
		x, y = self.__get_xy(args)
		return Vec2d(self.x / x, self.y / y)

	def lerp(self, *args, t=0.5):
		x, y = self.__get_xy(args)

		x = self.x + t * (x - self.x)
		y = self.y + t * (y - self.y)

		return Vec2d(x, y)

	def dot(self, *args):
		x, y = self.__get_xy(args)
		return sum([self.x * x, self.y * y])

	#endregion


	#region Dunder methods

	def __iadd__(self, *args):
		x, y = self.__get_xy(args)
		self.x += x ; self.y += y
		return self

	def __isub__(self, *args):
		x, y = self.__get_xy(args)
		self.x -= x ; self.y -= y
		return self

	def __imul__(self, *args):
		x, y = self.__get_xy(args)
		self.x *= x ; self.y *= y
		return self

	def __idiv__(self, *args):
		x, y = self.__get_xy(args)
		self.x /= x ; self.y /= y
		return self

	def __add__(self, *args):
		x, y = self.__get_xy(args)
		return Vec2d(self.x + x, self.y + y)

	def __sub__(self, *args):
		x, y = self.__get_xy(args)
		return Vec2d(self.x - x, self.y - y)

	def __mul__(self, *args):
		x, y = self.__get_xy(args)
		return Vec2d(self.x * x, self.y * y)

	def __div__(self, *args):
		x, y = self.__get_xy(args)
		return Vec2d(self.x / x, self.y / y)

	def __getitem__(self, index):
		return self.__elements[index]

	def __repr__(self):
		return f'vector X: {self.x}, Y: {self.y}'

	#endregion




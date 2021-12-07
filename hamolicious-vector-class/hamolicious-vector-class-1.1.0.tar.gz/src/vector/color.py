from vector.assistive_functions import get_normal, clamp_value, translate
from vector.vector2d import Vec2d

class Color:
	def __get_rgb(self, *args) -> list[float]:
		args = args[0]
		number_of_args = len(args)

		if number_of_args == 0:
			return [0, 0, 0]  # no arguments
		elif number_of_args == 3:
			return list(args)  # x, y and z passed in
		elif number_of_args == 1:  # one argument
			arg_type = type(args[0])

			if arg_type is float or arg_type is int:  # single int or float argument
				return [args[0], args[0], args[0]]
			if arg_type is list or arg_type is tuple:
				if len(args[0]) == 1:
					return [args[0][0], args[0][0], args[0][0]]
				return [args[0][0], args[0][1], args[0][2]]  # single list argument
			if arg_type is Color:
				return [args[0].r, args[0].b, args[0].b]

		raise TypeError(f'Invalid Input: {args}')

	def __init__(self, *args) -> None:
		self.__elements = self.__get_rgb(args)

	#region Properties

	#---------------------- R
	@property
	def r(self):
		self.__elements[0] = clamp_value(self.__elements[0], 0, 255)
		return int(self.__elements[0])

	@r.setter
	def r(self, val):
		val = clamp_value(val, 0, 255)
		self.__elements[0] = val

	#---------------------- G
	@property
	def g(self):
		self.__elements[1] = clamp_value(self.__elements[1], 0, 255)
		return int(self.__elements[1])

	@g.setter
	def g(self, val):
		val = clamp_value(val, 0, 255)
		self.__elements[1] = val

	#---------------------- B
	@property
	def b(self):
		self.__elements[2] = clamp_value(self.__elements[2], 0, 255)
		return int(self.__elements[2])

	@b.setter
	def b(self, val):
		val = clamp_value(val, 0, 255)
		self.__elements[2] = val

	#---------------------- Hex

	@property
	def hex(self):
		return '#FFFFFF' #TODO Add Hex function

	#endregion

	#region Creation methods

	@staticmethod
	def random():
		return Color(get_normal() * 255, get_normal() * 255, get_normal() * 255)

	@staticmethod
	def zero():
		return Color()

	@staticmethod
	def from_hex(hex):
		c = []

		hex = hex.replace('#', '')
		for i in range(0, 6, 2):
			element = hex[i:i+2]
			c.append(int(element, 16))

		return Color(c)

	@staticmethod
	def from_hsv(*args):
		h, s, v = Color(args).get()
		s /= 100
		v /= 100

		c = v * s
		x = c * (1 - abs(h / 60) % 2 - 1)
		m = v - c

		if h <=   0 or h >  60 : return Color((c + m) * 255, (x + m) * 255, (0 + m) * 255)
		if h <=  60 or h > 120 : return Color((x + m) * 255, (c + m) * 255, (0 + m) * 255)
		if h <= 120 or h > 180 : return Color((0 + m) * 255, (c + m) * 255, (x + m) * 255)
		if h <= 180 or h > 240 : return Color((0 + m) * 255, (x + m) * 255, (c + m) * 255)
		if h <= 240 or h > 300 : return Color((x + m) * 255, (0 + m) * 255, (c + m) * 255)
		if h <= 300 or h > 360 : return Color((c + m) * 255, (0 + m) * 255, (x + m) * 255)

	#endregion

	#region Conversion methods

	def as_hex(self):
		hexadecimal = ''
		for i in range(3):
			element = hex(self.__getitem__(i)).replace('0x', '').upper()
			if len(element) == 1:
				element = '0' + element
			hexadecimal += element

		return hexadecimal

	def as_unit(self):
		c = []
		for i in range(3):
			element = translate(self.__getitem__(i), 0, 255, 0, 1)
			c.append(element)

		return c

	def as_hsv(self):
		ur = self.r / 255
		ug = self.g / 255
		ub = self.b / 255

		cmax = max(self.get())
		cmin = min(self.get())

		delta = cmax - cmin


		if   delta == 0      : h = 0
		elif cmax  == self.r : h = 60 * (((ug - ub) / delta) % 6)
		elif cmax  == self.g : h = 60 * (((ub - ur) / delta) + 2)
		elif cmax  == self.b : h = 60 * (((ur - ug) / delta) + 4)

		if cmax == 0 : s = 0
		if cmax != 0 : s = delta / cmax

		v = (cmax / 255) * 100

		return (int(h), int(s) * 100, int(v))

	#endregion

	#region General manipulation methods

	def get(self):
		return [int(self.r), int(self.g), int(self.b)]

	def set(self, *args):
		r, g, b = self.__get_rgb(args)
		self.__elements = [r, g, b]

	def copy(self):
		return Color(self.r, self.g, self.b)

	def clear(self):
		self.r = self.g = self.b = 0

	def ilerp(self, *args, t=0.5):
		r, g, b = self.__get_rgb(args)

		r = self.r + t * (r - self.r)
		g = self.g + t * (g - self.g)
		b = self.b + t * (b - self.b)

		self.set(r, g, b)

	#endregion

	#region Dunder methods

	def __iadd__(self, *args):
		r, g, b = self.__get_rgb(args)
		self.r += r
		self.g += g
		self.b += b
		return self

	def __isub__(self, *args):
		r, g, b = self.__get_rgb(args)
		self.r -= r
		self.g -= g
		self.b -= b
		return self

	def __imul__(self, *args):
		r, g, b = self.__get_rgb(args)
		self.r *= r
		self.g *= g
		self.b *= b
		return self

	def __idiv__(self, *args):
		r, g, b = self.__get_rgb(args)
		self.r /= r
		self.g /= g
		self.b /= b
		return self

	def __add__(self, *args):
		r, g, b = self.__get_rgb(args)
		return Color(self.r + r, self.g + g, self.b + b)

	def __sub__(self, *args):
		r, g, b = self.__get_rgb(args)
		return Color(self.r - r, self.g - g, self.b - b)

	def __mul__(self, *args):
		r, g, b = self.__get_rgb(args)
		return Color(self.r * r, self.g * g, self.b * b)

	def __div__(self, *args):
		r, g, b = self.__get_rgb(args)
		return Color(self.r / r, self.g / g, self.b / b)

	def __getitem__(self, index):
		return int(self.__elements[index])

	def __repr__(self):
		return f'Color R: {self.r}, G: {self.g}, B: {self.b}'

	#endregion

	#region Mathematical manipulation methods
	def iadd(self, *args):
		r, g, b = self.__get_rgb(args)
		self.r += r
		self.g += g
		self.b += b

	def isub(self, *args):
		r, g, b = self.__get_rgb(args)
		self.r -= r
		self.g -= g
		self.b -= b

	def imult(self, *args):
		r, g, b = self.__get_rgb(args)
		self.r *= r
		self.g *= g
		self.b *= b

	def idiv(self, *args):
		r, g, b = self.__get_rgb(args)
		self.r /= r
		self.g /= g
		self.b /= b

	def ilerp(self, *args, t=0.5):
		r, g, b = self.__get_rgb(args)

		r = self.r + t * (r - self.r)
		g = self.g + t * (g - self.g)
		b = self.b + t * (b - self.b)

		self.set(r, g, b)

	def add(self, *args):
		r, g, b = self.__get_rgb(args)
		return Color(self.r + r, self.g + g, self.b + b)

	def sub(self, *args):
		r, g, b = self.__get_rgb(args)
		return Color(self.r - r, self.g - g, self.b - b)

	def mult(self, *args):
		r, g, b = self.__get_rgb(args)
		return Color(self.r * r, self.g * g, self.b * b)

	def div(self, *args):
		r, g, b = self.__get_rgb(args)
		return Color(self.r / r, self.g / g, self.b / b)

	def lerp(self, *args, t=0.5):
		r, g, b = self.__get_rgb(args)

		r = self.r + t * (r - self.r)
		g = self.g + t * (g - self.g)
		b = self.b + t * (b - self.b)

		return Color(r, g, b)

	#endregion

from mathutils import *

class Derived:
	__slots__ = 'value', 'der', 'vars'
	
	def __init__(self, value, derivatives=None, vars=None):
		self.value = value
		if derivatives is None and vars is None:
			self.der = [1]
			vars = [self.value]
		else:
			self.derivatives = derivatives
			self.vars = vars
	
	def __add__(self, other):
		return Derived(self.value+other.value, self.grad+other.grad)
	def __mul__(self, other):
		return Derived(self.value*other.value, self.grad*other.value + other.grad*self.value)

def compose(func):
	dfunc = derivatives[func]
	def func(value):
		return Derived(func(value.value), value.grad * dfunc(value.value))
	return func

def dlength(v):
	indev

from .mathutils import glm

class VecList:
	def __init__(self, *args, capacity=None, dtype=vec3, fill=None):
		if args:
			self.buff = glm.array(*args)
			self.capacity = len(self.buff)
		elif capacity:
			if fill:
				self.size = capacity
			else:
				self.size = 0
				fill = dtype(0)
			self.buff = glm.array(fill) * capacity
			self.capacity = capacity
		else:
			self.buff = glm.array()
			self.capacity = 0
			self.size = 0
	
	def reserve(self, amount):
		if self.capacity - self.size < amount:
			self.buff += glm.array(self.buff[-1]) * (amount - self.capacity)
	
	def __getitem__(self, i):		return self.buff[i]
	def __setitem__(self, i, v):	self.buff[i] = v
	def __iter__(self):			return (self.buff[i]  for i in range(self.size))
	def __copy__(self):			return VecList(self.buff)
	__deepcopy__ = __copy__
	
	def append(self, v):
		self.grant(1)
		self.buff[self.size] = v
		self.size += 1
	
	def extend(self, iterable):
		for e in iterable:	self.append(e)
	
	def pop(self, i=-1):
		if i == -1 or i-self.size == -1:
			self.size -= 1
		else:
			self.buff = self.buff[:i] + self.buff[i+1:]
	
	def insert(self, i, v):
		self.grant(1)
		self.buff[i+1:] = self.buff[i:-1]
		self.buff[i] = v		
	
	def __add__(self, other):
		if isinstance(other, VecList):
			return VecList(self.buff + other.buff)
		else:
			return VecList(self.buff + glm.array(other))
	
	def __iadd_(self, other):
		if isinstance(other, VecList):
			self.buff += other.buff
		else:
			self.buff += glm.array(other)
	
	def __mul__(self, amount):
		return VecList(self.buff * amount)
	

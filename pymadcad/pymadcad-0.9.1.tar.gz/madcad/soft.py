'''
	Soft(
		points=[(vec3, strength, smooth)],		smooth: face, line, fixed
		lines=[(indices)],
		faces=[((indices), (indices))],
		spec={p:normal, e:tangent},
		)
'''

from .mathutils import *
from .mesh import MeshError

class Soft:
	def __init__(self, points=None, attrs=None, lines=None, faces=None, spec=None, groups=None):
		self.points = points or []
		self.attrs = attrs or [(1, 0)] * len(self.points)
		self.lines = lines or []
		self.faces = faces or []
		self.spec = spec or {}
		self.groups = groups or [None] * len(self.faces)
		
	def check(self):
		l = len(self.points)
		for line in self.lines:
			for i in line:
				if i >= l:		raise MeshError("some line indices are greater than the number of points")
				if i < 0:		raise MeshError("point indices must be positive")
		if len(self.groups) != len(self.faces):	raise MeshError("the number of group and faces are different")
		if len(self.points) != len(self.attrs):	raise MeshError("the number of points and point attributes are different")
		
	def isvalid(self):
		try:	self.check()
		except MeshError:	return False
		return True
		
	def mesh(self, resolution=None):
		indev
		# choose discretization for each edge
		# make discretization coherent
		# mark specific lines
		# discretize face lines



def soft(mesh):
	''' convert a mesh to a Soft '''
	if isinstance(mesh, Soft):		return mesh
	elif isinstance(mesh, Mesh):	return Soft(points=mesh.points, faces=mesh.faces, groups=mesh.groups)
	elif isinstance(mesh, Web):		return Soft(points=mesh.points, lines=mesh.edges)
	else:
		raise TypeError('cannot convert {} to Soft'.format(type(mesh).__name))

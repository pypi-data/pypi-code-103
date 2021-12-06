import numpy.core as np
from .mathutils import *
from .rendering import Display

class MeshEditor:
	def __init__(self, scene, mesh=None):
		self.points = np.empty((0,3), dtype='f4')
		self.faces = np.empty((0,3), dtype='u4')
		self.pointflags = np.empty((0,), dtype='u1')
		self.faceflags = np.empty((0,), dtype='u1')
		self.vb_points = ctx.buffer(self.points)
		self.vb_faces = ctx.buffer(self.faces)
		self.vb_edges = ctx.buffer(self.edges)
		self.vb_pointflags = ctx.buffer(self.pointflags)
		self.vb_faceflags = ctx.buffer(self.faceflags)
		
		self.va_points = ctx.vertex_array(
			self.pointshader,
			[	(self.vb_points, '3f4', 'v_position'),
				(self.vb_pointflags, 'u1', 'v_flag')],
			)
		self.va_faces = ctx.vertex_array(
			self.faceshaders,
			[(self.vb_points, '3f4', 'v_position')],
			)
		indev

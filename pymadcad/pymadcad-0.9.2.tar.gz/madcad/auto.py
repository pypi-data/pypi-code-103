'''
def matchsurfaces(s1: 'Mesh', s2: 'Mesh') -> '[(i1, i2)]':
	s1, s2 = copy(s1), copy(s2)
	s1.strippoints()
	s2.strippoints()
	n1 = s1.vertexnormals()
	n2 = s2.vertexnormals()
	
	# select match according to a minimul criterion
	match = []
	for i1 in range(len(s1)):
		candidate = 0
		best = inf
		for i2 in range(len(s2)):
			link = s2.points[i2] - s1.points[i1]
			if dot(link, n1[i1]) < 0 or dot(link, n2[i2]) > 0:	continue
			score = abs(dot(link, n1[i1]-n2[i2]))
			if score < best:
				best = score
				candidate = i1
		match[i1] = candidate if not isinf(best) else None
	# solve crossing issues by proximity propagation
	
	
	return match
'''

from .core import rasterize_triangle
from .mathutils import vec3, ivec3, glm, boundingbox, length, dot
from .hashing import meshcellsize
from collections import deque
import numpy as np

def distancefield(surface):
	''' voxel giving the field of distance to surface, each point associated with the original triangle '''
	neigh = [ivec3(1,0,0), ivec3(0,1,0), ivec3(0,0,1),
			ivec3(-1,0,0), ivec3(0,-1,0), ivec3(0,0,-1)]
	
	normals = surface.vertexnormals
	centers = [sum(surface.facepoints(f))/3  for f in surface.faces]
	cell = meshcellsize(surface)
	bound = boundingbox(surface)
	origin = bound.min
	width = bound.width
	vox = np.array(
				ivec3(glm.ceil(width/cellsize)), 
				dtype='f2, i4, u1')
	queue = deque()
	# assign faces in the voxel
	for i,f in enumerate(surface.faces):
		for k in rasterize_triangle(surface.facepoints(f)):
			vox[k] = (0,i)
			queue.append(k)
	# propagate
	while queue:
		k, i = queue.popleft()
		if vox[k][1] == i:	continue
		p = origin + step*k
		v = p - centers[i]
		f = length(v) + dot(v, normals[i])
		if vox[k][0] >= f:	continue
		vox[k] = f, i
		for n in neigh:
			queue.append((k[0]+n[0], k[1]+n[1], k[2]+n[2]))
	
	return orign, cellsize, vox

def isosurface(vox, value):
	''' create a Mesh for the surface at isovalue in the voxel field '''
	cube = [ivec3(0,0,0), 
			ivec3(1,0,0), ivec3(0,1,0), ivec3(0,0,1), 
			ivec3(1,1,0), ivec3(0,1,1), ivec3(1,0,0), 
			ivec3(1,1,1)]
	
	points = []
	used = np.zero(vox.shape, 'u4')
	for x in range(vox.shape[0]):
		for y in range(vox.shape[1]):
			for z in range(vox.shape[2]):
				p = ivec3(x,y,z)
				l = [vox[p+n]  for n in cube]
				if min(l) < value and max(l) > value:
					points.append(pointsolve(vox, p, value))
					used[p] = len(points)
					for n in neigh:
						if used[p+n]:
							indev
	

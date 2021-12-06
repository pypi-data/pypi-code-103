from math import inf
from .mathutils import glm,vec2,dvec2,dmat2, perp, perpdot, length, distance, normalize, inverse, isnan, norminf, NUMPREC
from .mesh import Mesh, Web, Wire


def triangulation(outline, prec=NUMPREC):
	try:				m = triangulation_outline(outline, prec)
	except MeshError:	m = triangulation_skeleton(outline, prec)
	return m


def skeleting(outline: Wire, skeleting: callable, prec=NUMPREC) -> [vec2]:
	''' skeleting procedure for the given wire
		at each step, the skeleting function is called
		created points will be added to the wire point buffer and this buffer is returned (ROI)
	'''
	l = len(outline)
	pts = outline.points
	
	# edge normals
	enormals = [perp(normalize(outline[i]-outline[i-1]))	for i in range(l)]
	# compute half axis starting from each point
	haxis = []
	for i in range(l):
		haxis.append((outline.indices[i], i, (i+1)%l))
	
	# create the intersections to update
	intersect = [(0,0)] * l	# intersection for each edge
	dist = [-1] * l	# min distance for each edge
	def eval_intersect(i):
		o1,a1,b1 = haxis[i-1]
		o2,a2,b2 = haxis[i]
		# compute normals to points
		v1 = enormals[a1]+enormals[b1]
		v2 = enormals[a2]+enormals[b2]
		if norminf(v1) < prec:	v1 =  perp(enormals[b1])	# if edges are parallel, take the direction to the shape
		if norminf(v2) < prec:	v2 = -perp(enormals[b2])
		# compute the intersection
		x1,x2 = inverse(dmat2(v1,-v2)) * dvec2(-pts[o1] + pts[o2])
		if x1 >= -NUMPREC and x2 >= -NUMPREC:
			intersect[i] = pts[o2] + x2*v2
			dist[i] = min(x1*length(v1), x2*length(v2))
		elif isnan(x1) or isnan(x2):
			intersect[i] = pts[o2]
			dist[i] = 0
		else:
			intersect[i] = None
			dist[i] = inf
	for i in range(l):
		eval_intersect(i)
	
	# build skeleton
	while len(haxis) > 1:
		print(dist)
		i = min(range(len(haxis)), key=lambda i:dist[i])
		assert dist[i] != inf, "no more intersection found (algorithm failure)"
		o1,a1,b1 = haxis[i-1]
		o2,a2,b2 = haxis[i]
		# add the intersection point
		ip = len(pts)
		pts.append(intersect[i])
		# extend skeleton
		skeleting(haxis, i, ip)
		# create the new half axis
		haxis.pop(i)
		dist.pop(i)
		intersect.pop(i)
		haxis[i-1] = (ip, a1, b2)
		eval_intersect((i-2) % len(haxis))
		eval_intersect((i-1) % len(haxis))
		eval_intersect(i % len(haxis))
		eval_intersect((i+1) % len(haxis))
		eval_intersect((i+2) % len(haxis))
	
	return pts

def skeleton(outline: Wire, prec=NUMPREC) -> Web:
	''' return a Web that constitute the skeleton of the outline
		the returned Web uses the same point buffer than the input Wire.
		created points will be added into it
	'''
	skeleton = []
	#def sk(ip, o1,o2, a1,b1, a2,b2):
		#skeleton.append((o1,ip))
		#skeleton.append((o2,ip))
	def sk(haxis, i, ip):
		skeleton.append((haxis[i-1][0], ip))
		skeleton.append((haxis[i][0], ip))
	pts = skeleting(outline, sk, prec)
	return Web(pts, skeleton)

def triangulation_skeleton(outline: Wire, prec=NUMPREC) -> Mesh:
	''' return a Mesh with triangles filling the surface of the outline 
		the returned Mesh uses the same point buffer than the input Wire
	'''
	triangles = []
	skeleton = []
	pts = outline.points
	original = len(pts)
	minbone = [inf]
	def sk(haxis, i, ip):
		triangles.append((haxis[i-2][0], haxis[i-1][0], ip))
		triangles.append((haxis[i-1][0], haxis[i][0], ip))
		triangles.append((haxis[i][0], haxis[(i+1)%len(haxis)][0], ip))
		if   haxis[i-1][0] < original:
			d = distance(pts[haxis[i-1][0]], pts[ip])
			if d < minbone[0]:	minbone[0] = d
		else:
			skeleton.append((haxis[i-1][0], ip))
		if haxis[i][0] < original:
			d = distance(pts[haxis[i][0]], pts[ip])
			if d < minbone[0]:	minbone[0] = d
		else:
			skeleton.append((haxis[i][0], ip))
	pts = skeleting(outline, sk, prec)
	m = Mesh(pts, triangles)
	# merge points from short internal edges
	minbone = 0.5*minbone[0]
	merges = {}
	for a,b in skeleton:
		if distance(pts[a], pts[b]) < minbone:
			if   a not in merges:	merges[a] = merges.get(b,b)
			elif b not in merges:	merges[b] = merges.get(a,a)
	for k,v in merges.items():
		while v in merges and merges[v] != v:	
			if distance(pts[k], pts[v]) > minbone:
				merges[k] = k
				merges[v] = v
				break
			merges[k] = v = merges[v]
	m.mergepoints(merges)
	return m

def triangulation_outline(outline: Wire) -> Mesh:
	''' return a mesh with the triangles formed in the outline
		the returned mesh uses the same buffer of points than the input
	'''
	pts = outline.points
	
	hole = list(outline.indices)
	scores = [score(i) for i in range(len(outline))]
	def score(i):
		u = pts[hole[i+1]] - pts[hole[i]]
		v = pts[hole[i-1]] - pts[hole[i]]
		score = perpdot(u,v) / (length(u)+length(v)+length(u-v))
		if score < 0:	return score
		# check that there is not point of the outline inside the triangle
		decomp = inverse(dmat2(u,v))
		inside = False
		o = pts[hole[i]]
		for j,ip in range(len(hole)):
			if j != i and j != (i-1)%l and j != (i+1)%l:
				p = pts[hole[j]]
				uc,vc = decomp * dvec2(p-o)
				if 0 < uc and 0 < vc and uc+vc < 1:
					inside = True
					break
		if inside:
			score = -inf
		return score
	
	triangles = []
	while len(hole) > 2:
		l = len(outline)
		i = max(range(l), key=lambda i:scores[i])
		assert scores[i] > 0, "no more feasible triangles (algorithm failure)"
		triangles.append((hole[(i-1)%l], hole[i], hole[(i+1)%l]))
		hole.pop(i)
		scores[i-1] = score(i-1)
		scores[i] = score(i)
	
	return Mesh(pts, triangles)

from .mathutils import dot

def triangulation_sweepline(outline: Web) -> Mesh:
	''' sweep line algorithm to triangulate an outline
		the web edges should not be oriented, and thus the resulting face has no orientation
		complexity: O(n*ln2(n))
	'''
	pts = outline.points
	faces = []
	# select the direction with the maximum interval
	diag = glm.abs(outline.box().width)
	sortdim = 0
	if diag[1] > sortdim:	sortdim = 1
	if diag[2] > sortdim:	sortdim = 2
	# orient edges along the axis and sort them
	if len(outline.edges) < 3:	return Mesh()
	edges = outline.edges[:]
	for i,(a,b) in enumerate(edges):
		if pts[a][sortdim] < pts[b][sortdim]:	edges[i] = b,a
	stack = sorted(edges, key=lambda e: pts[e[0]][sortdim] )
	# direction of direct rotation the outline
	y = pts[stack[-1][1]] - pts[stack[-2][1]]
	y[sortdim] = 0
	
	def affine(e):
		v = pts[e[1]] - pts[e[0]]
		return (pts[e[0]], v/v[sortdim] if v[sortdim] else 0)
		
	clusters = []
	while stack:
		edge = stack.pop()
		# get the pair edge if there is one starting at the same point
		coedge = None
		for i in reversed(range(len(stack))):
			if pts[stack[i][0]][sortdim] < pts[edge[0]][sortdim]:	break
			#if edge[0] == stack[i][0]:
			if edge[0] == stack[i][0] and edge[1] != stack[i][1]:
				coedge = stack.pop(i)
				if dot(pts[edge[1]]-pts[edge[0]], y) < dot(pts[coedge[1]]-pts[coedge[0]], y):
					edge, coedge = coedge, edge
				break
		print(edge, coedge)
		
		# search in which cluster we are
		found = False
		#for i,cluster in enumerate(clusters):
		i = 0
		while i < len(clusters):
			p = pts[edge[0]]
			l0,l1,a0,a1 = clusters[i]
			
			if l0[1] == l1[1]:	
				faces.append((l0[0], l0[1], l1[0]))
				clusters.pop(i)
				continue
			
			print('   ', l0,l1,edge[0])
			# interior hole
			if coedge:
				if dot(p - a0[0]+a0[1]*p[sortdim], y) < 0 and dot(p - a1[0]+a1[1]*p[sortdim], y) > 0:
					#print('hole for ',i, edge)
					faces.append((l1[0], l0[0], edge[0]))
					clusters[i] = (l0, edge, a0, affine(edge))
					clusters.append((coedge, l1, affine(coedge), a1))
					found = True
					break
			# continuation of already existing edge of the cluster
			elif edge[0] == l0[1]:
				faces.append((l1[0], l0[0], l0[1]))
				clusters[i] = (edge, l1, affine(edge), a1)
				found = True
				break
			elif edge[0] == l1[1]:
				faces.append((l0[0], l1[1], l1[0]))
				clusters[i] = (l0, edge, a0, affine(edge))
				found = True
				break
			i += 1
		# if it's a new corner
		if coedge and not found:
			faces.append((edge[0], edge[1], coedge[1]))
			clusters.append((edge, coedge, affine(edge), affine(coedge)))
		#elif not coedge and not found:
			#raise Exception("algorithm failure, can be due to the given outline")
			
	for cluster in clusters:
		l0,l1,a0,a1 = cluster
		faces.append((l0[0], l0[1], l1[0]))
		if l0[1] != l1[1]:
			faces.append((l1[0], l0[1], l1[1]))
	
	return Mesh(pts, faces)

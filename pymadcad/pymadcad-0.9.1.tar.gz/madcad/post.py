''' pymadcad submodule for mesh post processing '''

def stretch(mesh, curve=0.1, locked=()):
	''' stretching smoothing of the surface until reaching a certain curve (rad/m)
		locked can be a set of points that won't be moved
		
		We advise having a well subdivided surface (use `subdivide` before if necessary)
	'''
	conn = connef(mesh.faces)
	edges = set(edgekey(*e)  for e in conn)
	pts = mesh.points
	def current_curve(a,b):
		c = arrangeface(mesh.faces[conn[(a,b)]], a)[2]
		d = arrangeface(mesh.faces[conn[(b,a)]], b)[2]
		z = normalise(b-a)
		cy = noproject(c-a, z)
		dy = noproject(d-a, z)
		cyl = length(cy)
		dyl = length(dy)
		return cross(dy, dy) / (cyl*dyl) / (cyl+dyl)
	
	curve = {e: current_curve(*e)	for e in edges}	# curve around each edge
	indev

def refine(mesh, ratio:float) -> Mesh:
	''' increase the resolution by adding interpolated points to the surface '''
	indev
	
def flipdiags(mesh) -> Mesh:
	''' flip quad diagonals to improve the surface smoothness '''
	indev
	
def subdivide(mesh, cuts=1) -> Mesh:
	''' subdivide each triangle '''
	indev
	
def edgedivide(mesh, edges=None, cuts=1) -> Mesh:
	''' subdivide the given edges in the mesh, or mesh outlines if nothing is provided '''
	if edges is None:	edges = mesh.outlines_oriented()
	indev



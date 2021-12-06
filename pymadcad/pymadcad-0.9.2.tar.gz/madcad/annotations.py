from .rendering import Group
from .kinematic import Solid
from .mesh import Container
from .mathutils import vec3
from .primitives import isaxis

def annotate(source, scene, recur=-1):
	if not isinstance(scene, Scene):
		raise TypeError('scene must be a Scene')
	
	def recur(source, level, recur):
		for sub,src in sourceitems(source):
			disp = level.displays.get(sub)
			if not disp:	continue
			
			if isinstance(disp, Group):
				annotate(src, disp.displays, recur-1, scene)
			
			if isinstance(src, vec3):
				level.displays[str(sub)+'#annotation'] = text.TextDisplay(
					scene, obj, str(sub), 
					size=settings.display['view_font_size'], 
					color=settings.display['annotation_color'], 
					align=(-1,1),
					)
			elif isaxis(src):
				pass # TODO
			elif isinstance(src, Container):
				pass # TODO: arrow annotation
			elif isinstance(src, Kinematic):
				makescheme(src.joints)
	
	recur(source, scene, recur)
	

def sourceitems(obj):
	if isinstance(obj, list):	return enumerate(obj)
	elif isinstance(obj, dict):	return obj.items()
	else:	return ()


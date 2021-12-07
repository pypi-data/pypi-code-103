# coding: utf-8
"""
Direct visualization with VPython.

Usage:
    genice III -f vpython

    opens a window in the web browser to show the image.

Options:

    No options available.

"""

desc = { "ref": {"VPython": "https://vpython.org"},
         "brief": "Visualize in the browser.",
         "usage": "No options available.",
         }



from collections import defaultdict
import colorsys
import numpy as np
import networkx as nx
import vpython as vp
from countrings import countrings_nx as cr
import genice2.formats
from genice2.molecules import serialize
from genice2.decorators import timeit, banner
from logging import getLogger

hue_sat = {3:(60., 1.0), 4:(180, 0.8), 5:(0, 0.5), 6:(0, 0.0), 7:(240, 0.5), 8:(300, 0.5)}

sun = np.array([1., -10., 5.])  # right, down, front
sun /= np.linalg.norm(sun)

def face(center, rpos):
    n = rpos.shape[0]

    # normalize relative vectors
    normalized = np.zeros_like(rpos)
    for i in range(n):
        normalized[i] = rpos[i] / np.linalg.norm(rpos[i])
    #normal for each triangle
    normals = np.zeros_like(rpos)
    for i in range(n):
        normals[i] = np.cross(normalized[i-1], normalized[i])
    # central normal
    c_normal = np.sum(normals, axis=0)
    c_normal /= np.linalg.norm(c_normal)
    if np.dot(c_normal, sun) < 0.0:
        c_normal = - c_normal
        normals  = - normals

    hue, sat = hue_sat[n]
    bri = 1
    r,g,b = colorsys.hsv_to_rgb(hue/360., sat, bri)
    pos = rpos + center
    v_center = vp.vertex( pos=vp.vector(*center), normal=vp.vector(*c_normal), color=vp.vector(r,g,b), opacity=0.75)
    vertices = [vp.vertex( pos=vp.vector(*p), normal=vp.vector(*(normals[i])), color=vp.vector(r,g,b), opacity=0.75) for i,p in enumerate(pos)]
    faces = set()
    for i in range(n):
        faces.add(vp.triangle(v0=vertices[i-1], v1=vertices[i], v2=v_center ))
#    group.add(sw.shapes.Polygon(pos, fill=rgb, stroke_linejoin="round", fill_opacity="1.0", stroke="#444", stroke_width=3))
    return faces










def draw(ice):
    logger = getLogger()
    atoms = []
    for mols in ice.universe:
        atoms += serialize(mols)
    logger.info("  Total number of atoms: {0}".format(len(atoms)))
    cellmat = ice.repcell.mat
    offset = (cellmat[0] + cellmat[1] + cellmat[2]) / 2
    # prepare the reverse dict
    waters = defaultdict(dict)
    for atom in atoms:
        resno, resname, atomname, position, order = atom
        if "O" in atomname:
            waters[order]["O"] = position - offset
        elif "H" in atomname:
            if "H0" not in waters[order]:
                waters[order]["H0"] = position - offset
            else:
                waters[order]["H1"] = position - offset
    for order, water in waters.items():
        O = water["O"]
        H0 = water["H0"]
        H1 = water["H1"]
        ice.vpobjects['w'].add(vp.simple_sphere(radius=0.05, pos=vp.vector(*O), color=vp.vector(1,0,0)))
        ice.vpobjects['w'].add(vp.simple_sphere(radius=0.025, pos=vp.vector(*H0), color=vp.vector(0,1,1)))
        ice.vpobjects['w'].add(vp.simple_sphere(radius=0.025, pos=vp.vector(*H1), color=vp.vector(0,1,1)))
        ice.vpobjects['w'].add(vp.cylinder(radius=0.015, pos=vp.vector(*O), axis=vp.vector(*(H0-O))))
        ice.vpobjects['w'].add(vp.cylinder(radius=0.015, pos=vp.vector(*O), axis=vp.vector(*(H1-O))))
        ice.vpobjects['l'].add(vp.label(pos=vp.vector(*O), xoffset=30, text="{0}".format(order), visible=False))
    for i,j in ice.spacegraph.edges(data=False):
        if i in waters and j in waters:  # edge may connect to the dopant
            O = waters[j]["O"]
            Oi = waters[i]["O"]
            d = O - Oi
            print(d@d)
            if d@d < 0.3**2:
                ice.vpobjects['a'].add(vp.arrow(shaftwidth=0.015, pos=vp.vector(*Oi), axis=vp.vector(*(O-Oi)), color=vp.vector(1,1,0)))
    logger.info("  Tips: use keys to draw/hide layers. [3 4 5 6 7 8 a w l]")






class Format(genice2.formats.Format):
    """
    Visualize in a browser using VPython.
    """
    def hooks(self):
        return {4:self.Hook4, 6:self.Hook6}

    @timeit
    @banner
    def __init__(self, **kwargs):
        "ArgParser (VPython)."
        logger = getLogger()
        for key, value in kwargs.items():
            assert False, "  Wrong options."
        # prepare the canvas
        # vp.canvas.background=vp.color.white


    @timeit
    @banner
    def Hook4(self, ice):
        "VPython (polyhedral expressions)."
        graph = nx.Graph(ice.spacegraph) #undirected
        cellmat = ice.repcell.mat
        ice.vpobjects = defaultdict(set)
        for ring in cr.CountRings(graph, pos=ice.reppositions).rings_iter(8):
            deltas = np.zeros((len(ring),3))
            for k,i in enumerate(ring):
                d = ice.reppositions[i] - ice.reppositions[ring[0]]
                d -= np.floor(d+0.5)
                deltas[k] = d
            comofs = np.sum(deltas, axis=0) / len(ring)
            deltas -= comofs
            com = ice.reppositions[ring[0]] + comofs
            com -= np.floor(com)
            # rel to abs
            com    = np.dot(com-0.5,    cellmat)
            deltas = np.dot(deltas, cellmat)
            ringsize = '{0}'.format(len(ring))
            ice.vpobjects[ringsize] |= face(com, deltas)


    @timeit
    @banner
    def Hook6(self, ice):
        "Display water molecules with VPython."
        draw(ice)
        # Toggle visibility
        visible = dict()
        for L in ice.vpobjects:
            visible[L] = False
        visible['l'] = True
        face_opacity = 1.0
        while True:
            ev = vp.scene.waitfor("keydown")
            if ev.key in ice.vpobjects:
                for L in ice.vpobjects[ev.key]:
                    L.visible = visible[ev.key]
                visible[ev.key] = not visible[ev.key]
            elif ev.key == "<":
                if face_opacity > 0.25:
                    face_opacity -= 0.25
                    for f in "345678":
                        if f in ice.vpobjects:
                            for L in ice.vpobjects[f]:
                                # L.opacity = face_opacity
                                print(L)

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import math

import compas_rhino
from compas.geometry import add_vectors
from compas.geometry import scale_vector
from compas.geometry import subtract_vectors
from compas.geometry import centroid_points


__all__ = ['mesh_ud']


def mesh_ud(formobject, forceobject, translation, scale=0.5):

    formdiagram = formobject.diagram
    forcediagram = forceobject.diagram

    formdiagram_xyz = formobject.vertex_xyz
    forcediagram_xyz = forceobject.vertex_xyz

    # --------------------------------------------------------------------------
    #   0. evaluate unified diagram scale
    # --------------------------------------------------------------------------
    if scale == 0:
        compas_rhino.display_message('A unified diagram with a scale of 0 is equivalent to the polyhedral force diagram.')
        return

    if scale == 1:
        compas_rhino.display_message('A unified diagram with a scale of 1 is equivalent to the polyhedral form diagram.')
        return

    assert 0 < scale and scale < 1, "Scale needs to be between 0 and 1."

    # --------------------------------------------------------------------------
    #   1. current positions of diagrams
    # --------------------------------------------------------------------------
    form_center = centroid_points(formdiagram_xyz.values())
    # force_center = centroid_points(forcediagram_xyz.values())

    # --------------------------------------------------------------------------
    #   2. get base points
    # --------------------------------------------------------------------------
    base_xyz = {}

    # determine location
    rotation = -math.pi/2

    if forceobject.settings['rotate.90deg']:
        rotation = 0.0

    for vkey in formdiagram.vertices():
        init_xyz = formdiagram_xyz[vkey]
        base_xyz[vkey] = _rotate_pt_xy(add_vectors(init_xyz, translation), rotation, add_vectors(form_center, translation))

    # --------------------------------------------------------------------------
    #   3. compute scaled forcediagram faces
    # --------------------------------------------------------------------------
    scaled_vertices_per_face = {}
    scaled_faces = {}  # {fkey: [xyz, xyz, xyz ...] ... }

    for face in forcediagram.faces():
        new_face_vertices = {}
        new_face_xyz = []
        for vertex in forcediagram.face_vertices(face):
            arm = scale_vector(subtract_vectors(forcediagram_xyz[vertex], base_xyz[face]), scale)
            scaled_xyz = add_vectors(base_xyz[face], arm)
            new_face_vertices[vertex] = scaled_xyz
            new_face_xyz.append(scaled_xyz)
        scaled_vertices_per_face[face] = new_face_vertices
        scaled_faces[face] = new_face_xyz

    # --------------------------------------------------------------------------
    #   4. bars
    # --------------------------------------------------------------------------
    bars = {}
    for u, v in forcediagram.edges():
        if not forcediagram.is_edge_on_boundary(u, v):
            f1, f2 = forcediagram.dual_edge((u, v))
            pt1 = scaled_vertices_per_face[f1][u]
            pt2 = scaled_vertices_per_face[f1][v]
            pt3 = scaled_vertices_per_face[f2][v]
            pt4 = scaled_vertices_per_face[f2][u]
            bars[(u, v)] = [pt1, pt2, pt3, pt4]

    return scaled_faces, bars


def _rotate_pt_xy(point, angle, origin):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    px, py = point[:2]
    ox, oy = origin[:2]

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy, 0

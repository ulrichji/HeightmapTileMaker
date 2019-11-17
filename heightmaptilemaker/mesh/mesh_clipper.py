from . import mesh
from . import clip_polygon
from progress.null_callback import NullCallback
from progress.progress import Progress

import numpy as np

from math import sqrt
import time

def getHexagon():
    hexagon_mesh = mesh.Mesh()
    vertices = [(0, 0.5, 0),
                (1/4, 0.5 - (sqrt(3)/4), 0),
                (3/4, 0.5 - (sqrt(3)/4), 0),
                (1, 0.5, 0),
                (3/4, 0.5 + (sqrt(3)/4), 0),
                (1/4, 0.5 + (sqrt(3)/4), 0)]
    face = [0, 1, 2, 3, 4, 5]

    for vertex in vertices:
        hexagon_mesh.addVertex(mesh.MeshVertex(position=vertex))
    hexagon_mesh.addFace(mesh.MeshFace(face))

    return hexagon_mesh

def _getClipPolygonFromFace(face, mesh):
    face_vertices = [mesh.getVertex(index) for index in face]
    vertices_positions = [vertex.position for vertex in face_vertices]
    result_polygon = clip_polygon.Polygon(vertices_positions)
    return result_polygon

def _getMeshClipPolygons(mesh):
    return [_getClipPolygonFromFace(face, mesh) for face in mesh.getFaces()]

def clipMesh(mesh_to_cut, clip_mesh, progress_callback=NullCallback()):
    return_mesh = mesh.Mesh()
    clip_polygons = _getMeshClipPolygons(clip_mesh)

    add_vertex_time = 0
    clip_time = 0

    number_of_faces = len(mesh_to_cut.getFaces())
    for i, face in enumerate(mesh_to_cut.getFaces()):
        progress_callback(Progress(progress=i, message="Creating heightmap", max_progress=number_of_faces))
        mesh_vertices = [mesh_to_cut.getVertex(index).position for index in face]
        polygon_to_clip = clip_polygon.Polygon(mesh_vertices)

        for clipper_polygon in clip_polygons:
            clip_time_start = time.time()
            clipped_polygon = clipper_polygon.clip(polygon_to_clip)
            clip_time += time.time() - clip_time_start
            if len(clipped_polygon.points) > 0:
                add_vertex_time_start = time.time()
                return_mesh.addFaceFromVertices([mesh.MeshVertex(np.array(point)) for point in clipped_polygon.points])
                add_vertex_time += time.time() - add_vertex_time_start

    return_mesh.removeDuplicates()
    return return_mesh

from . import obj_mesh

import numpy as np

class MeshVertex:
    def __init__(self, position=None, uv_coord=None, normal=None):
        self.position = position
        self.uv_coord = uv_coord
        self.normal = normal

    def scale(self, scale):
        self.position = (self.position[0] * scale, self.position[1] * scale, self.position[2] * scale)

class MeshFace:
    def __init__(self, indices):
        self.indices = indices

class Mesh:
    def __init__(self):
        self.vertices = []
        self.faces = []

    def addVertex(self, vertex):
        self.vertices.append(vertex)

    def addFace(self, face):
        self.faces.append(face)

    def getVerticesPositions(self):
        return [vertex.position for vertex in self.vertices]

    def getVerticesUVCoords(self):
        return None
        #return [vertex.uv_coord for vertex in self.vertices]

    def getVerticesNormals(self):
        return None
        #return [vertex.normal for vertex in self.vertices]

    def getFaces(self):
        return [[index for index in face.indices] for face in self.faces]

    def scale(self, scale):
        for vertex in self.vertices:
            vertex.scale(scale)

    def validate(self):
        for face in self.faces:
            for vertex_index in face.indices:
                if vertex_index >= len(self.vertices) or vertex_index < 0:
                    return False
        return True

    def exportObj(self, obj_file, object_name='heightmap'):
        obj_exporter = obj_mesh.ObjMesh(mesh=self, object_name=object_name)
        obj_exporter.save(obj_file)

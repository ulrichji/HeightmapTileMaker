import numpy as np

import json

class MeshVertex:
    def __init__(self, position=None, uv_coord=None, normal=None):
        self.position = position
        self.uv_coord = uv_coord
        self.normal = normal

    def scale(self, scale):
        self.position = (self.position[0] * scale, self.position[1] * scale, self.position[2] * scale)

    def getPositionAsJson(self):
        if self.position is None:
            return None
        return {'x': self.position[0], 'y': self.position[1], 'z': self.position[2]}

    def getUVAsJson(self):
        if self.uv_coord is None:
            return None
        return {'u': self.uv_coord[0], 'v': self.uv_coord[1]}

    def getNormalAsJson(self):
        if self.normal is None:
            return None
        return {'x': self.normal[0], 'y': self.normal[1], 'z': self.normal[2]}

    def asJson(self):
        vertex_json = {}
        position_json = self.getPositionAsJson()
        uv_json = self.getUVAsJson()
        normal_json = self.getNormalAsJson()

        if position_json is not None:
            vertex_json['position'] = position_json
        if uv_json is not None:
            vertex_json['uv'] = uv_json
        if normal_json is not None:
            vertex_json['normal'] = normal_json

        return vertex_json

    def setPositionFromJson(self, position_object):
        self.position = [float(position_object['x']),
                         float(position_object['y']),
                         float(position_object['z'])]

    def setUVFromJson(self, uv_object):
        self.uv = [float(uv_object['u']), float(uv_object['v'])]

    def setNormalFromJson(self, normal_object):
        self.normal = [float(normal_object['x']),
                       float(normal_object['y']),
                       float(normal_object['z'])]

    def fromJson(self, json_object):
        if 'vertex' not in json_object:
            raise Exception('No vertex data provided')

        vertex_object = json_object['vertex']
        if 'position' in vertex_object:
            self.setPositionFromJson(vertex_object['position'])
        if 'uv' in vertex_object:
            self.setUVFromJson(vertex_object['uv'])
        if 'normal' in vertex_object:
            self.setNormalFromJson(vertex_object['normal'])

        return self

class MeshFace:
    def __init__(self, indices):
        self.indices = indices

class Mesh:
    def __init__(self):
        self.vertices = []
        self.faces = []

    def addVertex(self, vertex):
        self.vertices.append(vertex)

    def getVertex(self, index):
        return self.vertices[index]

    def addFace(self, face):
        self.faces.append(face)

    def getFace(self, index):
        return self.faces[index]

    def getVertices(self):
        return self.vertices

    def vertexCount(self):
        return len(self.vertices)

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

    def faceCount(self):
        return len(self.faces)

    def scale(self, scale):
        for vertex in self.vertices:
            vertex.scale(scale)

    def validate(self):
        for face in self.faces:
            for vertex_index in face.indices:
                if vertex_index >= len(self.vertices) or vertex_index < 0:
                    return False
        return True

    def getVerticesAsJson(self):
        json_list = [{'vertex': vertex.asJson()} for vertex in self.getVertices()]
        return json_list

    def getFacesAsJson(self):
        json_list = self.getFaces()
        return json_list

    def asJson(self):
        json_object = {
            'vertices': self.getVerticesAsJson(),
            'faces': [{'face': indices} for indices in self.getFacesAsJson()]
        }
        return json_object

    def getJsonText(self):
        json_content = self.asJson()
        return json.dumps(json_content)

    def loadJsonVertices(self, vertex_list):
        self.vertices = [MeshVertex().fromJson(vertex_element) for vertex_element in vertex_list if 'vertex' in vertex_element]

    def loadJsonFaces(self, faces_list):
        self.faces = [MeshFace(face['face']) for face in faces_list if 'face' in face]

    def loadJson(self, json_object):
        if 'vertices' not in json_object:
            raise Exception('File does not have vertex data')
        if 'faces' not in json_object:
            raise Exception('File does not have face data')

        vertex_list = json_object['vertices']
        face_list = json_object['faces']

        self.loadJsonVertices(vertex_list)
        self.loadJsonFaces(face_list)

    def save(self, file_name):
        json_text = self.getJsonText()
        f = open(file_name, 'w')
        f.write(json_text)
        f.close()

    def load(self, file_name):
        f = open(file_name, 'r')
        json_text = f.read()
        f.close()
        json_object = json.loads(json_text)
        self.loadJson(json_object)

        return self

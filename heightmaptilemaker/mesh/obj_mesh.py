class ObjFace:
    def __init__(self, vertex_indices, uv_indices=None, normal_indices=None):
        if vertex_indices is None:
            raise Exception("A face must have vertex indices")
        if len(vertex_indices) < 3:
            raise Exception("A face must have at least three vertex indices")
        if uv_indices is not None and len(vertex_indices) != len(uv_indices):
            raise Exception("UV indices must either be None or of same length as vertex indices")
        if normal_indices is not None and len(vertex_indices) != len(normal_indices):
            raise Exception("Normal indices must either be None or of same length as vertex indices")

        self.vertex_indices = vertex_indices
        self.uv_indices = uv_indices
        self.normal_indices = normal_indices

    def getObjText(self):
        included_lists = []

        included_lists.append([str(index + 1) for index in self.vertex_indices])
        if self.uv_indices is not None:
            included_lists.append([str(index + 1) for index in self.uv_indices])
        if self.normal_indices is not None and self.uv_indices is None:
            included_lists.append(['' for index in self.normal_indices])
        if self.normal_indices is not None:
            included_lists.append([str(index + 1) for index in self.normal_indices])

        face_obj_text = 'f ' + ' '.join(( '/'.join([index_list[i] for index_list in included_lists]) for i in range(len(self.vertex_indices)) ))
        return face_obj_text

class ObjMesh:
    def __init__(self, mesh, object_name="Mesh"):
        self.object_name = object_name
        self.vertex_list = mesh.getVerticesPositions()
        self.uv_coord_list = mesh.getVerticesNormals()
        self.normals_list = mesh.getVerticesNormals()

        uv_indices = indices if self.uv_coord_list is not None else None
        normal_indices = indices if self.normals_list is not None else None

        self.faces_list = [ObjFace(indices, uv_indices, normal_indices) for indices in mesh.getFaces()]

    def getCommentObjText(self):
        return '#Generated in tile maker'

    def getObjectNameObjText(self):
        return 'o ' + str(self.object_name) if self.object_name is not None else ""

    def getVertexPositionObjText(self, vertex_pos):
        return 'v ' + ' '.join((str(axis_value) for axis_value in vertex_pos))

    def getVerticesPositionsObjText(self):
        if self.vertex_list is not None:
            return '\n'.join((self.getVertexPositionObjText(vertex_pos) for vertex_pos in self.vertex_list))
        return ''

    def getVertexUVCoordObjText(self, vertex_uv):
        return 'vt ' + ' '.join((str(axis_value) for axis_value in vertex_uv))

    def getVerticesUVCoordsObjText(self):
        if self.uv_coord_list is not None:
            return '\n'.join((self.getVertexUVCoordObjText(vertex_uv) for vertex_uv in self.uv_coord_list))
        return ''

    def getVertexNormalObjText(self, vertex_normal):
        return 'vn ' + ' '.join((str(axis_value) for axis_value in vertex_normal))

    def getVerticesNormalsObjText(self):
        if self.normals_list is not None:
            return '\n'.join((self.getVertexNormalObjText(vertex_normal) for vertex_normal in self.normals_list))
        return ''

    def getFacesObjText(self):
        if self.faces_list is not None:
            return '\n'.join((face.getObjText() for face in self.faces_list))
        return ''

    def getObjText(self):
        comment_text = self.getCommentObjText()
        object_name_text = self.getObjectNameObjText()
        vertices_positions_text = self.getVerticesPositionsObjText()
        vertices_uv_coordinates_text = self.getVerticesUVCoordsObjText()
        vertices_normals_text = self.getVerticesNormalsObjText()
        faces_text = self.getFacesObjText()

        return '\n'.join((comment_text, object_name_text,
            vertices_positions_text, vertices_uv_coordinates_text,
            vertices_normals_text, faces_text))

    def save(self, path):
        f = open(path, 'w')
        f.write(self.getObjText())
        f.close()

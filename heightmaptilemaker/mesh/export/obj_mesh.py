from pathlib import PurePath

class ObjMaterial:
    def __init__(self, texture_path=None):
        self.name = 'MapTexture'
        self.texture_path = PurePath(texture_path).name if texture_path is not None else None

    def getName(self):
        return self.name

    def getMtlText(self):
        material_name_text = self.__getMaterialNameText()
        color_text = self.__getColorText()
        texture_text = self.__getTextureText()

        return '\n'.join((material_name_text, color_text, texture_text))

    def __getMaterialNameText(self):
        return 'newmtl ' + self.getName()

    def __getColorText(self):
        ka_text = 'Ka 1.000 1.000 1.000'
        kd_text = 'Kd 1.000 1.000 1.000'
        ks_text = 'Ks 0.000 0.000 0.000'
        return '\n'.join((ka_text, kd_text, ks_text))

    def __getTextureText(self):
        map_ka_text = 'map_Ka ' + str(self.texture_path) if self.texture_path is not None else ''
        map_kd_text = 'map_Kd ' + str(self.texture_path) if self.texture_path is not None else ''

        return '\n'.join((map_ka_text, map_kd_text))

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
    def __init__(self, mesh, object_name="Mesh", texture_path=None):
        self.object_name = object_name
        self.vertex_list = [(vertex[0], vertex[2], vertex[1]) for vertex in mesh.getVerticesPositions()]
        self.uv_coord_list = mesh.getVerticesUVCoords()
        self.normals_list = mesh.getVerticesNormals()

        has_uv = len(self.uv_coord_list) > 0
        has_normals = len(self.normals_list) > 0

        self.faces_list = [ObjFace(indices, indices if has_uv else None, indices if has_normals else None) for indices in mesh.getFaces()]
        self.material = ObjMaterial(texture_path=texture_path)

    def getCommentObjText(self):
        return '#Generated in tile maker'

    def getObjectNameObjText(self):
        return 'o ' + str(self.object_name) if self.object_name is not None else ""

    def getMaterialsText(self, mat_file_name):
        if mat_file_name is not None:
            return '\n'.join(('mtllib ' + str(mat_file_name), 'usemtl ' + self.material.getName()))
        return ''

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

    def getObjText(self, mat_file_name=None):
        comment_text = self.getCommentObjText()
        object_name_text = self.getObjectNameObjText()
        materials_text = self.getMaterialsText(mat_file_name)
        vertices_positions_text = self.getVerticesPositionsObjText()
        vertices_uv_coordinates_text = self.getVerticesUVCoordsObjText()
        vertices_normals_text = self.getVerticesNormalsObjText()
        faces_text = self.getFacesObjText()

        return '\n'.join((comment_text, object_name_text, materials_text,
            vertices_positions_text, vertices_uv_coordinates_text,
            vertices_normals_text, faces_text))

    def getMaterialPathFromObjPath(self, obj_file_path):
        return obj_file_path + '.mtl'

    def getRelativeMaterialPath(self, obj_file_path):
        full_path = self.getMaterialPathFromObjPath(obj_file_path)
        file_name = PurePath(full_path).name
        return file_name

    def save(self, path):
        obj_text = self.getObjText(mat_file_name=self.getRelativeMaterialPath(path))
        f = open(path, 'w')
        f.write(obj_text)
        f.close()

        mtl_text = self.material.getMtlText()
        f = open(self.getMaterialPathFromObjPath(path), 'w')
        f.write(mtl_text)
        f.close()

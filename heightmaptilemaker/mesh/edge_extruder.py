from .mesh import MeshFace, MeshVertex

class IndexEdge:
    def __init__(self, first_index, second_index):
        self.from_index = first_index
        self.to_index = second_index

    def __hash__(self):
        min_index = min(self.from_index, self.to_index)
        max_index = max(self.from_index, self.to_index)
        return hash((min_index, max_index))

    def __eq__(self, other):
        forward_equal = self.from_index == other.from_index and self.to_index == other.to_index
        reverse_equal = self.to_index == other.from_index and self.from_index == other.to_index
        return forward_equal or reverse_equal

    def __str__(self):
        return str(self.from_index) + ":" + str(self.to_index)

class EdgeExtruder:
    def __init__(self, thickness):
        self.thickness = thickness

    def extrudeMesh(self, mesh):
        print('Finding boundary edges')
        index_edges = self.__getBoundaryEdges(mesh)
        print('Extruding edges')
        self.__extrudeEdges(index_edges, mesh)

        return mesh

    def __getBoundaryEdges(self, mesh):
        edges = {}
        for face in mesh.faces:
            for i in range(len(face.indices)):
                edge = IndexEdge(face.indices[i], face.indices[(i + 1) % len(face.indices)])

                if edge in edges:
                    edges[edge] += 1
                else:
                    edges[edge] = 1

        boundary_edges = [key for (key, item) in edges.items() if item == 1]
        return boundary_edges

    def __extrudeEdges(self, index_edges, mesh):
        print('Adding vertices')
        vertex_index_map = {}
        for index_edge in index_edges:
            if index_edge.from_index not in vertex_index_map:
                new_vertex_index = self.__addVertexFromIndex(index_edge.from_index, mesh)
                vertex_index_map[index_edge.from_index] = new_vertex_index
            if index_edge.to_index not in vertex_index_map:
                new_vertex_index = self.__addVertexFromIndex(index_edge.to_index, mesh)
                vertex_index_map[index_edge.to_index] = new_vertex_index

        print('Computing centroid')
        bottom_center_vertex = self.__computeVertexIndexCentroid(list(vertex_index_map.values()), mesh)
        bottom_center_vertex_index = mesh.addVertex(MeshVertex(position=bottom_center_vertex))

        print('Adding faces')
        for index_edge in index_edges:
            quad_a = index_edge.from_index
            quad_b = index_edge.to_index
            quad_c = vertex_index_map[quad_a]
            quad_d = vertex_index_map[quad_b]

            mesh.addFace(MeshFace((quad_b, quad_a, quad_c)))
            mesh.addFace(MeshFace((quad_b, quad_c, quad_d)))
            mesh.addFace(MeshFace((quad_c, bottom_center_vertex_index, quad_d)))

    def __addVertexFromIndex(self, vertex_index, mesh):
        vertex = mesh.vertices[vertex_index]
        new_vertex = vertex.deepcopy()
        new_vertex.position[2] = -self.thickness
        new_index = mesh.addVertex(new_vertex)
        return new_index

    def __computeVertexIndexCentroid(self, vertex_indices, mesh):
        dim = max(len(mesh.vertices[index].position) for index in vertex_indices)
        centroid = [0 for i in range(dim)]

        for dim_index in range(dim):
            centroid[dim_index] += sum(mesh.vertices[index].position[dim_index] / len(vertex_indices) for index in vertex_indices if dim_index < len(mesh.vertices[index].position))

        return centroid

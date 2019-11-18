
class MeshDisplace:
    def __init__(self):
        pass

    def displaceMesh(self, mesh, displacement_map):
        self.mesh = mesh
        self.displacement_map = displacement_map

        for vertex in mesh.vertices:
            self.__displaceVertex(vertex)

    def __displaceVertex(self, vertex):
        x, y = (vertex.position[0], vertex.position[1])
        z = self.displacement_map.getDisplacementAt(x, y)
        vertex.position[2] = z


class UVProjector:
    def __init__(self):
        pass

    def topViewProject(self, mesh):
        for vertex in mesh.vertices:
            vertex.uv_coord = (vertex.position[0], 1 - vertex.position[1])

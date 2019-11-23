from progress.null_callback import NullCallback
from progress.progress import Progress

class MeshDisplace:
    def __init__(self):
        pass

    def displaceMesh(self, mesh, displacement_map, progress_callback=NullCallback()):
        self.mesh = mesh
        self.displacement_map = displacement_map

        for i, vertex in enumerate(mesh.vertices):
            progress_callback(Progress(i + 1, message='Displacing vertex', max_progress=len(mesh.vertices)))
            self.__displaceVertex(vertex)

    def __displaceVertex(self, vertex):
        x, y = (vertex.position[0], vertex.position[1])
        z = self.displacement_map.getDisplacementAt(x, y)
        vertex.position[2] = z

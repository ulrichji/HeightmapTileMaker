from . import mesh

import numpy as np

class HeightmapMesh(mesh.Mesh):
    def __init__(self, heightmap, pixel_size):
        super(HeightmapMesh, self).__init__()

        mesh_width = heightmap.getWidth() * pixel_size
        mesh_height = heightmap.getHeight() * pixel_size

        mesh_vertices = self._createMeshVerticesFromHeightmap(heightmap, mesh_width, mesh_height)
        mesh_faces = self._createMeshFacesFromHeightmap(heightmap)

        for vertex in mesh_vertices:
            self.addVertex(mesh.MeshVertex(position=list(vertex)))
        for face in mesh_faces:
            self.addFace(mesh.MeshFace(indices=face))

    def _createMeshVerticesFromHeightmap(self, heightmap, mesh_width, mesh_height):
        x_positions = np.linspace(0.0, mesh_width, num=heightmap.getWidth())
        y_positions = np.linspace(0.0, mesh_height, num=heightmap.getHeight())
        z_values = heightmap.getHeightmap()
        xv, yv = np.meshgrid(x_positions, y_positions)

        mesh_vertex_positions = np.dstack((xv, yv, z_values))
        return mesh_vertex_positions.reshape((heightmap.getWidth() * heightmap.getHeight(), 3))

    def _createMeshFacesFromHeightmap(self, heightmap):
        width = heightmap.getWidth()
        height = heightmap.getHeight()

        upper_left_tris = [(y*width + x, (y+1)*width + x, y * width + x + 1) for y in range(height-1) for x in range(width-1)]
        lower_right_tris = [((y+1)*width + x + 1, y*width + x + 1, (y+1)*width + x) for y in range(height-1) for x in range(width - 1)]

        all_faces = []
        all_faces.extend(upper_left_tris)
        all_faces.extend(lower_right_tris)

        return all_faces

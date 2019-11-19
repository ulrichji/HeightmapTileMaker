from mesh.mesh import Mesh
from mesh.edge_extruder import EdgeExtruder

if __name__ == '__main__':
    print('Loading mesh from file')
    mesh = Mesh().load('hexagon_tile.json')

    extruder = EdgeExtruder(thickness=0.1)
    print('Extruding mesh')
    extruder.extrudeMesh(mesh)

    print('Saving extruded tile')
    mesh.save('hexagon_extruded.json')

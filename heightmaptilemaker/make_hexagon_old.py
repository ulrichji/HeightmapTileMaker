from mesh import mesh, clipping

import math

def createHexagon():
    hex_radius = 0.5
    hex_center = (hex_radius, hex_radius)

    hexagon_width = hex_radius
    hexagon_height = (math.sqrt(3) / 2) * hex_radius
    hexagon_cross_width = (1 / 2) * hex_radius

    hexagon_vertices = [
        (hex_center[0] - hexagon_cross_width, hex_center[1] - hexagon_height),
        (hex_center[0] + hexagon_cross_width, hex_center[1] - hexagon_height),
        (hex_center[0] + hex_radius, hex_center[1]),
        (hex_center[0] + hexagon_cross_width, hex_center[1] + hexagon_height),
        (hex_center[0] - hexagon_cross_width, hex_center[1] + hexagon_height),
        (hex_center[0] - hex_radius, hex_center[1])
    ]

    polygon_mesh = mesh.Mesh()
    for vertex_2d in hexagon_vertices:
        polygon_mesh.addVertex(mesh.MeshVertex(position=(vertex_2d[0], vertex_2d[1], 0)))
    polygon_mesh.addFace(mesh.MeshFace([0, 1, 2, 3, 4, 5]))

    return polygon_mesh

def main():
    print('Loading mesh')
    heightmap_mesh = mesh.Mesh().load('kraktind_mesh.json')
    print('Creating hexagon')
    clip_polygon = createHexagon()

    print('Creating clipper')
    heightmap_clipper = clipping.GreinerHormannClipper(clip_polygon)
    print('Clipping mesh')
    clipped_heightmap = heightmap_clipper.clipMesh(heightmap_mesh)

    print('Saving clipped mesh')
    clipped_heightmap.save('kraktind_clipped_mesh.json')

if __name__ == '__main__':
    main()

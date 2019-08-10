from mesh import heightmap_mesh
from heightmap import heightmap

import argparse

if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser(description='Program will create a mesh from the provided numpy heightmap and pixel size')
    argument_parser.add_argument('heightmap', type=str, help='The numpy heightmap file to load. File is a 2D array of elevations (as created by the make_heightmap.py program).')
    argument_parser.add_argument('pixel_size', metavar='pixel-size', type=float, help='The width of each pixel. If running the make_heigtmap.py program, this is reported as the second and final GDAL transform parameter. This argument is used for scaling')
    argument_parser.add_argument('--mesh-size', type=float, default=1, help="The total width and height of the output mesh model")
    argument_parser.add_argument('--output', type=str, help='Specify the file of the result .obj file')
    arguments = argument_parser.parse_args()
    print(arguments)

    heightmap_path = arguments.heightmap
    pixel_size = arguments.pixel_size
    output_file = arguments.output
    mesh_size = arguments.mesh_size

    print("Loading heightmap from file")
    heightmap = heightmap.Heightmap().loadFromFile(heightmap_path)
    print("Creating mesh")
    mesh = heightmap_mesh.HeightmapMesh(heightmap, pixel_size)
    print("Validating mesh")
    print(mesh.validate())
    print("Scaling mesh")
    mesh.scale(mesh_size / (heightmap.getWidth() * pixel_size))

    if output_file is not None:
        print("Exporting .obj file to " + str(output_file))
        mesh.exportObj(output_file)

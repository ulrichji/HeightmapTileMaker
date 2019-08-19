from mesh.export import obj_mesh
from mesh import mesh

import argparse

if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser(description='Program will export mesh json to obj')
    argument_parser.add_argument('input_file', type=str, help='The mesh json file.')
    argument_parser.add_argument('output_file', type=str, help='The obj file to export to')
    argument_parser.add_argument('--object_name', default='mesh', metavar='object-name', type=str, help='The name of the object to store in the .obj file')
    arguments = argument_parser.parse_args()

    file_to_load = arguments.input_file
    export_file = arguments.output_file
    object_name = arguments.object_name

    print('Loading from ' + str(file_to_load))
    mesh = mesh.Mesh().load(file_to_load)

    print('Exporting to ' + str(export_file))
    obj_exporter = obj_mesh.ObjMesh(mesh=mesh, object_name=object_name)
    obj_exporter.save(export_file)

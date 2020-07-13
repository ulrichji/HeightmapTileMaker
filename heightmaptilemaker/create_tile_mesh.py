import argparse
import tile_creator

if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser(description='This program will create a 3D mesh of some terrain based on the input configuration.')
    argument_parser.add_argument('input_config', type=str, help='The configuration (see example_config.yaml).')
    argument_parser.add_argument('--output_file', type=str, help='The obj file to save the mesh')
    argument_parser.add_argument('--object_name', default='mesh', metavar='object-name', type=str, help='The name of the object to store in the .obj file')
    arguments = argument_parser.parse_args()

    tile_config = tile_creator.TileConfig(arguments.input_config)
    tile_creator.createTileFromTileConfig(tile_config)

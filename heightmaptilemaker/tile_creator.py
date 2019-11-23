from progress.progress import Progress
import progress.default_printer
import progress.callback

from mesh.generator import grid
from mesh.mesh_clipper import clipMesh, getHexagon
from mesh.mesh_displace import MeshDisplace
from mesh.edge_extruder import EdgeExtruder
from mesh.export import obj_mesh

from geo import geo_utils

from heightmap.heightmap_displacement_lookup import HeightmapDisplaceLookup

import yaml
import glob

class ConfigValueNotFound(Exception):
    def __init__(self, message, file_path):
        # Call the base class constructor with the parameters it needs
        super(ValidationError, self).__init__('A configuration value was not found in config file \"' + str(file_path) + '\" :' + message)

class YAMLFileParser:
    def __init__(self, filepath):
        with open(filepath, 'r') as yaml_file:
            yaml_document = yaml_file.read()
            self.yaml_content = yaml.load(yaml_document)

    def requiredValue(self, value_name, element=None):
        element = element or self.yaml_content

        if not value_name in element:
            raise ConfigValueNotFound(value_name)
        return element[value_name]

    def requiredValues(self, first_value, *args):
        current_element = self.requiredValue(first_value)
        for arg in args:
            current_element = self.requiredValue(arg, current_element)

        return current_element

    def optionalValue(self, value_name, default_value, element=None):
        element = element or self.yaml_content

        if not value_name in element:
            return default_value
        return element[value_name]


class TileConfig:
    def __init__(self, yaml_file_path):
        yaml_parser = YAMLFileParser(yaml_file_path)
        self.tiff_directory = yaml_parser.requiredValue('tiff-directory')
        self.geo_top_left_east = yaml_parser.requiredValues('geo-top-left', 'east')
        self.geo_top_left_north = yaml_parser.requiredValues('geo-top-left', 'north')
        self.geo_top_right_east = yaml_parser.requiredValues('geo-top-right', 'east')
        self.geo_top_right_north = yaml_parser.requiredValues('geo-top-right', 'north')
        self.geo_distance = yaml_parser.requiredValue('geo-distance')

        self.size = yaml_parser.optionalValue('size', 1)
        self.output_path = yaml_parser.optionalValue('output-path', None)
        self.mesh_resolution_x = yaml_parser.optionalValue('mesh-resolution-x', default_value=1024)
        self.mesh_resolution_y = yaml_parser.optionalValue('mesh-resolution-y', default_value=1024)
        self.tile_thickness = yaml_parser.optionalValue('tile_thickness', default_value=self.size/10)

        self.geo_top_left = (self.geo_top_left_east, self.geo_top_left_north)
        self.geo_top_right = (self.geo_top_right_east, self.geo_top_right_north)

    def __str__(self):
        return yaml.dump(self)

def findGeoTiffFiles(directory):
    return glob.glob(directory + "/*.tif")

def createTileFromTileConfig(tile_config):
    progress_printer = progress.default_printer.Printer()

    progress_printer(Progress(0.0, "Creating grid mesh " + str(tile_config.mesh_resolution_x) + "x" + str(tile_config.mesh_resolution_y)))
    grid_mesh = grid.generate((tile_config.mesh_resolution_x, tile_config.mesh_resolution_y))

    progress_printer(Progress(0.05, "Creating cut shape (default hexagon)"))
    tile_shape = getHexagon()

    mesh_clipper_callback = progress.callback.Callback(progress_printer, start_at=0.05, end_at=0.5, message='Carving tile shape')
    clipped_mesh = clipMesh(grid_mesh, tile_shape, mesh_clipper_callback)

    progress_printer(Progress(0.51, "Computing geo transform"))
    geo_transform = geo_utils.computeGdalGeoTransformFrom2Points(
        tile_config.geo_top_left, tile_config.geo_top_right, (1, 1))

    progress_printer(Progress(0.55, "Loading geotiff files"))
    displacement_lookup = HeightmapDisplaceLookup(
        findGeoTiffFiles(tile_config.tiff_directory),
        geo_transform.transform_parameters,
        1/tile_config.geo_distance)

    mesh_displace_callback = progress.callback.Callback(progress_printer, start_at=0.60, end_at=0.89, message='Computing tile displacement')
    MeshDisplace().displaceMesh(clipped_mesh, displacement_lookup, mesh_displace_callback)

    progress_printer(Progress(0.9, 'Scaling mesh'))
    clipped_mesh.scale(tile_config.size)

    progress_printer(Progress(0.93, 'Extruding tile edges'))
    extruder = EdgeExtruder(thickness=tile_config.tile_thickness)
    extruder.extrudeMesh(clipped_mesh)

    progress_printer(Progress(0.97, 'Converting to obj'))
    obj_exporter = obj_mesh.ObjMesh(mesh=clipped_mesh, object_name='Heightmap tile')
    obj_exporter.save(tile_config.output_path)

    progress_printer.finish()

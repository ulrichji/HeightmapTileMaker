from progress.progress import Progress
import progress.default_printer
import progress.callback

from mesh.generator import grid
from mesh.mesh_clipper import clipMesh, getHexagon
from mesh.mesh_displace import MeshDisplace
from mesh.edge_extruder import EdgeExtruder
from mesh.export import obj_mesh
from mesh.uv_projection import UVProjector

from geo import geo_utils
from geo import geotiff_raster
from geo import raster_lookup
from geo import image_creator
from geo import image_raster

from heightmap.heightmap_displacement_lookup import HeightmapDisplaceLookup

from PIL import Image

import yaml
import glob

class ConfigValueNotFound(Exception):
    def __init__(self, message, file_path):
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

    def optionalValues(self, default_value, first_value, *args):
        current_element = self.optionalValue(first_value, None)
        for arg in args:
            if current_element is None:
                return default_value
            current_element = self.optionalValue(arg, None, current_element)

        return current_element or default_value


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
        self.tile_thickness = yaml_parser.optionalValue('tile-thickness', default_value=self.size/10)
        self.elevation_multiplier = yaml_parser.optionalValue('elevation-multiplier', default_value=1.0)

        self.texture_path = yaml_parser.optionalValues(None, 'texture', 'path')
        self.texture_result_path = yaml_parser.optionalValues(None, 'texture', 'result-path')
        self.texture_geo_top_left_east = yaml_parser.optionalValues(None, 'texture', 'geo-top-left', 'east')
        self.texture_geo_top_left_north = yaml_parser.optionalValues(None, 'texture', 'geo-top-left', 'north')
        self.texture_geo_top_right_east = yaml_parser.optionalValues(None, 'texture', 'geo-top-right', 'east')
        self.texture_geo_top_right_north = yaml_parser.optionalValues(None, 'texture', 'geo-top-right', 'north')
        self.texture_resolution_x = yaml_parser.optionalValues(512, 'texture', 'resolution-x')
        self.texture_resolution_y = yaml_parser.optionalValues(512, 'texture', 'resolution-y')

        self.geo_top_left = (self.geo_top_left_east, self.geo_top_left_north)
        self.geo_top_right = (self.geo_top_right_east, self.geo_top_right_north)
        self.texture_geo_top_left = (self.texture_geo_top_left_east, self.texture_geo_top_left_north)
        self.texture_geo_top_right = (self.texture_geo_top_right_east, self.texture_geo_top_right_north)

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
    raster_files = geotiff_raster.createRastersFromFiles(findGeoTiffFiles(tile_config.tiff_directory))
    heightmap_raster = raster_lookup.MultiGeoRaster(raster_files)
    elevation_multiplier = tile_config.elevation_multiplier * (1 / tile_config.geo_distance)
    displacement_lookup = HeightmapDisplaceLookup(
        heightmap_raster,
        geo_transform,
        elevation_multiplier)

    mesh_displace_callback = progress.callback.Callback(progress_printer, start_at=0.60, end_at=0.89, message='Computing tile displacement')
    MeshDisplace().displaceMesh(clipped_mesh, displacement_lookup, mesh_displace_callback)

    progress_printer(Progress(0.501, "Creating uv coordinates"))
    UVProjector().topViewProject(clipped_mesh)

    progress_printer(Progress(0.8999, 'Creating texture'))
    input_texture_image = Image.open(tile_config.texture_path)
    output_texture_image = Image.new('RGB', (tile_config.texture_resolution_x, tile_config.texture_resolution_y))

    input_image_geo_transform = geo_utils.computeGdalGeoTransformFrom2Points(tile_config.texture_geo_top_left, tile_config.texture_geo_top_right, input_texture_image.size)
    output_texture_geo_transform = geo_utils.computeGdalGeoTransformFrom2Points(tile_config.geo_top_left, tile_config.geo_top_right, output_texture_image.size)

    output_texture = image_raster.ImageRaster(output_texture_image, output_texture_geo_transform)
    input_texture = image_raster.ImageRaster(input_texture_image, input_image_geo_transform)
    image_maker = image_creator.ImageCreator(input_texture, output_texture)
    progress_printer(Progress(0.8999, 'Creating image'))
    image_maker.createImage()
    output_texture_image.save(tile_config.texture_result_path)

    progress_printer(Progress(0.9, 'Scaling mesh'))
    clipped_mesh.scale(tile_config.size)

    progress_printer(Progress(0.93, 'Extruding tile edges'))
    extruder = EdgeExtruder(thickness=tile_config.tile_thickness)
    extruder.extrudeMesh(clipped_mesh)

    progress_printer(Progress(0.97, 'Converting to obj'))
    obj_exporter = obj_mesh.ObjMesh(mesh=clipped_mesh, object_name='Heightmap tile', texture_path=tile_config.texture_result_path)
    obj_exporter.save(tile_config.output_path)

    progress_printer.finish()

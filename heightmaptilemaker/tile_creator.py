import yaml

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

    def __str__(self):
        return yaml.dump(self)

from .top_level_modifier import TopLevelModifier
from .min_modifier import MinModifier
from .cone_modifier import ConeModifier
from .cube_frustum_modifier import CubeFrustumModifier
from .average_circle_modifier import AverageCircleModifier

import math

def createModifierByType(modifier_type, params):
    if modifier_type == 'min':
        return MinModifier()
    if modifier_type == 'average-circle':
        if ('center' not in params or
            'x' not in params['center'] or 'y' not in params['center'] or 
            'radius' not in params or 'angle-deg' not in params):
            raise Exception('Center points x, y, radius and angle are required for creating a average-circle modifier. Got: ' + str(params))
        return AverageCircleModifier(
            center=(float(params['center']['x']),
                    float(params['center']['y'])),
            radius=float(params['radius']),
            angle_deg=float(params['angle-deg']))
    if modifier_type == 'cone':
        if ('center' not in params or
            'x' not in params['center'] or 'y' not in params['center'] or 'z' not in params['center'] or
            'base-radius' not in params or 'top-radius' not in params or 'height' not in params):
            raise Exception('Center points x, y and z, base-radius, top-radius and height are required for creating a cone. Got: ' + str(params))
        return ConeModifier(
            center=(float(params['center']['x']),
                    float(params['center']['y']),
                    float(params['center']['z'])),
            base_radius=float(params['base-radius']),
            top_radius=float(params['top-radius']),
            height=float(params['height']))
    if modifier_type == 'cube-frustum':
        if ('center' not in params or
            'x' not in params['center'] or 'y' not in params['center'] or 'z' not in params['center'] or
            'rotation' not in params or 'height' not in params or
            'bottom' not in params or 'width' not in params['bottom'] or 'height' not in params['bottom'] or
            'top' not in params or 'width' not in params['top'] or 'height' not in params['top']):
            raise Exception('Center, rotation, height, bottom-width, bottom-height, top-width and top-height are required for creating a frustum cube. Got: ' + str(params))
        return CubeFrustumModifier(
            center=(float(params['center']['x']),
                    float(params['center']['y']),
                    float(params['center']['z'])),
            rotation=float(params['rotation'] * (math.pi / 180)),
            height=float(params['height']),
            bottom_dimensions=(float(params['bottom']['width']),
                               float(params['bottom']['height'])),
            top_dimensions=(float(params['top']['width']),
                            float(params['top']['height'])))

    raise Exception("Unknown modifier: " + str(modifier_type))

def createModifiersFromObjects(modifiers_list_of_dicts):
    generated_modifiers = []
    for modifier_dict in modifiers_list_of_dicts:
        if len(modifier_dict.keys()) != 1:
            raise Exception("A single value should be used as modifier type identificator. Found: " + str(modifier_dict.keys()))
        modifier_type = next(iter(modifier_dict.keys()))
        modifier = createModifierByType(modifier_type, modifier_dict[modifier_type])
        if(modifier.supports_sub_modifiers()):
            sub_modifiers = createModifiersFromObjects(modifier_dict[modifier_type])
            modifier.add_submodifiers(sub_modifiers)
        generated_modifiers.append(modifier)
    
    return generated_modifiers

def setupModifiersFromParameters(modifiers_list_of_dicts):
    return TopLevelModifier(createModifiersFromObjects(modifiers_list_of_dicts))

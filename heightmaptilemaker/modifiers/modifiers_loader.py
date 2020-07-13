from .top_level_modifier import TopLevelModifier
from .min_modifier import MinModifier
from .cone_modifier import ConeModifier

def createModifierByType(modifier_type, params):
    if modifier_type == 'min':
        return MinModifier()
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
            height=float(params['height'])
        )

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

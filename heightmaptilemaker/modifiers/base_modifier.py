class BaseModifier:
    def __init__(self, supports_sub_modifiers):
        self.__supports_sub_modifiers = supports_sub_modifiers

    def supports_sub_modifiers(self):
        return self.__supports_sub_modifiers
    
    def initialize_by_vertex(self, vertex):
        pass

    def modify_vertex(self, vertex):
        raise Exception('modify_vertex must be overridden by subtypes')
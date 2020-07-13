from .base_modifier import BaseModifier

class MinModifier(BaseModifier):
    def __init__(self):
        super().__init__(supports_sub_modifiers=True)
        self.sub_modifiers = []

    def add_submodifiers(self, sub_modifiers):
        self.sub_modifiers.extend(sub_modifiers)

    def modify_vertex(self, vertex):
        min_vertex = vertex
        for sub_modifier in self.sub_modifiers:
            vertex_copy = vertex.deepcopy()
            sub_modifier.modify_vertex(vertex_copy)
            if vertex_copy.position[2] < min_vertex.position[2]:
                min_vertex = vertex_copy
        
        vertex.set_from(min_vertex)

class TopLevelModifier:
    def __init__(self, modifiers_list):
        self.modifiers_list = modifiers_list

    def apply_modifiers_to_mesh(self, mesh):
        for vertex in mesh.getVertices():
            for mod in self.modifiers_list:
                mod.modify_vertex(vertex)

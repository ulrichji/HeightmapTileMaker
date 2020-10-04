from .base_modifier import BaseModifier

import math

class ConeModifier(BaseModifier):
    def __init__(self, center, base_radius, top_radius, height):
        super().__init__(supports_sub_modifiers=False)
        self.center=center
        self.base_radius=base_radius
        self.top_radius=top_radius
        self.height=height
    
    def modify_vertex(self, vertex):
        x_diff = vertex.position[0] - self.center[0]
        y_diff = vertex.position[1] - self.center[1]
        distance_to_center = math.sqrt((x_diff*x_diff) + (y_diff*y_diff))

        slant_relative_height = (None if distance_to_center >= self.top_radius and distance_to_center >= self.base_radius else
                                 (1 if self.top_radius <= self.base_radius else 0) if distance_to_center <= self.top_radius and distance_to_center <= self.base_radius else
                                 (distance_to_center - self.base_radius) / (self.top_radius - self.base_radius))

        if slant_relative_height is None:
            return

        height_from_base = slant_relative_height * self.height
        new_vertex_z = height_from_base + self.center[2]
        vertex.position = [vertex.position[0], vertex.position[1], new_vertex_z]

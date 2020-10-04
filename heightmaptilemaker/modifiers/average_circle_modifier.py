from .base_modifier import BaseModifier

import math

class AverageCircleModifier(BaseModifier):
    def __init__(self, center, radius, angle_deg):
        super().__init__(supports_sub_modifiers=False)
        self.center=center
        self.radius = radius
        self.angle_deg = angle_deg

        self.__height_sum=0
        self.__height_count=0
    
    def height(self):
        if self.__height_count == 0:
            return None
        
        return self.__height_sum / self.__height_count

    def initialize_by_vertex(self, vertex):
        x_diff = vertex.position[0] - self.center[0]
        y_diff = vertex.position[1] - self.center[1]
        distance_to_center = math.sqrt((x_diff*x_diff) + (y_diff*y_diff))

        if distance_to_center <= self.radius:
            self.__height_sum += vertex.position[2]
            self.__height_count += 1

    def modify_vertex(self, vertex):
        angle_rads = math.pi * (self.angle_deg / 180.0)
        height = self.height()

        x_diff = vertex.position[0] - self.center[0]
        y_diff = vertex.position[1] - self.center[1]
        z_diff = vertex.position[2] - height
        distance_to_center = math.sqrt((x_diff*x_diff) + (y_diff*y_diff))

        distance_from_circle = distance_to_center - self.radius
        min_clamp = min(height, height - (distance_from_circle * math.tan(angle_rads)))
        max_clamp = max(height, height + (distance_from_circle * math.tan(angle_rads)))
        
        new_vertex_z = (min_clamp if vertex.position[2] < min_clamp
                   else max_clamp if vertex.position[2] > max_clamp
                   else vertex.position[2])

        vertex.position = [vertex.position[0], vertex.position[1], new_vertex_z]

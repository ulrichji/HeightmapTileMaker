from .base_modifier import BaseModifier

import math

def rotated_point(point, angle):
    costheta = math.cos(angle)
    sintheta = math.sin(angle)

    new_x = (point[0] * costheta) - (point[1] * sintheta)
    new_y = (point[0] * sintheta) + (point[1] * costheta)

    if len(point) > 2:
        return tuple((new_x, new_y, *(point[i] for i in range(2,len(point)))))
    return (new_x, new_y)

def translated_point(point, translation):
    return tuple((point[i] + translation[i] for i in range(min(len(point), len(translation)))))

class Line:
    def __init__(self, from_point, to_point, rotation=0, translation=None):
        if translation is None:
            translation = tuple((0 for i in range(len(from_point))))

        transformed_from_point = translated_point(rotated_point(from_point, rotation), translation)
        transformed_to_point = translated_point(rotated_point(to_point, rotation), translation)

        diff = tuple(transformed_to_point[i] - transformed_from_point[i] for i in range(min(len(transformed_to_point), len(transformed_from_point))))

        self.length = math.sqrt(sum(d**2 for d in diff))
        self.direction = tuple(d / self.length for d in diff)
        self.start = tuple(p for p in transformed_from_point)

    def get_end_point(self):
        return tuple(self.start[i] + (self.length * self.direction[i]) for i in range(min(len(self.start), len(self.direction))))

    # Based on cross-product rule: Right is positive, and left is negative, on line is 0
    def compute_side(self, point):
        end = self.get_end_point()

        if len(self.start) < 2 or len(end) < 2:
            raise Exception("Unable to compute side of line with less than 2 coordinates")
        
        side_value = (((end[1] - self.start[1]) * point[0])
                    - ((end[0] - self.start[0]) * point[1])
                    + (end[0] * self.start[1])
                    - (end[1] * self.start[0]))
        
        return side_value

    def compute_signed_distance_to_point(self, point):
        start_to_point = tuple(point[i] - self.start[i] for i in range(min(len(self.start), len(point))))
        projected_length = sum(start_to_point[i] * self.direction[i] for i in range(min(len(start_to_point), len(self.direction))))

        closest_point = tuple(self.start[i] + (self.direction[i] * projected_length) for i in range(min(len(self.start), len(self.direction))))
        if projected_length < 0:
            closest_point = tuple(p for p in self.start)
        elif projected_length > self.length:
            closest_point = self.get_end_point()
        
        distance = math.sqrt(sum((closest_point[i] - point[i])**2 for i in range(min(len(closest_point), len(point)))))
        side_of_line = 1 if self.compute_side(point) > 0 else -1 if self.compute_side(point) < 0 else 0

        return distance * side_of_line

class CubeFrustumModifier(BaseModifier):
    def __init__(self, center, rotation, height, bottom_dimensions, top_dimensions):
        super().__init__(supports_sub_modifiers=False)
        self.center = center
        self.height = height
        self.bottom_lines = [
            Line(from_point=(-bottom_dimensions[0]/2, -bottom_dimensions[1]/2),
                 to_point=(-bottom_dimensions[0]/2, bottom_dimensions[1]/2),
                 rotation=rotation,
                 translation=center),
            Line(from_point=(-bottom_dimensions[0]/2, bottom_dimensions[1]/2),
                 to_point=(bottom_dimensions[0]/2, bottom_dimensions[1]/2),
                 rotation=rotation,
                 translation=center),
            Line(from_point=(bottom_dimensions[0]/2, bottom_dimensions[1]/2),
                 to_point=(bottom_dimensions[0]/2, -bottom_dimensions[1]/2),
                 rotation=rotation,
                 translation=center),
            Line(from_point=(bottom_dimensions[0]/2, -bottom_dimensions[1]/2),
                 to_point=(-bottom_dimensions[0]/2, -bottom_dimensions[1]/2),
                 rotation=rotation,
                 translation=center)]
        self.top_lines = [
            Line(from_point=(-top_dimensions[0]/2, -top_dimensions[1]/2),
                 to_point=(-top_dimensions[0]/2, top_dimensions[1]/2),
                 rotation=rotation,
                 translation=center),
            Line(from_point=(-top_dimensions[0]/2, top_dimensions[1]/2),
                 to_point=(top_dimensions[0]/2, top_dimensions[1]/2),
                 rotation=rotation,
                 translation=center),
            Line(from_point=(top_dimensions[0]/2, top_dimensions[1]/2),
                 to_point=(top_dimensions[0]/2, -top_dimensions[1]/2),
                 rotation=rotation,
                 translation=center),
            Line(from_point=(top_dimensions[0]/2, -top_dimensions[1]/2),
                 to_point=(-top_dimensions[0]/2, -top_dimensions[1]/2),
                 rotation=rotation,
                 translation=center)]
    
    def __point_inside_right_winded_shape(self, point, shape_lines):
        return all(0 <= line.compute_signed_distance_to_point(point) for line in shape_lines)

    def __signed_distance_to_right_winded_shape(self, point, shape_lines):
        if self.__point_inside_right_winded_shape(point, shape_lines):
            # All distances are positive, so return the smallest
            return min(line.compute_signed_distance_to_point(point) for line in shape_lines)
        else:
            # Only negative values are valid, so discard positive values
            return max(line.compute_signed_distance_to_point(point) for line in shape_lines 
                        if 0 >= line.compute_signed_distance_to_point(point))

    def modify_vertex(self, vertex):
        if len(vertex.position) < 3 or len(self.center) < 3:
            raise Exception('Unable to modify height of vertex/center with less than 3 dimenions')

        is_inside_bottom = self.__point_inside_right_winded_shape(vertex.position, self.bottom_lines)
        is_inside_top = self.__point_inside_right_winded_shape(vertex.position, self.top_lines)

        if not is_inside_bottom and not is_inside_top:
            pass
        else:
            distance_to_bottom = self.__signed_distance_to_right_winded_shape(vertex.position, self.bottom_lines)
            distance_to_top = self.__signed_distance_to_right_winded_shape(vertex.position, self.top_lines)

            if is_inside_bottom and is_inside_top:
                if distance_to_bottom < distance_to_top:
                    vertex.position[2] = self.center[2]
                else:
                    vertex.position[2] = self.center[2] + self.height
            else:
                ramp_height = self.height * (abs(distance_to_bottom) / (abs(distance_to_bottom) + abs(distance_to_top)))
                vertex.position[2] = self.center[2] + ramp_height

import struct

from .transform import GeoTransform

def rawRasterToFloat(raw_raster, number_of_floats):
    return struct.unpack('f' * number_of_floats, raw_raster)

def computeGdalGeoTransformFrom3Points(points_list, heightmap_size):
    g0 = points_list[0][0]
    g1 = (points_list[2][0] - points_list[0][0]) / heightmap_size[0]
    g2 = (points_list[1][0] - points_list[0][0]) / heightmap_size[1]
    g3 = points_list[0][1]
    g4 = (points_list[2][1] - points_list[0][1]) / heightmap_size[0]
    g5 = (points_list[1][1] - points_list[0][1]) / heightmap_size[1]

    return GeoTransform((g0, g1, g2, g3, g4, g5))

def computeGdalGeoTransformFrom2Points(upper_left_point, upper_right_point, heightmap_size):
    aspect_ratio =  heightmap_size[1] / heightmap_size[0]
    left_to_right_dist = (upper_right_point[0] - upper_left_point[0], upper_right_point[1] - upper_left_point[1])
    translation_vector = (left_to_right_dist[0] * aspect_ratio, left_to_right_dist[1] * aspect_ratio)
    translation_vector_rotated = (translation_vector[1], -translation_vector[0])
    point_rotated = (upper_left_point[0] + translation_vector_rotated[0], upper_left_point[1] + translation_vector_rotated[1])

    return computeGdalGeoTransformFrom3Points((upper_left_point, point_rotated, upper_right_point), heightmap_size)

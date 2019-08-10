import struct

def xyIndexToCoordinate(xy_index_pair, geo_transform):
    x_index = xy_index_pair[0]
    y_index = xy_index_pair[1]
    return ( geo_transform[0] + x_index * geo_transform[1] + y_index * geo_transform[2],
             geo_transform[3] + x_index * geo_transform[4] + y_index * geo_transform[5])

def coordinateToXYIndex(coordinate_pair, geo_transform):
    geo_x = coordinate_pair[0]
    geo_y = coordinate_pair[1]

    g0,g1,g2,g3,g4,g5 = geo_transform

    return ((geo_x*g5 - geo_y*g2 - g0*g5 + g3*g2) / (g1*g5 - g4*g2),
            (geo_y*g1 - geo_x*g4 - g3*g1 + g0*g4) / (g5*g1 - g2*g4))

def rawRasterToFloat(raw_raster, number_of_floats):
    return struct.unpack('f' * number_of_floats, raw_raster)

class GdalGeoTransform:
    def __init__(self, gdal_geo_transform):
        self.transform_parameters = gdal_geo_transform

    def transformGeoLocationToPixelLocation(self, geo_x, geo_y):
        return coordinateToXYIndex((geo_x, geo_y), self.transform_parameters)

    def transformPixelLocationToGeoLocation(self, pixel_x, pixel_y):
        return xyIndexToCoordinate((pixel_x, pixel_y), self.transform_parameters)

def computeGdalGeoTransformFrom3Points(points_list, heightmap_size):
    g0 = points_list[0][0]
    g1 = (points_list[2][0] - points_list[0][0]) / heightmap_size[0]
    g2 = (points_list[1][0] - points_list[0][0]) / heightmap_size[1]
    g3 = points_list[0][1]
    g4 = (points_list[2][1] - points_list[0][1]) / heightmap_size[0]
    g5 = (points_list[1][1] - points_list[0][1]) / heightmap_size[1]

    return GdalGeoTransform((g0, g1, g2, g3, g4, g5))

def computeGdalGeoTransformFrom2Points(upper_left_point, upper_right_point, heightmap_size):
    aspect_ratio =  heightmap_size[1] / heightmap_size[0]
    left_to_right_dist = (upper_right_point[0] - upper_left_point[0], upper_right_point[1] - upper_left_point[1])
    translation_vector = (left_to_right_dist[0] * aspect_ratio, left_to_right_dist[1] * aspect_ratio)
    translation_vector_rotated = (translation_vector[1], -translation_vector[0])
    point_rotated = (upper_left_point[0] + translation_vector_rotated[0], upper_left_point[1] + translation_vector_rotated[1])

    return computeGdalGeoTransformFrom3Points((upper_left_point, point_rotated, upper_right_point), heightmap_size)

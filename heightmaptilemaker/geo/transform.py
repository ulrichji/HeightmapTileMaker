class Transform:
    def transformGeoLocationToPixelLocation(self, geo_x, geo_y):
        ...

    def transformPixelLocationToGeoLocation(self, pixel_x, pixel_y):
        ...

class GeoTransform(Transform):
    def __init__(self, transform_parameters):
        self.transform_parameters = transform_parameters

    def transformGeoLocationToPixelLocation(self, geo_x, geo_y):
        return self.__coordinateToXYIndex(geo_x, geo_y)

    def transformPixelLocationToGeoLocation(self, pixel_x, pixel_y):
        return self.__xyIndexToCoordinate(pixel_x, pixel_y)

    def __xyIndexToCoordinate(self, pixel_x, pixel_y):
        g0,g1,g2,g3,g4,g5 = self.transform_parameters

        return ( g0 + pixel_x * g1 + pixel_y * g2,
                 g3 + pixel_x * g4 + pixel_y * g5)

    def __coordinateToXYIndex(self, geo_x, geo_y):
        g0,g1,g2,g3,g4,g5 = self.transform_parameters

        return ((geo_x*g5 - geo_y*g2 - g0*g5 + g3*g2) / (g1*g5 - g4*g2),
                (geo_y*g1 - geo_x*g4 - g3*g1 + g0*g4) / (g5*g1 - g2*g4))

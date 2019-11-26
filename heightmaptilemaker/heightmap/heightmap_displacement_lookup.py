from geo.raster_lookup import MultiGeoRaster
from geo import geotiff_raster
from geo import geo_utils

class HeightmapDisplaceLookup:
    def __init__(self, raster_lookup, geo_transform, height_scaledown):
        self.raster_lookup = raster_lookup
        self.geo_transform = geo_transform
        self.height_scaledown = height_scaledown

    def getDisplacementAt(self, x, y):
        geo_x, geo_y = geo_utils.xyIndexToCoordinate((x, y), self.geo_transform)
        displacement = self.raster_lookup.getValueAtPosition(geo_x, geo_y) or 0.0
        displacement_scaled = displacement * self.height_scaledown

        return displacement_scaled

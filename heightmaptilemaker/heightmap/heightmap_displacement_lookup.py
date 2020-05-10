from geo.raster_lookup import MultiGeoRaster
from geo import geotiff_raster
from geo import geo_utils

class HeightmapDisplaceLookup:
    def __init__(self, raster_lookup, geo_transform, height_scale):
        self.raster_lookup = raster_lookup
        self.geo_transform = geo_transform
        self.height_scale = height_scale

    def getDisplacementAt(self, x, y):
        geo_x, geo_y = self.geo_transform.transformPixelLocationToGeoLocation(x, y)
        displacement = self.raster_lookup.getValueAtPosition(geo_x, geo_y) or 0.0
        displacement_scaled = displacement * self.height_scale

        return displacement_scaled

from geo.raster_lookup import RasterLookup
from geo import geo_utils

class HeightmapDisplaceLookup:
    def __init__(self, heightmap_files, geo_transform, height_scaledown):
        self.raster_lookup = RasterLookup(heightmap_files, nodata_value=0)
        self.geo_transform = geo_transform
        self.height_scaledown = height_scaledown

    def getDisplacementAt(self, x, y):
        geo_x, geo_y = geo_utils.xyIndexToCoordinate((x, y), self.geo_transform)
        displacement = self.raster_lookup.getElevationAtPosition(geo_x, geo_y)
        displacement_scaled = displacement * self.height_scaledown

        return displacement_scaled

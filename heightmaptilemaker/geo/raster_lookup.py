from . import geo_utils

class GeoRaster:
    def __init__(self, raster_grid):
        self.raster_grid = raster_grid
        self.raster_shape = raster_grid.getRasterShape()
        self.geo_transform = raster_grid.getGeoTransform()

    def getValueAtPosition(self, geo_x, geo_y):
        pixel_x, pixel_y = self.geo_transform.transformGeoLocationToPixelLocation(geo_x, geo_y)
        return self._getPixelAtLocation(pixel_x, pixel_y)


    def _getPixelAtLocation(self, pixel_x, pixel_y):
        if self._locationInBounds(pixel_x, pixel_y):
            return self.raster_grid.getValueAt(pixel_x, pixel_y)
        return None

    def _locationInBounds(self, pixel_x, pixel_y):
        raster_width = self.raster_shape[0]
        raster_height = self.raster_shape[1]

        if pixel_x >= 0 and pixel_x < raster_width and pixel_y >= 0 and pixel_y < raster_height:
            return True
        return False

class MultiGeoRaster:
    def __init__(self, raster_grid_list):
        self.raster_list = [GeoRaster(raster) for raster in raster_grid_list]

    def getValueAtPosition(self, geo_x, geo_y):
        for raster in self.raster_list:
            raster_value = raster.getValueAtPosition(geo_x, geo_y)
            if raster_value is not None:
                return raster_value

        return None

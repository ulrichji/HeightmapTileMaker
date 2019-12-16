from . import geo_utils
from . import transform

import gdal

import glob
import struct

class RasterBandReader:
    def __init__(self, gdal_raster_band):
        self.gdal_raster_band = gdal_raster_band

    def readPixelAt(self, pixel_x, pixel_y):
        raw_elevation = self.gdal_raster_band.ReadRaster(xoff=pixel_x,
                                                         yoff=pixel_y,
                                                         xsize=1,
                                                         ysize=1,
                                                         buf_xsize=1,
                                                         buf_ysize=1,
                                                         buf_type=gdal.GDT_Float32)
        try:
            return geo_utils.rawRasterToFloat(raw_elevation, 1)[0]
        except struct.error as e:
            print(e)
            raise Exception("The following error occured when converting pixel (" +
                str(raw_elevation) + ")  at " + str(pixel_x) + " " + str(pixel_y) + ":\n" + str(e))

class GeotiffRasterBandBoundaries:
    def __init__(self, gdal_raster_band):
        self.width_pixels = gdal_raster_band.XSize
        self.height_pixels = gdal_raster_band.YSize

    def locationInBounds(self, pixel_x, pixel_y):
        if pixel_x >= 0 and pixel_x < self.width_pixels and pixel_y >= 0 and pixel_y < self.height_pixels:
            return True
        return False


class GeotiffRasterBand:
    def __init__(self, gdal_raster_band, geo_transform):
        self.geo_transform = transform.GeoTransform(geo_transform)
        self.boundaries = GeotiffRasterBandBoundaries(gdal_raster_band)
        self.raster_band_reader = RasterBandReader(gdal_raster_band)
        self.width = gdal_raster_band.XSize
        self.height = gdal_raster_band.YSize

    def locationInBounds(self, pixel_x, pixel_y):
        return self.boundaries.locationInBounds(pixel_x, pixel_y)

    def getElevationAt(self, pixel_x, pixel_y):
        elevation_value = self.raster_band_reader.readPixelAt(pixel_x, pixel_y)
        return elevation_value

    def getBoundaries(self):
        return(self.width, self.height)

class GeotiffRasterFile:
    def __init__(self, raster_file_path, nodata_value):
        self.dataset = gdal.Open(raster_file_path)
        self.nodata_value = None
        self.gdal_nodata_value = -32767.0
        self.geo_transform = self.dataset.GetGeoTransform()
        self.raster_bands = [GeotiffRasterBand(band, self.geo_transform) for band in
                                (self.dataset.GetRasterBand(i+1) for i in range(self.dataset.RasterCount))]

    def __del__(self):
        # Yes... This does close the dataset file
        self.dataset = None

    def getRasterShape(self):
        width = max(band.getBoundaries()[0] for band in self.raster_bands)
        height = max(band.getBoundaries()[1] for band in self.raster_bands)

        return (width, height)

    def getGeoTransform(self):
        return transform.GeoTransform(self.geo_transform)

    def getValueAt(self, pixel_x, pixel_y):
        for raster_band in self.raster_bands:
            if(raster_band.locationInBounds(pixel_x, pixel_y)):
                elevation = raster_band.getElevationAt(pixel_x, pixel_y)
                if elevation > self.gdal_nodata_value:
                    return elevation
        return self.nodata_value

from math import floor, ceil
class BilinearInterpolation:
    def __init__(self, raster):
        self.raster = raster

    def getRasterShape(self):
        return self.raster.getRasterShape()

    def getGeoTransform(self):
        return self.raster.getGeoTransform()

    def getValueAt(self, x, y):
        f = self.__getRasterValueAndCheckBoundaries
        x1 = floor(x)
        y1 = floor(y)
        x2 = ceil(x)
        y2 = ceil(y)

        divisor = (x2 - x1) * (y2 - y1)

        f11 = f(x1, y1)
        f21 = f(x2, y1)
        f12 = f(x1, y2)
        f22 = f(x2, y2)

        if abs(divisor) < 1e-9 or f11 is None or f21 is None or f12 is None or f22 is None:
            return f11 or f21 or f12 or f22 or None

        height_value = (1 / divisor) * (
            f11 * (x2 - x) * (y2 - y) +
            f21 * (x - x1) * (y2 - y) +
            f12 * (x2 - x) * (y - y1) +
            f22 * (x - x1) * (y - y1))

        return height_value

    def __getRasterValueAndCheckBoundaries(self, x, y):
        if self.__isInBounds(x, y):
            return self.raster.getValueAt(x, y)
        else:
            return None

    def __isInBounds(self, x, y):
        shape = self.getRasterShape()
        return x >= 0 and y >= 0 and x < shape[0] and y < shape[1]

class FloorInterpolation:
    def __init__(self, raster):
        self.raster = raster

    def getRasterShape(self):
        return self.raster.getRasterShape()

    def getGeoTransform(self):
        return self.raster.getGeoTransform()

    def getValueAt(self, pixel_x, pixel_y):
        return self.raster.getValueAt(int(pixel_x), int(pixel_y))

def createRastersFromFiles(file_list, nodata_value=None):
    return [BilinearInterpolation(GeotiffRasterFile(f, nodata_value=nodata_value)) for f in file_list]

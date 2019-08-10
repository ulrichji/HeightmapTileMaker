from . import geo_utils

import gdal

import glob
import struct

class RasterBandBoundaries:
    def __init__(self, gdal_raster_band, gdal_geo_transform):
        self.transform = gdal_geo_transform
        self.width_pixels = gdal_raster_band.XSize
        self.height_pixels = gdal_raster_band.YSize

    def locationInBounds(self, geo_x, geo_y):
        pixel_x, pixel_y = self.transform.transformGeoLocationToPixelLocation(geo_x, geo_y)
        if pixel_x >= 0 and pixel_x < self.width_pixels and pixel_y >= 0 and pixel_y < self.height_pixels:
            return True
        return False

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

class RasterBand:
    def __init__(self, gdal_raster_band, geo_transform):
        self.geo_transform = geo_utils.GdalGeoTransform(geo_transform)
        self.boundaries = RasterBandBoundaries(gdal_raster_band, self.geo_transform)
        self.raster_band_reader = RasterBandReader(gdal_raster_band)

    def locationInBounds(self, geo_x, geo_y):
        return self.boundaries.locationInBounds(geo_x, geo_y)

    def getElevationAt(self, geo_x, geo_y):
        pixel_x, pixel_y = self.geo_transform.transformGeoLocationToPixelLocation(geo_x, geo_y)
        elevation_value = self.raster_band_reader.readPixelAt(int(pixel_x), int(pixel_y))
        return elevation_value

class RasterFile:
    def __init__(self, raster_file_path):
        self.file_path = raster_file_path
        self.dataset = gdal.Open(raster_file_path)
        self.raster_bands = [RasterBand(band, self.dataset.GetGeoTransform()) for band in
                                (self.dataset.GetRasterBand(i+1) for i in range(self.dataset.RasterCount))]

    def __del__(self):
        # Yes... This does close the dataset file
        self.dataset = None

    def locationInBounds(self, geo_x, geo_y):
        for raster_band in self.raster_bands:
            if(raster_band.locationInBounds(geo_x, geo_y)):
                return True
        return False

    def getElevationAt(self, geo_x, geo_y):
        for raster_band in self.raster_bands:
            if(raster_band.locationInBounds(geo_x, geo_y)):
                return raster_band.getElevationAt(geo_x, geo_y)
        return None

# TODO: Handle NOVALUE etc
class RasterLookup:
    def __init__(self, file_list):
        self.raster_files = [RasterFile(f) for f in file_list]

    def locationInBounds(self, geo_x, geo_y):
        for raster_file in self.raster_files:
            if(raster_file.locationInBounds(geo_x, geo_y)):
                return True
        return False

    def getElevationAtPosition(self, geo_x, geo_y):
        for raster_file in self.raster_files:
            if(raster_file.locationInBounds(geo_x, geo_y)):
                return raster_file.getElevationAt(geo_x, geo_y)
        return None

from . import geo_utils

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
        self.geo_transform = geo_utils.GdalGeoTransform(geo_transform)
        self.boundaries = GeotiffRasterBandBoundaries(gdal_raster_band)
        self.raster_band_reader = RasterBandReader(gdal_raster_band)
        self.width = gdal_raster_band.XSize
        self.height = gdal_raster_band.YSize

    def locationInBounds(self, pixel_x, pixel_y):
        return self.boundaries.locationInBounds(pixel_x, pixel_y)

    def getElevationAt(self, pixel_x, pixel_y):
        elevation_value = self.raster_band_reader.readPixelAt(int(pixel_x), int(pixel_y))
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
        return geo_utils.GdalGeoTransform(self.geo_transform)

    def getValueAt(self, pixel_x, pixel_y):
        for raster_band in self.raster_bands:
            if(raster_band.locationInBounds(pixel_x, pixel_y)):
                elevation = raster_band.getElevationAt(pixel_x, pixel_y)
                if elevation > self.gdal_nodata_value:
                    return elevation
        return self.nodata_value

def createRastersFromFiles(file_list, nodata_value=None):
    return [GeotiffRasterFile(f, nodata_value=nodata_value) for f in file_list]

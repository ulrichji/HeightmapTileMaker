import geo.geo_utils
import geo.raster_lookup
from progress.null_callback import NullCallback
from progress.progress import Progress

import glob
import numpy as np

class Heightmap:
    def __init__(self):
        self.pixels = []
        self.heightmap = None
        self.nodata_fillin = 0

        self.out_of_bounds_count = 0
        self.nodata_count = 0

    def createFromRaster(self,
                         raster_lookup,
                         geo_transform,
                         heightmap_size,
                         progress_callback=NullCallback()):
        pixel_count = heightmap_size[0] * heightmap_size[1]
        self.pixels = [0 for i in range(pixel_count)]

        for y in range(heightmap_size[1]):
            for x in range(heightmap_size[0]):
                geo_pos = geo_transform.transformPixelLocationToGeoLocation(x, y)
                pixel_index = x + y*heightmap_size[0]
                if raster_lookup.locationInBounds(geo_pos[0], geo_pos[1]):
                    elevation = raster_lookup.getElevationAtPosition(geo_pos[0], geo_pos[1])
                    if elevation is not None:
                        self.pixels[pixel_index] = elevation
                    else:
                        self.pixels[pixel_index] = self.nodata_fillin
                        self.nodata_count += 1
                else:
                    self.out_of_bounds_count += 1

                progress_callback(Progress(progress=pixel_index + 1,
                    message="Creating heightmap",
                    max_progress=heightmap_size[0] * heightmap_size[1],))

        raster_matrix = np.array(self.pixels).reshape(heightmap_size)
        self.heightmap = raster_matrix

        return self

    def pixelCount(self):
        return self.heightmap.shape[0] * self.heightmap.shape[1]

    def getStatistics(self):
        return {
            'out_of_bounds_percentage':
                100.0 * float(self.out_of_bounds_count) / self.pixelCount(),
            'nodata_percentage':
                100.0 * float(self.nodata_count) / self.pixelCount()
        }

    def loadFromFile(self, file_name):
        self.heightmap = np.load(file_name)
        self.pixels = list(self.heightmap.reshape(self.heightmap.shape[0] * self.heightmap.shape[1]))

        return self

    def writeToFile(self, file_name):
        if self.heightmap is None or len(self.pixels) <= 0:
            raise Exception("Heigtmap is not loaded")
        np.save(file_name, self.heightmap)

    def getWidth(self):
        return self.heightmap.shape[0]

    def getHeight(self):
        return self.heightmap.shape[1]

    def getHeightmap(self):
        return self.heightmap


class ImageCreator:
    def __init__(self, input_raster, output_raster):
        self.input_raster = input_raster
        self.output_raster = output_raster

    def createImage(self):
        for y in range(self.output_raster.getRasterShape()[1]):
            for x in range(self.input_raster.getRasterShape()[0]):
                self.__setPixel(x, y)

    def __setPixel(self, x, y):
        geo_x, geo_y = self.output_raster.getGeoTransform().transformPixelLocationToGeoLocation(x, y)
        input_x, input_y = self.input_raster.getGeoTransform().transformGeoLocationToPixelLocation(geo_x, geo_y)
        raster_value = self.input_raster.getValueAt(input_x, input_y)
        self.output_raster.setValueAt(x, y, raster_value or (0, 0, 0))

class ImageRaster:
    def __init__(self, image, geo_transform):
        self.image = image
        self.geo_transform = geo_transform

    def getRasterShape(self):
        return (self.width(), self.height())

    def getGeoTransform(self):
        return self.geo_transform

    def getValueAt(self, pixel_x, pixel_y):
        if pixel_x >= 0 and pixel_x < self.width() and pixel_y >= 0 and pixel_y < self.height():
            return self.image.getpixel((pixel_x, pixel_y))
        return None

    def setValueAt(self, pixel_x, pixel_y, value):
        if pixel_x >= 0 and pixel_x < self.width() and pixel_y >= 0 and pixel_y < self.height():
            self.image.putpixel((pixel_x, pixel_y), value)

    def width(self):
        return self.image.size[0]

    def height(self):
        return self.image.size[1]

from geo.raster_lookup import RasterLookup

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 4:
        print("Program will print the elevation from the given geotiff files at the specified coordinate")
        print("Usage: python " + str(sys.argv[0]) + " <geo-x-coord (East)> <geo-y-coord (North)> geotiff1.tif [...]")
        print("Geo coordinates should be on the same coordinate system as the geotiff files")
        exit(-1)

    geo_x = float(sys.argv[1])
    geo_y = float(sys.argv[2])
    file_paths = sys.argv[3:]

    print("Loading dataset files")
    elevation_lookup = RasterLookup(file_paths)
    print("Searching for elevation at " + str(geo_y) + "N and " + str(geo_x) + "E")
    if elevation_lookup.locationInBounds(geo_x, geo_y):
        print("Specified coordinate is found in dataset boundaries")
        elevation = elevation_lookup.getElevationAtPosition(geo_x, geo_y)
        print("Elevation: " + str(elevation))
    else:
        print("Error: Specified coordinate was not found within the boundaries of any of the provided files")
        exit(-1)

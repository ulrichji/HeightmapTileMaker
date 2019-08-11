from geo import geo_utils
from geo import raster_lookup
from heightmap import heightmap

import progress.default_printer
import progress.timed_callback
from progress.progress import Progress

import argparse

if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser(description='Program will create a numpy array heightmap from the specified geotiff files and image top row in geo-coordinates')
    argument_parser.add_argument('top_left_corner_geo_east', metavar='top-left-corner-geo-east', type=float, help='The east geo coordinate of the top left corner of the heightmap image')
    argument_parser.add_argument('top_left_corner_geo_north', metavar='top-left-corner-geo-north', type=float, help='The north geo coordinate of the top left corner of the heightmap image')
    argument_parser.add_argument('top_right_corner_geo_east', metavar='top-right-corner-geo-east', type=float, help='The east geo coordinate of the top right corner of the heightmap image')
    argument_parser.add_argument('top_right_corner_geo_north', metavar='top-right-corner-geo-north', type=float, help='The north geo coordinate of the top right corner of the heightmap image')
    argument_parser.add_argument('geo_tiff_files', metavar='geo-tiff-files', type=str, nargs='+', help='Specify a list of geotiff files to create heightmap from')
    argument_parser.add_argument('--heightmap-width', type=int, default=1024, help='Specify the preferred width of the heightmap you want to create (default=1024)')
    argument_parser.add_argument('--heightmap-height', type=int, default=1024, help='Specify the preferred height of the heightmap you want to create (default=1024)')
    argument_parser.add_argument('--plot', action='store_true', help='Draw the resulting heightmap using pyplot')
    argument_parser.add_argument('--output', type=str, help='Specify the file of the result (npy file)')
    arguments = argument_parser.parse_args()

    geo_top_left_x = arguments.top_left_corner_geo_east
    geo_top_left_y = arguments.top_left_corner_geo_north
    geo_top_right_x = arguments.top_right_corner_geo_east
    geo_top_right_y = arguments.top_right_corner_geo_north

    heightmap_width = arguments.heightmap_width
    heightmap_height = arguments.heightmap_height

    geo_top_left = (geo_top_left_x, geo_top_left_y)
    geo_top_right = (geo_top_right_x, geo_top_right_y)
    heightmap_size = (heightmap_width, heightmap_height)

    heightmap_geo_transform = geo_utils.computeGdalGeoTransformFrom2Points(
        geo_top_left, geo_top_right, heightmap_size)

    print('Got the following GDAL geo transform parameters: ' + str(heightmap_geo_transform.transform_parameters))

    progress_printer = progress.default_printer.Printer()

    progress_printer(Progress(0, 'Loading geo files'))
    geo_tiff_files = arguments.geo_tiff_files
    raster_lookup = raster_lookup.RasterLookup(geo_tiff_files)

    heightmap = heightmap.Heightmap().createFromRaster(raster_lookup, heightmap_geo_transform, heightmap_size, progress.timed_callback.TimedCallback(progress_printer, start_at=0.05, end_at=0.9))

    if arguments.output is not None:
        progress_printer(Progress(0.9, 'Saving heightmap to ' + str(arguments.output)))
        output_file = arguments.output
        heightmap.writeToFile(output_file)

    progress_printer.finish()

    if arguments.plot is not None:
        import matplotlib.pyplot as plt

        print('Plotting image')
        plt.imshow(heightmap.getHeightmap())
        plt.show()

    print('Stats: ' + str(heightmap.getStatistics()))

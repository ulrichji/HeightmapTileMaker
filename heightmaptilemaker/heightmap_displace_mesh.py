from mesh.mesh_displace import MeshDisplace
from mesh.mesh import Mesh
from heightmap.heightmap_displacement_lookup import HeightmapDisplaceLookup
from geo import geo_utils

import glob

if __name__ == '__main__':
    mesh_file_path = 'hexagon_grid_mesh.json'
    raster_file_paths = glob.glob('D:/Files/heightmaps/Helldalisen_DTM_1m/data/dtm/N*.tif')

    print('Loading mesh from file')
    mesh = Mesh().load(mesh_file_path)

    print('Generating geo transform')
    geo_top_left = (513428, 7509110)
    geo_top_right = (519330, 7509279)
    heightmap_size = (1, 1)
    geo_transform = geo_utils.computeGdalGeoTransformFrom2Points(
        geo_top_left, geo_top_right, heightmap_size)

    print('Got the following GDAL geo transform parameters: ' + str(geo_transform.transform_parameters))

    print('Creating displacement map')
    displacement_lookup = HeightmapDisplaceLookup(
        raster_file_paths,
        geo_transform.transform_parameters,
        1/6960)

    print('Displacing mesh')
    mesh_displace = MeshDisplace().displaceMesh(mesh, displacement_lookup)

    print('Saving result')
    mesh.save('hexagon_tile.json')

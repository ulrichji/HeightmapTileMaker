from mesh.generator import grid
from mesh.mesh_clipper import clipMesh, getHexagon

import progress.default_printer
import progress.timed_callback
from progress.progress import Progress

if __name__ == '__main__':
    print("Generating grid...")
    grid_mesh = grid.generate((1024, 1024))
    print("Generating hexagon...")
    clip_mesh = getHexagon()
    print("Clipping mesh...")
    progress_printer = progress.default_printer.Printer()
    hexagon_grid = clipMesh(grid_mesh, clip_mesh, progress_printer)
    progress_printer.finish()
    print("Saving mesh...")
    hexagon_grid.save('hexagon_grid_mesh.json')

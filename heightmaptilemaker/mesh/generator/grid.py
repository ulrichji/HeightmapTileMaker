from .. import mesh

import numpy as np

def generate(resolution=(10, 10)):
    res_x = resolution[0]
    res_y = resolution[1]

    xs = np.linspace(0.0, 1.0, num=res_x)
    ys = np.linspace(0.0, 1.0, num=res_y)
    zs = np.linspace(0.0, 0.0, num=1)
    xv, yv, zv = np.meshgrid(xs, ys, zs)

    vertices = np.array(list(zip(xv.flatten(), yv.flatten(), zv.flatten())))

    upper_left_tris = [(y*res_x + x, (y+1)*res_x + x, y*res_x + x + 1) for y in range(res_y-1) for x in range(res_x-1)]
    lower_right_tris = [((y+1)*res_x + x + 1, y*res_x + x + 1, (y+1)*res_x + x) for y in range(res_y-1) for x in range(res_x - 1)]
    faces = upper_left_tris + lower_right_tris

    return_mesh = mesh.Mesh()
    for vertex in vertices:
        return_mesh.addVertex(mesh.MeshVertex(position=vertex))
    for face in faces:
        return_mesh.addFace(mesh.MeshFace(indices=face))

    return return_mesh

if __name__ == '__main__':
    generate()

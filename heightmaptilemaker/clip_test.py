from mesh.clip_polygon import Polygon

def intersectionTestPolygons():
    return (Polygon([
                (-2.02, 0.73), (-6.53, 7.11), (4.08, 8.43), (-2, 6),
                (7.77, 3.28), (-4.26, -3.82), (-8.72, -3.78)]),
            Polygon([
                (-9.17, -2.55), (0.16, -4.69), (0, 1.46), (3.4, -1.13),
                (-1.7, 8.52), (-6.94, 6.56), (-8.4, 3.1), (-5.44, 1.69)]))

def containedTestPolygons():
    return (Polygon([
                (-2.02, 0.73), (-6.53, 7.11), (4.08, 8.43), (-2, 6),
                (7.77, 3.28), (-4.26, -3.82), (-8.72, -3.78)]),
            Polygon([
                (-6.17,-2.55), (0.16,-0.69), (0,1.46), (3.4,1.87),
                (-2.7,6.52), (-5.94,6.56), (-2.4,3.1), (-0.44,1.69)]))

def nonContainedTestPolygons():
    return (Polygon([
                (-6.17,-2.55), (0.16,-0.69), (0,1.46), (3.4,1.87),
                (-2.7,6.52), (-5.94,6.56), (-2.4,3.1), (-0.44,1.69)]),
            Polygon([
                (-2.02, 0.73), (-6.53, 7.11), (4.08, 8.43), (-2, 6),
                (7.77, 3.28), (-4.26, -3.82), (-8.72, -3.78)]))

def separatedTestPolygons():
    return (Polygon([
                (-6.17,-2.55), (0.16,-0.69), (0,1.46), (3.4,1.87),
                (-2.7,6.52), (-5.94,6.56), (-2.4,3.1), (-0.44,1.69)]),
            Polygon([
                (-11.17,-1.55), (-10.84,-4.69), (-3.9,1.46), (-5.4,0.87),
                (-4.6,3.62), (-6.94,6.56), (-8.4,3.1), (-5.44,1.69)]))

def triangleHexagonPolygons():
    return (Polygon([
                (0,0.5), (0.25,0.9330127018922193), (0.75,0.9330127018922193), (1,0.5),
                (0.75,0.0669872981077807), (0.25,0.0669872981077807)]),
            Polygon([(0,0.9), (0.5,0.9), (0.5,0.6)]))

def startInsideHexagon():
    return (Polygon([
                (0,0.5), (0.25,0.9330127018922193), (0.75,0.9330127018922193), (1,0.5),
                (0.75,0.0669872981077807), (0.25,0.0669872981077807)]),
            Polygon([(0.5,0.9), (0.5,0.6), (0,0.9)]))

def triangleHexagonReverseOrder():
    return (Polygon([(0.5,0.9), (0.5,0.6), (0,0.9)]),
            Polygon([
                (0,0.5), (0.25,0.9330127018922193), (0.75,0.9330127018922193), (1,0.5),
                (0.75,0.0669872981077807), (0.25,0.0669872981077807)]))

def singleTriangleVertexInHexagon():
    return (Polygon([
                (0,0.5), (0.25,0.9330127018922193), (0.75,0.9330127018922193), (1,0.5),
                (0.75,0.0669872981077807), (0.25,0.0669872981077807)]),
            Polygon([(0,0.9), (0.5,0.9), (0.0,0.6)]))

def pointOnEdge():
    return (Polygon([
                (0,0.5), (0.25,0.9330127018922193), (0.75,0.9330127018922193), (1,0.5),
                (0.75,0.0669872981077807), (0.25,0.0669872981077807)]),
            Polygon([(0,0.9), (0.5,0.9), (0.0,0.4)]))

def doubleTriangleIntersectionReversed():
    return (Polygon([
                (0,0.5), (0.25,0.0669872981077807), (0.75,0.0669872981077807), (1,0.5),
                (0.75,0.9330127018922193), (0.25,0.9330127018922193)]),
            Polygon([(0.5,0.9), (0,0.9), (0.0,0.6)]))

def clipTest(test_objects_functor):
    print('Test: ' + str(test_objects_functor))
    clip_polygon, polygon_to_clip = test_objects_functor()

    clip_polygon.geodrafter_printPolygon()
    polygon_to_clip.geodrafter_printPolygon()

    result_polygon = clip_polygon.clip(polygon_to_clip)

    result_polygon.geodrafter_printPolygon()
    print()

if __name__ == '__main__':
    clipTest(intersectionTestPolygons)
    clipTest(containedTestPolygons)
    clipTest(nonContainedTestPolygons)
    clipTest(separatedTestPolygons)
    clipTest(triangleHexagonPolygons)
    clipTest(startInsideHexagon)
    clipTest(triangleHexagonReverseOrder)
    clipTest(singleTriangleVertexInHexagon)
    clipTest(pointOnEdge)
    clipTest(doubleTriangleIntersectionReversed)

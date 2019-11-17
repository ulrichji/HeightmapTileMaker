from .polygon_boolean_operator import PolygonBooleanOperator
from .greiner_hormann_clipper import GreinerHormannPolygon

class Polygon:
    def __init__(self, points):
        self.points = points

    def performBoolean(self, other_polygon, boolean_operator=PolygonBooleanOperator.INTERSECTION):
        gh_clip_polygon = GreinerHormannPolygon(self.points)
        gh_other_polygon = GreinerHormannPolygon(other_polygon.points)

        GreinerHormannPolygon.linkPolygons(gh_clip_polygon, gh_other_polygon)
        result_polygon = gh_clip_polygon.getPolygonPointsFromBoolean(gh_other_polygon, boolean_operator=boolean_operator)
        return Polygon([point.pos for point in result_polygon.points])

    def clip(self, other_polygon):
        return self.performBoolean(other_polygon, boolean_operator=PolygonBooleanOperator.INTERSECTION)

    # Function is intended to be used with the geodrafter online tool:
    # https://www.matheretter.de/calc/geodrafter
    def geodrafter_printPolygon(self):
        print('polygon(' + ' '.join(str(point[0]) + '|' + str(point[1]) for point in self.points) + ')')

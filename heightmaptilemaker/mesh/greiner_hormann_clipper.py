from .polygon_boolean_operator import PolygonBooleanOperator

from enum import Enum
from math import sqrt

class IntersectionType(Enum):
    NOT_AN_INTERSECTION=0
    UNKNOWN=1
    ENTRY=2
    EXIT=3

    def isIntersection(self):
        return self == self.UNKNOWN or self == self.ENTRY or self == self.EXIT

    def getInverted(self):
        if(self == self.ENTRY):
            return self.EXIT
        elif(self == self.EXIT):
            return self.ENTRY

        return enum_type

class TraversalDirection(Enum):
    FORWARD=1
    BACKWARDS=2

class PolygonPoint:
    def __init__(self, pos, is_intersection=False):
        self.pos = pos
        self.next = None
        self.prev = None
        self.other_polygon_link = None
        self.intersection_type = IntersectionType.UNKNOWN if is_intersection else IntersectionType.NOT_AN_INTERSECTION
        self.processed = False

    def setNext(self, next_point):
        self.next = next_point

    def setPrev(self, prev_point):
        self.prev = prev_point

    def getNext(self, traversal_direction):
        if traversal_direction == TraversalDirection.FORWARD:
            return self.next
        elif traversal_direction == TraversalDirection.BACKWARDS:
            return self.prev

    def linkToPoint(self, other_point):
        self.other_polygon_link = other_point

    def __str__(self):
        return '(' + ','.join(str(p) for p in self.pos) + ')'

class PolygonEdge:
    def __init__(self, from_point, to_point):
        self.from_point = from_point
        self.to_point = to_point
        self.intersections = []

    def insertIntersectionAt(self, intersection_point, t):
        self.intersections.append((intersection_point, t))

    def getIntersectionsAsPoints(self):
        self.intersections.sort(key=lambda intersection: intersection[1])

        return [intersection[0] for intersection in self.intersections]

    # Source: https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
    #    Title: Line–line intersection
    #    Author: Wikipedia
    #    Last edit date: 16 August 2019
    def computeIntersection(self, other_edge):
        x1,y1 = (self.from_point.pos[0], self.from_point.pos[1])
        x2,y2 = (self.to_point.pos[0], self.to_point.pos[1])
        x3,y3 = (other_edge.from_point.pos[0], other_edge.from_point.pos[1])
        x4,y4 = (other_edge.to_point.pos[0], other_edge.to_point.pos[1])

        t_dividend = ((x1 - x3) * (y3 - y4)) - ((y1 - y3) * (x3 - x4))
        u_dividend = -(((x1 - x2) * (y1 - y3)) - ((y1 - y2) * (x1 - x3)))

        tu_divisor = ((y3 - y4) * (x1 - x2)) - ((y1 - y2) * (x3 - x4))

        if abs(tu_divisor) <= 1e-9:
            return None

        t = t_dividend / tu_divisor
        u = u_dividend / tu_divisor

        if t <= 1e-9 or t > 1 - 1e-9 or u < 1e-9 or u >= 1 - 1e-9:
            return None


        intersection_point = (x1 + (t * (x2 - x1)), y1 + (t * (y2 - y1)), 0)
        return (intersection_point, t)

    # Source: https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
    #    Title: Line–line intersection
    #    Author: Wikipedia
    #    Last edit date: 16 August 2019
    def computeIntersectionForPointInPolygon(self, other_edge):
        x1,y1 = (self.from_point.pos[0], self.from_point.pos[1])
        x2,y2 = (self.to_point.pos[0], self.to_point.pos[1])
        x3,y3 = (other_edge.from_point.pos[0], other_edge.from_point.pos[1])
        x4,y4 = (other_edge.to_point.pos[0], other_edge.to_point.pos[1])

        t_dividend = ((x1 - x3) * (y3 - y4)) - ((y1 - y3) * (x3 - x4))
        u_dividend = -(((x1 - x2) * (y1 - y3)) - ((y1 - y2) * (x1 - x3)))

        tu_divisor = ((y3 - y4) * (x1 - x2)) - ((y1 - y2) * (x3 - x4))

        if abs(tu_divisor) <= 1e-9:
            return None

        t = t_dividend / tu_divisor
        u = u_dividend / tu_divisor

        is_upward = y3 < y4
        is_downward = y3 > y4

        if is_upward:
            if t <= 1e-9 or t >= 1 - 1e-9 or u <= -1e-9 or u >= 1 - 1e-9:
                return None
        elif is_downward:
            if t < 1e-9 or t >= 1 - 1e-9 or u <= 1e-9 or u >= 1 + 1e-9:
                return None
        else:
            return None

        intersection_point = (x1 + (t * (x2 - x1)), y1 + (t * (y2 - y1)), 0)
        return (intersection_point, t)

    def isPointLeft(point):
        P0 = self.from_point.pos
        P1 = self.to_point.pos
        P2 = point

        return ((P1[0] - P0[0]) * (P2[1] - P0[1]) - (P2[0] -  P0[0]) * (P1[1] - P0[1]))

    def intersectsPoint(self, point):
        x0,y0 = (point.pos[0], point.pos[1])
        x1,y1 = (self.from_point.pos[0], self.from_point.pos[1])
        x2,y2 = (self.to_point.pos[0], self.to_point.pos[1])

        dividend = sqrt((y2 - y1)**2 + (x2 - x1)**2)
        if dividend <= 1e-9:
            return False

        divisor = (y2 - y1)*x0 - (x2 - x1)*y0 + x2*y1 + y2*x1
        distance = abs(divisor / dividend)

        if distance < 1e-9:
            return True

        return False

class GreinerHormannPolygon:
    def __init__(self, points_list=[]):
        self.points = [PolygonPoint(point) for point in points_list]
        self.edges = self.__getEdgesFromPoints()

        self.__setupPointsOrder()

    def remakeFromEdges(self, edge_list):
        edge_points = [[edge.from_point, *edge.getIntersectionsAsPoints()] for edge in edge_list]
        #print("Edge points:", ','.join('(' + ','.join(str(pt) for pt in edge_point) + ')' for edge_point in edge_points))
        self.points = [point for edge in edge_points for point in edge]
        #print('Points:', ','.join(str(pt) for pt in self.points))
        #print("Edges first: ", ', '.join('(' + ', '.join((str(edge.from_point), str(edge.to_point))) + ')' for edge in self.edges))
        self.edges = self.__getEdgesFromPoints()
        #print("Edges after: ", ', '.join('(' + ', '.join((str(edge.from_point), str(edge.to_point))) + ')' for edge in self.edges))
        self.__setupPointsOrder()

    def isPointInside(self, point):
        #cn = 0; # the  crossing number counter

        ## loop through all edges of the polygon
        #for i in range(len(self.points)):
        #    current_vertex = self.points[i]
        #    next_vertex = self.points[(i + 1) % len(self.points)]

        #    if (((current_vertex.pos[1] <= point[1]) and (next_vertex.pos[1] > point[1])) or ((current_vertex.pos[1] > point[1]) and (next_vertex.pos[1] <= point[1]))):
        #        vt = (point[1] - current_vertex.pos[1]) / (next_vertex.pos[1] - current_vertex.pos[1])
        #        if point[1] < current_vertex.pos[1] + vt * (next_vertex.pos[0] - current_vertex.pos[0]):
        #            cn += 1

        #return cn % 2 == 1
        ray_from_point = PolygonPoint((point[0], point[1]))
        # This has length of polygon width to maximize the floating point resolution
        max_x_point = max(p.pos[0] for p in self.points)
        ray_to_point = PolygonPoint((max_x_point + 1, point[1]))

        ray = PolygonEdge(ray_from_point, ray_to_point)
        ray_intersections = (ray.computeIntersectionForPointInPolygon(edge) for edge in self.edges)
        ray_intersections_count = sum(1 for intersection in ray_intersections if intersection)
        is_point_inside = ray_intersections_count % 2 == 1

        return is_point_inside

        #vertex_intersections = [ray.intersectsPoint(p) for p in self.points]
        #edge_intersection_count = sum(0 if intersection is None else 1 for intersection in ray_intersections)
        #vertex_intersection_count = sum(a for a in vertex_intersections)
        ##if edge_intersection_count % 2 == 1 or vertex_intersection_count > 0:
        ##    print()
        ##    print(edge_intersection_count, vertex_intersection_count)
        ##    print()
        #intersection_count = edge_intersection_count + vertex_intersection_count
        ##print('Points: ', ','.join(str(pt) for pt in self.points))
        ##print('INts:', vertex_intersections)

        #is_point_inside = intersection_count % 2 == 1
        ##print("Edge cnt:", len(self.edges), ", edgeint:", edge_intersection_count, ", pointint:", vertex_intersection_count)
        ##print("Edges: ", ', '.join(', '.join((str(edge.from_point), str(edge.to_point))) for edge in self.edges))
        ##print("Is point inside:", point, is_point_inside, ", ray:", ray.from_point, ray.to_point, intersection_count)

        #if abs(point[0] - 0.16535) < 0.00005 and abs(point[1] -  0.20472) < 0.00005:
        #    print(','.join(str(pt) for pt in self.points))
        #    print(is_point_inside, edge_intersection_count, vertex_intersection_count, len(self.points), ray.from_point, ray.to_point, "     ")

        #return is_point_inside

    @staticmethod
    def linkPolygons(first_polygon, second_polygon):
        GreinerHormannPolygon.__computeEdgeIntersections(first_polygon, second_polygon)
        first_polygon.__updateIntersectionTypes(second_polygon)
        second_polygon.__updateIntersectionTypes(first_polygon)

    def getPolygonPointsFromBoolean(self, other_polygon, boolean_operator):
        return self.__createPolygonFromIntersections(other_polygon, boolean_operator)

    def __getEdgesFromPoints(self):
        #print('Points:', ', '.join(str(point) for point in self.points))
        return [PolygonEdge(self.points[i], self.points[(i+1) % len(self.points)]) for i in range(len(self.points))]

    def __setupPointsOrder(self):
        for i in range(len(self.points)):
            point = self.points[i]
            next_point = self.points[(i+1) % len(self.points)]
            prev_point = self.points[i-1]

            point.setNext(next_point)
            point.setPrev(prev_point)

    def __computePolygonWidth(self):
        return max(point.pos[0] for point in self.points) - min(point.pos[0] for point in self.points)

    @staticmethod
    def __computeEdgeIntersections(first_polygon, second_polygon):
        intersections = []
        for first_edge in first_polygon.edges:
            for second_edge in second_polygon.edges:
                first_intersection = first_edge.computeIntersection(second_edge)
                second_intersection = second_edge.computeIntersection(first_edge)
                if first_intersection is not None and second_intersection is not None:
                    first_intersection_pos, t = first_intersection
                    second_intersection_pos, u = second_intersection

                    first_intersection_point = PolygonPoint(first_intersection_pos, is_intersection=True)
                    second_intersection_point = PolygonPoint(second_intersection_pos, is_intersection=True)

                    first_intersection_point.linkToPoint(second_intersection_point)
                    second_intersection_point.linkToPoint(first_intersection_point)

                    first_edge.insertIntersectionAt(first_intersection_point, t)
                    second_edge.insertIntersectionAt(second_intersection_point, u)

        first_polygon.remakeFromEdges(first_polygon.edges)
        second_polygon.remakeFromEdges(second_polygon.edges)

    def __updateIntersectionTypes(self, other_polygon):
        if len(self.points) <= 0:
            return None

        current_intersection_type = self.__getFirstIntersectionType(other_polygon)
        for point in self.points:
            if point.intersection_type.isIntersection():
                point.intersection_type = current_intersection_type
                current_intersection_type = current_intersection_type.getInverted()

    def __getFirstIntersectionType(self, other_polygon):
        is_inside_other = other_polygon.isPointInside(self.points[0].pos)
        return IntersectionType.EXIT if is_inside_other else IntersectionType.ENTRY

    def __createPolygonFromIntersections(self, other_polygon, boolean_operator):
        intersections = [point for point in self.points if point.intersection_type.isIntersection()]

        if len(intersections) <= 0:
            return self.__getNonIntersectingPolygon(other_polygon, boolean_operator)

        return self.__tracePolygonPerimetersFromIntersections(intersections, boolean_operator)

    def __getNonIntersectingPolygon(self, other_polygon, boolean_operator):
        # Currently the only supported boolean operator
        assert(boolean_operator == PolygonBooleanOperator.INTERSECTION)

        this_is_inside_other = other_polygon.isPointInside(self.points[0].pos)
        other_is_inside_this = self.isPointInside(other_polygon.points[0].pos)
        if not this_is_inside_other and not other_is_inside_this:
            return GreinerHormannPolygon()
        if this_is_inside_other:
            return self
        else:
            return other_polygon

    def __tracePolygonPerimetersFromIntersections(self, intersections, boolean_operator):
        # Currently the only supported boolean operator
        assert(boolean_operator == PolygonBooleanOperator.INTERSECTION)

        result_polygon_points = []
        current_point = intersections[0]
        traversal_direction = TraversalDirection.FORWARD
        _cnt = 0
        while(any(not intersection.processed for intersection in intersections) or current_point != intersections[0]):
            result_polygon_points.append(current_point.pos)

            if current_point.intersection_type.isIntersection():
                current_point.processed = True
                current_point = current_point.other_polygon_link
                current_point.processed = True
                traversal_direction = TraversalDirection.FORWARD if current_point.intersection_type == IntersectionType.ENTRY else TraversalDirection.BACKWARDS

            current_point = current_point.getNext(traversal_direction)
            _cnt += 1

            if(_cnt > 1000):
                print("Fail")
                return GreinerHormannPolygon(result_polygon_points)

        return GreinerHormannPolygon(result_polygon_points)

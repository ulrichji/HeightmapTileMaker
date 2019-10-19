from polygon_boolean_operator import PolygonBooleanOperator

from enum import Enum

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
        t_divisor = ((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))

        u_dividend = -(((x1 - x2) * (y1 - y3)) - ((y1 - y2) * (x1 - x3)))
        u_divisor = ((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))

        if abs(t_divisor) <= 0 or abs(u_divisor) <= 0:
            return None

        t = t_dividend / t_divisor
        u = u_dividend / u_divisor

        if t < 0 or t > 1 or u < 0 or u > 1:
            return None

        intersection_point = (x1 + (t * (x2 - x1)), y1 + (t * (y2 - y1)))
        return (intersection_point, t)

class GreinerHormannPolygon:
    def __init__(self, points_list=[]):
        self.points = [PolygonPoint(point) for point in points_list]
        self.edges = self.__getEdgesFromPoints()

        self.__setupPointsOrder()

    def remakeFromEdges(self, edge_list):
        edge_points = [[edge.from_point, *edge.getIntersectionsAsPoints()] for edge in edge_list]
        self.points = [point for edge in edge_points for point in edge]
        self.edges = self.__getEdgesFromPoints()

        self.__setupPointsOrder()

    def isPointInside(self, point):
        ray_from_point = PolygonPoint(point)
        # This has length of polygon width to maximize the floating point resolution
        ray_to_point = PolygonPoint((point[0] + self.__computePolygonWidth(), point[1]))

        ray = PolygonEdge(ray_from_point, ray_to_point)
        ray_intersections = (ray.computeIntersection(edge) for edge in self.edges)
        intersection_count = sum(0 if intersection is None else 1 for intersection in ray_intersections)

        return intersection_count % 2 == 1

    @staticmethod
    def linkPolygons(first_polygon, second_polygon):
        GreinerHormannPolygon.__computeEdgeIntersections(first_polygon, second_polygon)
        first_polygon.__updateIntersectionTypes(second_polygon)
        second_polygon.__updateIntersectionTypes(first_polygon)

    def getPolygonPointsFromBoolean(self, other_polygon, boolean_operator):
        return self.__createPolygonFromIntersections(other_polygon, boolean_operator)

    def __getEdgesFromPoints(self):
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
        while(any(not intersection.processed for intersection in intersections) or current_point != intersections[0]):
            result_polygon_points.append(current_point.pos)

            if current_point.intersection_type.isIntersection():
                current_point.processed = True
                current_point.other_polygon_link.processed = True
                current_point = current_point.other_polygon_link
                traversal_direction = TraversalDirection.FORWARD if current_point.intersection_type == IntersectionType.ENTRY else TraversalDirection.BACKWARDS

            current_point = current_point.getNext(traversal_direction)

        return GreinerHormannPolygon(result_polygon_points)

import math

import globals
import global_constants

def get_center(width:int, height:int) -> tuple:
    return (width/2, height/2)

def cross_product(v1, v2):
    return v1[0] * v2[1] - v1[1] * v2[0]

def is_point_in_rhombus(rhombus_points, point) -> bool:

    A, B, C, D = rhombus_points

    # Create vectors from rhombus vertices to the point
    AP = (point[0] - A[0], point[1] - A[1])
    BP = (point[0] - B[0], point[1] - B[1])
    CP = (point[0] - C[0], point[1] - C[1])
    DP = (point[0] - D[0], point[1] - D[1])

    # Create vectors for rhombus edges
    AB = (B[0] - A[0], B[1] - A[1])
    BC = (C[0] - B[0], C[1] - B[1])
    CD = (D[0] - C[0], D[1] - C[1])
    DA = (A[0] - D[0], A[1] - D[1])

    # Calculate cross products
    cross1 = cross_product(AB, AP)
    cross2 = cross_product(BC, BP)
    cross3 = cross_product(CD, CP)
    cross4 = cross_product(DA, DP)

    # Check if the point is on the same side of all edges as the opposite vertex
    if (cross1 > 0 and cross2 > 0 and cross3 > 0 and cross4 > 0) or \
       (cross1 < 0 and cross2 < 0 and cross3 < 0 and cross4 < 0):
        return True
    return False

def intersection_point(p1, p2, p3, p4):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0: return None  # Lines are parallel or coincident

    # Calculate the numerators
    num_x = (x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)
    num_y = (x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)

    # Calculate intersection point
    x = num_x / denom
    y = num_y / denom

    return (x, y)

def distance_between_points(p1, p2):
    x1, y1 = p1
    x2, y2 = p2

    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    return distance

def projection_coords_by_abstraction_coords(x, y, h):
    (ground_level_origin_x, ground_level_origin_y) = global_constants.PROJECTION_GROUND_LEVEL_ORIGIN

    x_relative_to_ground_level_origin = x * global_constants.PROJECTION_TILE_X_OFFSET
    y_relative_to_ground_level_origin = y * global_constants.PROJECTION_TILE_Y_OFFSET - h * global_constants.PROJECTION_TILE_Y_OFFSET

    return (ground_level_origin_x + x_relative_to_ground_level_origin, ground_level_origin_y + y_relative_to_ground_level_origin)

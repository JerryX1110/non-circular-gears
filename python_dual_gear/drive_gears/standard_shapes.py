from math import sin, cos, pi, sqrt
from scipy.spatial import distance
import numpy as np
from drive_gears.shape_processor import toCartesianCoordAsNp

ellipse_a, ellipse_b = 1.5, 1


def gen_focal_ellipse(number_of_samples: int) -> [float]:
    sample_points = np.linspace(0, 2 * pi, number_of_samples, endpoint=False)
    a, e = ellipse_a, sqrt(1 - ellipse_b ** 2 / ellipse_a ** 2)

    def _radius(theta):
        return a * (1 - e * e) / (1 + e * cos(theta))

    return [_radius(theta) for theta in sample_points]


def gen_ellipse_gear(number_of_samples: int) -> [float]:
    a, b = ellipse_a, ellipse_b
    sample_points = np.linspace(0, 2 * pi, number_of_samples, endpoint=False)

    def _radius(theta):
        return a * b / distance.euclidean((0, 0), (b * cos(theta), a * sin(theta)))

    return [
        _radius(theta)
        for theta in sample_points
    ]


def gen_circular_gear(number_of_samples: int) -> [float]:
    return [1.0] * number_of_samples


std_shapes = {
    "circular": gen_circular_gear,
    "ellipse": gen_ellipse_gear,
    "focal_ellipse": gen_focal_ellipse,
}


def generate_std_shapes(type: str, n: int, center_point):
    if type not in std_shapes:
        print(f"Type Error! No {type} found!")
    else:
        return toCartesianCoordAsNp(std_shapes[type](n), center_point[0], center_point[1])

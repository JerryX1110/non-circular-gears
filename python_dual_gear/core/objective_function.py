from drive_gears.shape_processor import getUniformContourSampledShape
import numpy as np
from optimization.dtw import dtw
from typing import Union


def calculate_area(points):
    points = tuple(points)
    assert len(points) == 3
    matrix = np.append(np.array(points), np.ones((3, 1), np.float64), axis=1)
    return 0.5 * np.linalg.det(matrix)


def triangle_area(points, index, spacing):
    indices = index - spacing, index, index + spacing
    indices = [i % len(points) for i in indices]
    return calculate_area((points[index] for index in indices))


def triangle_area_representation(contour: np.ndarray, sample_count: int) -> np.ndarray:
    """
    calculate the TAR of a given contour
    :param contour: counterclockwise [(x,y)] points
    :param sample_count: number of points to be re-sampled
    :return: TAR(n,ts) as a 2-dim array
    """
    contour = getUniformContourSampledShape(contour, sample_count, False)
    # answer = np.empty((sample_count, (sample_count - 1) // 2))
    # for index in range(sample_count):
    #     for ts in range(1, 1 + answer.shape[1]):
    #         answer[index, ts - 1] = triangle_area(contour, index, ts)
    perimeter = sum([np.linalg.norm(contour[i] - contour[i - 1]) for i in range(len(contour))])
    answer = np.array([[triangle_area(contour, index, ts + 1) for ts in range((sample_count - 1) // 2)]
                       for index in range(sample_count)])
    return answer / perimeter ** 2


def tar_to_distance_matrix(tar_a: np.ndarray, tar_b: np.ndarray) -> np.ndarray:
    assert tar_a.shape == tar_b.shape
    ts = tar_a.shape[1]
    answer = np.empty((tar_a.shape[0], tar_b.shape[0]), dtype=float)
    for i in range(answer.shape[0]):
        for j in range(answer.shape[1]):
            distance_sum = 0
            for k in range(ts):
                distance_sum += abs(tar_a[i, k] - tar_b[j, k])
            distance_sum /= ts
            answer[i, j] = distance_sum
    return answer


def dtw_distance(distance_matrix: np.ndarray, offset: int) -> float:
    assert distance_matrix.shape[0] == distance_matrix.shape[1]
    n = distance_matrix.shape[0]

    def distance(index_a, index_b) -> float:
        index_a = index_a % n
        index_b = (index_b - offset) % n
        return distance_matrix[index_a, index_b]

    return dtw(distance_matrix.shape, distance)[0]


def trivial_distance(distance_matrix: np.ndarray, offset: int) -> float:
    assert distance_matrix.shape[0] == distance_matrix.shape[1]
    n = distance_matrix.shape[0]
    return distance_matrix.trace(offset=offset) + distance_matrix.trace(offset=offset - n)


def tar_distance(tar_a: np.ndarray, tar_b: np.ndarray, distance_function=dtw_distance) -> float:
    assert tar_a.shape == tar_b.shape
    distance_matrix = tar_to_distance_matrix(tar_a, tar_b)
    return min([distance_function(distance_matrix, offset) for offset in range(tar_a.shape[0])])


def shape_difference_rating(contour_a: np.ndarray, contour_b: np.ndarray,
                            sample_rate: Union[int, None] = None, distance_function=dtw_distance) -> float:
    """
    calculate the shape difference level according to TAR function and DSW
    :param contour_a: the contour A array([(x,y)]) in counterclockwise direction
    :param contour_b: the contour B array([(x,y)]) in counterclockwise direction
    :param sample_rate: the re-sampled rate used in the calculation, None for choosing the maximum of input
    :param distance_function: the distance warping function used (dtw or trivial)
    :return: TAR DSW-difference
    """
    if sample_rate is None:
        sample_rate = max(contour_a.shape[0], contour_b.shape[0])
    tar_a = triangle_area_representation(contour_a, sample_rate)
    tar_b = triangle_area_representation(contour_b, sample_rate)
    return tar_distance(tar_a, tar_b, distance_function)



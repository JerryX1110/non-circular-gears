from shape_processor import getUniformContourSampledShape
import numpy as np
from dtw import dtw
import math
import matplotlib.pyplot as plt
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


def tar_distance(tar_a: np.ndarray, tar_b: np.ndarray) -> float:
    assert tar_a.shape == tar_b.shape
    distance_matrix = tar_to_distance_matrix(tar_a, tar_b)
    return min([dtw_distance(distance_matrix, offset) for offset in range(tar_a.shape[0])])


def shape_difference_rating(contour_a: np.ndarray, contour_b: np.ndarray,
                            sample_rate: Union[int, None] = None) -> float:
    """
    calculate the shape difference level according to TAR function and DSW
    :param contour_a: the contour A array([(x,y)]) in counterclockwise direction
    :param contour_b: the contour B array([(x,y)]) in counterclockwise direction
    :param sample_rate: the re-sampled rate used in the calculation, None for choosing the maximum of input
    :return: TAR DSW-difference
    """
    if sample_rate is None:
        sample_rate = max(contour_a.shape[0], contour_b.shape[0])
    tar_a = triangle_area_representation(contour_a, sample_rate)
    tar_b = triangle_area_representation(contour_b, sample_rate)
    return tar_distance(tar_a, tar_b)


if __name__ == '__main__':
    import os
    import time

    plt.ion()
    fig, subplots = plt.subplots(1, 2)
    square_contour = np.array([(0, 0), (10, 0), (10, 10), (0, 10)])
    debug_dir = os.path.join(os.path.dirname(__file__), 'debug/objective_function_test/')
    os.makedirs(debug_dir)


    def rect_contour(height):
        return np.array(
            [(0, 0), (10, 0), (10, height), (0, height)]
        )


    for i in np.linspace(1, 21, 100):
        square = getUniformContourSampledShape(square_contour, 1024, False)
        rect = getUniformContourSampledShape(rect_contour(i), 1024, False)
        for subplot in subplots:
            subplot.clear()
        subplots[0].plot(*square.transpose())
        subplots[1].plot(*rect.transpose())
        subplots[1].text(0, 0, shape_difference_rating(square, rect, 64))
        for subplot in subplots:
            subplot.axis('equal')
        plt.savefig(os.path.join(debug_dir, f'test_{i}.png'))
        time.sleep(0.1)

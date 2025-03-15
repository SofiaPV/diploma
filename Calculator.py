import numpy as np
from FileManager import FileManager


class Calculator:

    def __init__(self, mainfile=None, files=None):
        self._manager = FileManager(mainfile, files)

        self._main = None  # main frame
        self._original_points = None  # a [x, y, z] array for visualization
                                      # before movement
        self._moved_points = None   #  a [x, y, z] array after movement
        self._frame_info = None     # an array with rotation matrix[0],
                                    # matrix of movement[1] and angles[2]



    @staticmethod
    def _make_matrices(m, num_of_rows=3, points_in_row=5):
        """
        :param m: construct matrix for calculation
        :param num_of_rows: rows to use
        :param points_in_row:  how many points a row has
        :return: matrix suitable for calculations
        """
        ans = []
        for i in range(num_of_rows * points_in_row):
            ans.append(list(m[i]))
            ans[-1].append(1)
        return np.array(ans)

    @staticmethod
    def calc_matrices(points, deformed_points, num_of_rows=3, points_in_row=5, l=0):

        before = Calculator._make_matrices(points, num_of_rows, points_in_row)
        after = deformed_points[:num_of_rows * points_in_row]

        xtx = before.T @ before
        weigths = np.linalg.inv(xtx + np.eye(xtx.shape[0]) * l) @ before.T @ after

        return weigths[:3, :], weigths[-1, :]  # M, b



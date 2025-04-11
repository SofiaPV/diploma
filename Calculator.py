import numpy as np
import math
from FileManager import FileManager, InvalidFormatError


class Calculator:

    def __init__(self, mainfile=None, files=None):
        self._manager = FileManager(mainfile, files)  # !!! getter, setter
        self._mainfile = mainfile
        self._files = files

        self._main = None  # main frame
        self._original_points = []  # a [x, y, z] array for visualization
                                      # before movement
        self._moved_points = []   #  a [x, y, z] array after movement
        self._frame_info = dict()

        self._rows = None
        self._points_in_row = None

    @property
    def rows(self):
        return self._rows

    @property
    def points_in_row(self):
        return self._points_in_row

    @rows.setter
    def rows(self, new_value):
        if not new_value.isdigit():
            self._rows = None
            raise ValueError
        self._rows = int(new_value)

    @points_in_row.setter
    def points_in_row(self, new_value):
        if not new_value.isdigit():
            self._points_in_row = None
            raise ValueError
        self._points_in_row = int(new_value)

    @property
    def mainfile(self):
        return self._mainfile

    @property
    def files(self):
        return self._files

    @mainfile.setter
    def mainfile(self, new):
        self._mainfile = new

    @files.setter
    def files(self, new):
        self._files = new

    @property
    def mainframe(self):
        if self._main is None:
            self._read()
            if self._main is None:
                raise ValueError
        return self._main

    @property
    def original_points(self):
        if len(self._original_points) == 0:
            self._read()
            if len(self._original_points) == 0:
                raise ValueError
        return self._original_points

    @property
    def moved_points(self):
        return self._moved_points

    @property
    def frame_info(self):
        return self._frame_info

    def _make_matrices(self, m, num_of_rows=3, points_in_row=5):
        """
        :param m: construct matrix for calculation
        :param num_of_rows: rows to use
        :param points_in_row:  how many points a row has
        :return: matrix suitable for calculations
        """
        print(f"m: {m}\n num_of_rows: {num_of_rows}\npoints_in_row: {points_in_row}")
        ans = []
        for i in range(num_of_rows * points_in_row):
            ans.append(list(m[i]))
            ans[-1].append(1)
        return np.array(ans)

    @staticmethod
    def compute_angels(matrix, in_angles=False):
        """
        :matrix: a rotation matrix
        :in_angles: if True, returns rotations in angles, else in radians
        :return [[theta (y axis), psi(rotation about x axis), phi (z-axis)], ...]
        """

        if matrix[2][0] != 1 and matrix[2][0] != -1:

            angles = np.array([[0., 0., 0.], [0., 0., 0.]])

            # theta
            angles[0][0] = -math.asin(matrix[2][0])
            angles[1][0] = math.pi - angles[0][0]

            # psi
            angles[0][1] = math.atan2(matrix[2][1] / math.cos(angles[0][0]), matrix[2][2] / math.cos(angles[0][0]))
            angles[1][1] = math.atan2(matrix[2][1] / math.cos(angles[1][0]), matrix[2][2] / math.cos(angles[1][0]))

            # phi
            angles[0][2] = math.atan2(matrix[1][0] / math.cos(angles[0][0]), matrix[0][0] / math.cos(angles[0][0]))
            angles[1][2] = math.atan2(matrix[1][0] / math.cos(angles[1][0]), matrix[0][0] / math.cos(angles[1][0]))

            return angles if not in_angles else angles * 180 / math.pi

        else:
            # phi = anything, let it be 0
            phi, theta, psi = 0, 0, 0
            if matrix[2][0] == -1:
                theta = math.pi / 2
                psi = phi + math.atan2(matrix[0][1], matrix[0][2])
            else:
                theta = -math.pi / 2
                psi = -phi + math.atan2(-matrix[0][1], -matrix[0][2])
            return np.array([[theta, psi, phi]])

    @staticmethod
    def calc_matrices(before, after, l=0):

        xtx = before.T @ before
        weigths = np.linalg.inv(xtx + np.eye(xtx.shape[0]) * l) @ before.T @ after

        return weigths[:3, :], weigths[-1, :]  # M, b

    def _read(self):
        try:
            self._main = self._manager.get_points(self._mainfile)
            if len(self._main) != self._points_in_row*self._rows:
                raise InvalidFormatError("Количество точек не совпадает с заявленным")
        except (InvalidFormatError, AttributeError) as e:
            self._main = None

        for fname in self._files:
            try:
                self._original_points.append(self._manager.get_points(fname))
                if len(self._original_points[-1]) != self._points_in_row * self._rows:
                    raise InvalidFormatError("Количество точек не совпадает с заявленным")
            except (InvalidFormatError, AttributeError) as e:
                self._original_points = []

    def calculate(self):
        """
        takes original points, calculates rotation matrices, movement matrices,
        angles, new position for every fame of deformed points
        """
        # !!! check if read data
        num_of_rows = 3
        points_in_row = self._points_in_row
        l = 0

        print(f"main: {self._main}")
        before = self._make_matrices(self._main, num_of_rows, points_in_row)
        for i, frame in enumerate(self._original_points):
            after = np.array(frame[:num_of_rows * points_in_row])
            M, b = self.calc_matrices(before, after, l)
            self._frame_info[i] = [M, b, self.compute_angels(M, True)]
            self._moved_points.append(self._main @ M + b)
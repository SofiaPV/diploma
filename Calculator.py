import numpy as np
import math
from FileManager import FileManager, InvalidFormatError
from scipy.spatial.transform import Rotation as R


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
        self._deformation_info = dict()

        self._rows = None
        self._points_in_row = None
        self._fixed_rows = None

    @property
    def deformation_info(self):
        return self._deformation_info

    @property
    def fixed_rows(self):
        return self._fixed_rows

    @fixed_rows.setter
    def fixed_rows(self, new_value):
        try:
            self._fixed_rows = int(new_value)
        except ValueError:
            self._fixed_rows = None
            raise ValueError("fixed_rows должно быть целым числом")
        except Exception as e:
            print(f"Что-то пошло не так: {e}")
            self._fixed_rows = None

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
        self._main = None

    @files.setter
    def files(self, new):
        self._files = new
        self._original_points = []

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

        #r = R.from_matrix(matrix)
        #euler = r.as_euler('zyx', degrees=True)  # если порядок ZYX, то сначала X, потом Y, потом Z
        #print(euler)
        #return euler

        #print(np.linalg.det(matrix))
        if matrix[2][0] != 1 and matrix[2][0] != -1:

            angles = np.array([[0., 0., 0.], [0., 0., 0.]])

            # theta
            #print(matrix[2][0])
            angles[0][0] = -math.asin(max(-1, min(1, matrix[2][0])))
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
            self._main = None
            self._main = self._manager.get_points(self._mainfile)
            if len(self._main) != self._points_in_row*self._rows:
                raise InvalidFormatError("Количество точек не совпадает с заявленным")
        except (InvalidFormatError, AttributeError) as e:
            self._main = None

        self._original_points = []
        for fname in self._files:
            try:
                self._original_points.append(self._manager.get_points(fname))
                if len(self._original_points[-1]) != self._points_in_row * self._rows:
                    raise InvalidFormatError("Количество точек не совпадает с заявленным")
            except (InvalidFormatError, AttributeError) as e:
                self._original_points = []

    def _calc_info(self, p1, p2):
        """
        :param p1: original points (moved to fit moved points)
        :param p2: moved points
        :return:
        """

        # making np.arrays for easy calculations
        p1 = np.array(p1)
        p2 = np.array(p2)

        # centroids
        cent1 = p1.mean(axis=0)
        cent2 = p2.mean(axis=0)

        # Making points centered
        centered1 = p1 - cent1
        centered2 = p2 - cent2

        # SVD
        _, _, vh1 = np.linalg.svd(centered1)
        _, _, vh2 = np.linalg.svd(centered2)

        # f(t) = centroid + t*direction
        direction1 = vh1[0]
        direction2 = vh2[0]

        # computing alpha
        alpha = np.dot(direction1, direction2) / (np.linalg.norm(direction1) * np.linalg.norm(direction2))
        alpha_rad = np.arccos(np.clip(alpha, -1.0, 1.0))
        anpha_deg = np.degrees(alpha_rad)
        #print(f"Угол: {anpha_deg} градусов")

        # searching for a plane
        n = np.cross(direction1, direction2)
        d = -n[0]*cent1[0] - n[1]*cent1[1] - n[2]*cent1[2]
        #print(f"Уравнение плоскости: {n[0]}x + {n[1]}y + {n[2]}z + {d} = 0")
        #print(f"Входит ли туда вторая точка: {n[0]*cent2[0]+n[1]*cent2[1]+n[2]*cent2[2]+d}=0?")

        # finding dx, dy
        vec = cent2 - cent1
        theta = np.dot(direction1, vec) / (np.linalg.norm(direction1) * np.linalg.norm(vec))
        theta = np.arccos(np.clip(theta, -1.0, 1.0))
        #print(f"угол между вектором разницы средних и направлением изначального сечения: {np.degrees(theta)}")

        dir1_norm = direction1 / np.linalg.norm(direction1)
        y_normal = np.cross(n, direction1)
        y_norm = y_normal / np.linalg.norm(y_normal)
        dx = np.linalg.norm(vec) * np.cos(theta) #* np.sign(np.dot(vec, dir1_norm))

        # TODO: remove new logic
        #print(f"shape: {np.array(self._moved_points).shape}")
        vec_x = np.array(self._moved_points[-1][self._points_in_row]) - np.array(self._moved_points[-1][0])
        vec_y = np.array(self._moved_points[-1][self._points_in_row+1]) - np.array(self._moved_points[-1][0])
        #print(f"{vec_x=}, {vec_y=}")
        vec_z = np.cross(vec_x, vec_y)
        #print(f"{vec_z=}")
        # TODO: end of new logic, next line uses it
        dy = np.linalg.norm(vec) * np.sin(theta) * np.sign(np.dot(vec, vec_z))  #* np.sign(np.dot(vec, y_norm))
        #print(f"dy: {dy * y_norm}")
        #dy = np.dot(y_normal, vec) / np.linalg.norm(y_normal)

        #print(f"dx: {dx}, dy: {dy}\n")
        return {"angle": anpha_deg, "dx": dx, "dy": dy, "directions": [direction1, direction2]}

    def calculate(self):
        """
        takes original points, calculates rotation matrices, movement matrices,
        angles, new position for every fame of deformed points
        """
        # !!! check if read data
        num_of_rows = self._fixed_rows
        points_in_row = self._points_in_row
        l = 0
        self._moved_points = []
        self._deformation_info = dict()

        before = self._make_matrices(self._main, num_of_rows, points_in_row)
        #print(f"_original_points: {len(self._original_points)}")
        for i, frame in enumerate(self._original_points):
            after = np.array(frame[:num_of_rows * points_in_row])
            M, b = self.calc_matrices(before, after, l)
            self._frame_info[i] = [np.round(M, 3), np.round(b, 3),
                                   np.round(self.compute_angels(M, True), 3)]
            self._moved_points.append(self._main @ M + b)

            self._deformation_info[i] = dict()
            for j in range(num_of_rows, self._rows):
                #print(f"Ряд {j} Кадр {i}")
                info = self._calc_info(self._moved_points[-1][j * points_in_row: (j+1) * points_in_row],
                                frame[j * points_in_row: (j+1) * points_in_row])
                self._deformation_info[i][j] = info

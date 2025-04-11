class InvalidFormatError(Exception):
    pass

class FileManager:

    def __init__(self, mainfile=None, files=None):
        self._mainfile_name = mainfile
        self._files = files

    @staticmethod
    def get_points(filename):
        """
        :param filename: a file to read
        :return: an array [[x, y, z], ...] presented in file
        """
        f = open(filename, 'r')  # !!! .txt only
        data = []

        for i, line in enumerate(f):
            line = line.strip()
            parts = line.split('\t')
            if len(parts) != 3:
                raise InvalidFormatError(f"Не удалось выделить три числа в строке {i}. "
                                         f"Проверьте формат чисел.")
            try:
                data.append(list(map(float, parts)))
            except ValueError:
                raise InvalidFormatError(f"Ошибка в строке {i}: не удаётся преобразовать значения в числа.")


        for line in f:
            data.append(list(map(float, line.split('\t'))))  # !!! only '\t' format
        f.close()
        return data


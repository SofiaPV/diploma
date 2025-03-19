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
        for line in f:
            data.append(list(map(float, line.split('\t'))))  # !!! only '\t' format
        f.close()
        return data


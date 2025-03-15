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

    @staticmethod
    def spit_file_data(filename=None, data=None):
        """
        :param filename: a filename to read and to split into dimensions
                         if None, array [[x1, y1, z1], ...] passed into
                         data
        :param data: array to split, if None than must give a filename with
                     data
        :return: x:List, y:List, z:List
        """
        if filename:
            data = FileManager.get_points(filename)
        if data is None:
            return

        x, y, z = [], [], []
        for line in data:
            x.append(line[0])
            y.append(line[1])
            z.append(line[2])
        return x, y, z

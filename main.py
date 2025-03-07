import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox,
                             QFileDialog, QListView, QSizePolicy, QVBoxLayout)
from PyQt5.QtCore import QStringListModel
from PyQt5 import uic, QtCore

#from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
import plotly.graph_objects as go


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # general settings
        self.setWindowTitle("Диплом")
        self.showMaximized()
        uic.loadUi("first.ui", self)

        # variables definition
        self._main_file_name = None
        self._directory = None
        self._files = None

        # plotly web browser
        #self._browser = QWebEngineView(self.main_graphic)
        #vlayout = QVBoxLayout(self.main_graphic)
        #vlayout.addWidget(self._browser)
        #self._make_graphics()

        # connect buttons to functions
        self.open_mainfile.clicked.connect(self.browse_file)
        self.open_directory.clicked.connect(self.browse_directory)

        # listView settings
        self._model = QStringListModel()
        self.file_view.setModel(self._model)

    def browse_file(self):
        filename = ''
        try:
            filename = QFileDialog.getOpenFileName(self, 'Выберите файл')
        except Exception as e:
            print(f"Error while choosing file occured: {e}")
            return

        if filename[0] == '':
            return

        self.mainfile.setText(filename[0].split('/')[-1])  # !!! нормальный сплит
        self._main_file_name = filename[0]

    def browse_directory(self):
        try:
            self._directory = str(QFileDialog.getExistingDirectory(self, "Выберите папку"))
        except Exception as e:
            print(f"Error while choosing directory occured: {e}")
            return

        if self._directory == '':
            return

        self._files = self.read_directory(self._directory)
        current_files = []
        for file in self._files:
            current_files.append(file.split('\\')[-1])

        self._model.setStringList(current_files)

    def _make_graphics(self):
        fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 5, 6], mode='lines+markers')])
        html_content = fig.to_html(full_html=False, include_plotlyjs='cdn')
        #try:
        #    self._browser.setHtml(html_content)
        #except Exception as e:
        #    print(f'Error: {e}')

    @staticmethod
    def read_directory(directory):
        filenames = []
        for element in os.listdir(directory):
            file_path = os.path.join(directory, element)
            if os.path.isfile(file_path):
                filenames.append(file_path)
        return filenames


def main():
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = \
        'C:\\София\\София\\python\\UI_diploma_1\\.venv\\Lib\\site-packages\\PyQt5\\Qt5\\plugins\\platforms'

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

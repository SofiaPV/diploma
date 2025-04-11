import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt6.QtCore import QStringListModel
from PyQt6 import uic
from PyQt6.QtWebEngineWidgets import QWebEngineView

from Visualiser import Visualiser
from SaveDialog import SaveDialog


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
        self._visualiser = Visualiser()

        # plotly web browser
        self._data_view = QWebEngineView()
        self._calculations_view = QWebEngineView()
        self.tabWidget.addTab(self._data_view, "Данные")
        self.tabWidget.addTab(self._calculations_view, "Вычисления")

        # connect buttons to functions
        self.open_mainfile.clicked.connect(self.browse_file)
        self.open_directory.clicked.connect(self.browse_directory)
        self.saveButton.triggered.connect(self._open_dialog)
        self.calculate_button.clicked.connect(self._make_graphics)

        # connecting signals
        self.rows.editingFinished.connect(self._num_of_rows_handler)
        self.points_in_row.editingFinished.connect(self._num_of_points_handler)
        self.fixed_rows.editingFinished.connect(self._fixed_rows_handler)

        #  add tool tips
        self.open_mainfile.setToolTip("Выберите файл с точками (x, y, z) до начала эксперимента. "
                                      "Формат данных: x\\ty\\tz\\t\\n")
        self.open_directory.setToolTip("Выберите папку с файлами, содержащие точки (x, y, z) в процессе эксперимента. "
                                      "Формат данных: x\\ty\\tz\\t\\n")

        # listView settings
        self._model = QStringListModel()
        self.file_view.setModel(self._model)

    def _fixed_rows_handler(self):
        try:
            self._visualiser.calculator.fixed_rows = self.fixed_rows.text()
        except Exception as e:
            self._message(False, "Ошибка!", "Вы должны ввести целое число в "
                                            "поля 'Число рядов', 'Точек в рядах' и 'Неподвижные ряды'.")

    def _num_of_points_handler(self):
        try:
            self._visualiser.calculator.points_in_row = self.points_in_row.text()
        except Exception as e:
            self._message(False, "Ошибка!", "Вы должны ввести целое число в "
                                            "поля 'Число рядов', 'Точек в рядах' и 'Неподвижные ряды'.")

    def _num_of_rows_handler(self):
        try:
            self._visualiser.calculator.rows = self.rows.text()
        except Exception as e:
            self._message(False, "Ошибка!", "Вы должны ввести целое число в "
                                            "поля 'Число рядов' и 'Точек в рядах'")


    def _open_dialog(self):
        dialog = SaveDialog(self)
        dialog.save_signal.connect(self._save_data)
        dialog.exec()

    def _message(self, success, message, informative_message):
        msg = QMessageBox()
        msg.setStyleSheet(self.styleSheet())

        if success:
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Успех")
        else:
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Ошибка")

        msg.setText(message)
        msg.setInformativeText(informative_message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)

        msg.exec()

    def _save_data(self, path, save_orig, save_calced):
        frame_data = self._visualiser.calculator.frame_info
        if len(frame_data) == 0:
            self._message(False, "Ошибка!", "Данные еще не были подсчитаны. "
                                           "Загрузите файлы или дождитесь окончания подсчетов.")
            return

        #  Writing fame data (M, b, angles) into file
        for key, arr in frame_data.items():
            with open(f'{path}/frame{key}_data.txt', 'w') as f:
                f.write(f"Rotation Matrix: {arr[0].tolist()}\n")
                f.write(f"Bias: {arr[1].tolist()}\n")
                f.write(f"Angles: {arr[2].tolist()}\n")

        if save_orig:
            with open(f'{path}/orig.html', 'w') as f:
                f.write(self._visualiser.orig_html)

        if save_calced:
            with open(f'{path}/calced.html', 'w') as f:
                f.write(self._visualiser.calced_html)

        self._message(True, "", "Данные успешно сохранены.")

    def browse_file(self):
        if self._visualiser.calculator.rows is None or self._visualiser.calculator.points_in_row is None:
            self._message(False, "Ошибка!", "Вначале укажите число рядов и точек в "
                                            "каждом ряду в полях выше")
            return

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
        self._visualiser.mainfile_name = filename[0]

    def browse_directory(self):
        if self._visualiser.calculator.rows is None or self._visualiser.calculator.points_in_row is None:
            self._message(False, "Ошибка!", "Вначале укажите число рядов и точек в "
                                            "каждом ряду в полях выше")
            return

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
        self._visualiser.files = self._files

    def _make_graphics(self):

        message = "Вы не указали:\n"
        if self._visualiser.files is None:
            message += "* папку с файлами эксперимента\n"
        if self._visualiser.mainfile_name is None:
            message += "* файл с опорными точками\n"
        if self._visualiser.calculator.fixed_rows is None:
            message += "* кол-во неподвижных рядов\n"
        if message != "Вы не указали:\n":
            self._message(False, "Ошибка!", message)
            return
        if self._visualiser.calculator.rows < self._visualiser.calculator.fixed_rows:
            self._message(False, "Ошибка!", "Число неподвижных рядов не может "
                                            "превышать количество рядов")
            return

        self._message(True, "", "Данные обрабатываются. Пожалуйста, подождите.")
        try:
            html_content = self._visualiser.visualize_original_data()
        except ValueError as e:
            self._message(False, "Ошибка!", f"Программа не смогла интерпретировать "
                                            f"данные. Проверьте формат входных файлов и/или количество точек в них.")
            return
        self._data_view.setHtml(html_content)
        html2 = self._visualiser.visualize_calculations()
        self._calculations_view.setHtml(html2)

    @staticmethod
    def read_directory(directory):
        filenames = []
        for element in os.listdir(directory):
            file_path = os.path.join(directory, element)
            if os.path.isfile(file_path):
                filenames.append(file_path)
        return filenames


def main():
    #os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = \
    #    'C:\\София\\София\\python\\UI_diploma_1\\.venv\\Lib\\site-packages\\PyQt5\\Qt5\\plugins\\platforms'

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

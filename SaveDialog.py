from PyQt6.QtWidgets import QFileDialog, QDialog, QMessageBox
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal


class SaveDialog(QDialog):

    save_signal = pyqtSignal(str, bool, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("saveDialog.ui", self)

        self._directory = None
        self._saveOrig = False
        self._saveCalc = False

        self.chooseFolderButton.clicked.connect(self._choose_folder)
        self.saveDataButton.stateChanged.connect(self._saveOrigFunc)
        self.saveCalcButton.stateChanged.connect(self._saveCalcFunc)
        self.saveButton.clicked.connect(self._save)

    def _choose_folder(self):
        try:
            self._directory = str(QFileDialog.getExistingDirectory(self, "Выберите папку"))
        except Exception as e:
            print(f"Error while choosing directory occured: {e}")
            return
        self.folderName.setText(self._directory)

    def _saveOrigFunc(self, state):
        self._saveOrig = True if state == 2 else False

    def _saveCalcFunc(self, state):
        self._saveCalc = True if state == 2 else False

    def _save(self):
        if self._directory is not None:
            self.save_signal.emit(self._directory, self._saveOrig, self._saveCalc)
            self.accept()
        else:
            self._message()

    def _message(self):
        msg = QMessageBox()
        msg.setStyleSheet("""
                QMessageBox{
                    background-color: rgb(45, 50, 80);
                    color: rgb(255, 255, 255);
                    font: 10px;
                }
                
                QMessageBox QPushButton {	
                    background-color: rgb(249, 177, 122);
                    border-radius: 5px; 
                    border: none;  
                    width: 20px; 
                    height: 20px;
                }
                
                QMessageBox QLabel {
                    color: rgb(255, 255, 255); 
                }

                QMessageBox {
                    font-size: 10pt;
                    color: rgb(255, 255, 255);
                }
        """)

        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Ошибка!")

        msg.setText("Ошибка!")
        msg.setInformativeText("Не выбрано место сохранения.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)

        msg.exec()

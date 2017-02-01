from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QLabel


def wave_dialog(png_name):
    image = QPixmap(png_name)

    Dialog = QDialog()
    Dialog.setWindowModality(Qt.WindowModal)
    Dialog.setObjectName("Dialog")
    Dialog.setWindowTitle("Wave form")

    Dialog.resize(image.width(), image.height())

    waveform = QLabel(Dialog)
    waveform.setPixmap(image)
    waveform.show()
    Dialog.exec_()
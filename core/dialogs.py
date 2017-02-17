#!/usr/bin/env python
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QHBoxLayout, QTableWidget, QTableWidgetItem, QToolButton, QVBoxLayout, QWidget,
    QLabel, QDialog, QFileDialog, QProgressBar, QTextEdit)

from core.config import fetch_options, update_music_paths
from core.downloader import YoutubeDownloader


def wave_dialog(png_name):
    image = QPixmap(png_name)

    Dialog = QDialog()
    Dialog.setWindowModality(Qt.WindowModal)
    Dialog.setWindowTitle(png_name)

    Dialog.resize(image.width(), image.height())

    waveform = QLabel(Dialog)
    waveform.setPixmap(image)
    waveform.show()
    Dialog.exec_()


class DownloadManager(QWidget):
    def __init__(self, parent=None):

        QWidget.__init__(self, parent)
        self.setObjectName("Download Manager")
        self.setWindowTitle("Download Manager")
        self.setWindowModified(True)

        self.links_to_download = QTextEdit()
        self.download_status = QProgressBar()

        self.download_button = QToolButton(clicked=self.download)
        self.download_button.setText("Download")
        self.download_label = QLabel()

        download_controls = QHBoxLayout()
        download_controls.addWidget(self.download_button)
        download_controls.addWidget(self.download_label)

        download_layout = QVBoxLayout()
        download_layout.addWidget(self.links_to_download)
        download_layout.addWidget(self.download_status)
        download_layout.addLayout(download_controls)

        self.setLayout(download_layout)

    def set_refresh(self, refresh):
        self.refresh = refresh

    def download(self):
        yt = YoutubeDownloader(self.links_to_download.toPlainText().split(','),
                               self.download_label, self.download_button,
                               self.download_status, self.refresh)
        yt.begin()
        self.links_to_download.clear()



class LibrariesManager(QWidget):

    def __init__(self, parent=None):

        QWidget.__init__(self, parent)

        self.setObjectName("Music Libraries")
        self.setWindowTitle("Music Libraries")
        self.setWindowModified(True)
        #self.setWindowModality(Qt.WA_WindowModified)
        self.libraries = QTableWidget()

        add_paths = QToolButton(clicked=self.add_library)
        add_paths.setText("Add")
        remove_paths = QToolButton(clicked=self.remove_library)
        remove_paths.setText("Remove")
        save_paths = QToolButton(clicked=self.done_library)
        save_paths.setText("Done")

        self.items = 0
        self.libraries.setRowCount(self.items)
        self.libraries.setColumnCount(1)
        self.libraries.horizontalHeader().setStretchLastSection(True)
        self.libraries.horizontalHeader().hide()
        paths = fetch_options()['paths']['music_path'].split(';')
        for path in paths:
            if len(path) > 1:
                self.add_to_table(path)

        controls_l = QHBoxLayout()
        controls_l.setAlignment(Qt.AlignLeft)
        controls_l.addWidget(add_paths)
        controls_l.addWidget(remove_paths)
        controls_l.addWidget(save_paths)

        main_l = QVBoxLayout()
        main_l.addWidget(self.libraries)
        main_l.addLayout(controls_l)
        self.setLayout(main_l)

    def add_to_table(self, path):
        self.libraries.setRowCount(self.items + 1)
        self.libraries.setItem(self.items, 0, QTableWidgetItem(path))
        self.items += 1

    def add_library(self):
        self.folder_dialog = QFileDialog.getExistingDirectory(self, 'Select Folder')
        self.libraries.setRowCount(self.items + 1)
        print(self.folder_dialog)
        self.libraries.setItem(self.items, 0, QTableWidgetItem(self.folder_dialog))
        self.items += 1

    def remove_library(self):
        for index in sorted(self.libraries.selectedIndexes())[::-1]:
            self.libraries.removeRow(index.row())

    def done_library(self):
        paths = [self.libraries.model().index(path, 0).data() for path in range(self.libraries.rowCount())]
        update_music_paths(paths)
        self.close()
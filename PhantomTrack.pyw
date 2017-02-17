#!/usr/bin/env python

import sys
# Third party libraries
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction
# Core libraries
from core.dialogs import LibrariesManager, DownloadManager
from core.config import fetch_options
from core.player import MusicPlayer


class MainApplication(QMainWindow):
    def __init__(self):
        QApplication.__init__(self)
        menubar = self.menuBar()
        # TODO : refactor this.
        fileMenu = menubar.addMenu('&Music')
        edit_libraries_action = QAction('&Library folders', self)
        edit_libraries_action.triggered.connect(self.call_libraries_manager)
        download_action = QAction('&Download music', self)
        download_action.triggered.connect(self.call_download_manager)
        fileMenu.addAction(edit_libraries_action)
        fileMenu.addAction(download_action)

        options = fetch_options()
        print(options['paths'])
        if len(options['paths']['music_path']) < 1:
            self.call_libraries_manager()

    def call_download_manager(self):
        self.download_manager = DownloadManager()
        self.download_manager.set_refresh(self.widget.refresh)
        self.download_manager.show()

    def call_libraries_manager(self):
        self.libraries_manager = LibrariesManager()
        self.libraries_manager.show()

    def set_up_gui(self, widget):
        self.widget = widget
        self.setCentralWidget(widget)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(15, 15, 15))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
    palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(palette)

    music_player = MusicPlayer()

    main_app = MainApplication()
    main_app.setWindowTitle("Phantom Track")
    main_app.set_up_gui(music_player)
    main_app.show()
    sys.exit(app.exec_())

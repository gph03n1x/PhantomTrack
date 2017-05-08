#!/usr/bin/env python
import sys
import logging
# Third party libraries
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette, QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction
# Core libraries
from core.dialogs import LibrariesManager, DownloadManager
from core.config import fetch_options
from core.player import MusicPlayer
from core.playlist.dialog import PlaylistManager


class MainApplication(QMainWindow):
    def __init__(self, options):
        """
        Initializes the main window with the Music libraries manager
        and the download manager in the menu bar. If there are no music
        paths defined it hides itself.
        """
        QApplication.__init__(self)

        self.options = options
        self.do_not_refresh = False

        menu_bar = self.menuBar()
        music_menu = menu_bar.addMenu('&Music')
        edit_libraries_action = QAction('&Library folders', self)
        edit_libraries_action.triggered.connect(self.call_libraries_manager)
        download_action = QAction('&Download music', self)
        download_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_D))
        download_action.triggered.connect(self.call_download_manager)
        playlist_action = QAction('&Configure playlist', self)
        playlist_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_P))
        playlist_action.triggered.connect(self.call_playlist_manager)
        music_menu.addAction(edit_libraries_action)
        music_menu.addAction(download_action)
        music_menu.addAction(playlist_action)


        if len(self.options['paths']['music_path']) < 1:
            self.do_not_refresh = True
            self.hide()

    def begin(self):
        """
        Checks the music paths and there none defined it
        calls the Music libraries manager
        :return:
        """
        if len(self.options['paths']['music_path']) < 1:
            self.call_libraries_manager()
        else:
            self.show()

    def set_up_gui(self):
        """
        Sets the player widget as the main widget of the application
        and if the user had music libraries defined already then
        refreshes (initializes) the playlist
        :param widget:
        :return:
        """
        self.widget = MusicPlayer(self)
        self.setCentralWidget(self.widget)
        if not self.do_not_refresh:
            self.widget.refresh()
            self.widget.change_thumbnail(0)

    def call_download_manager(self, links=None):
        """
        Shows a download manager window
        :return:
        """
        self.download_manager = DownloadManager()
        self.download_manager.set_refresh(self.widget.refresh)
        self.download_manager.add_links(links)
        self.download_manager.show()
        self.download_manager.links_to_download.setFocus()

    def call_libraries_manager(self):
        """
        Shows a music libraries manager window
        :return:
        """
        self.libraries_manager = LibrariesManager()
        self.libraries_manager.set_app_associations(self, self.widget)
        self.libraries_manager.show()

    def call_playlist_manager(self):
        self.playlist_manager = PlaylistManager()
        self.playlist_manager.set_app_associations(self, self.widget)
        self.playlist_manager.show()


if __name__ == "__main__":
    # TODO: comment the code.
    logging.basicConfig(filename="error.log", level=logging.INFO)
    logger = logging.getLogger(__name__)
    options = fetch_options()

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

    main_app = MainApplication(options)
    main_app.setWindowTitle("Phantom Track")
    main_app.set_up_gui()
    main_app.begin()

    sys.exit(app.exec_())

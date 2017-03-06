from os import listdir
from os.path import isfile, join

from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QHBoxLayout, QTableWidget, QTableWidgetItem, QToolButton, QVBoxLayout, QWidget, QCompleter,
    QLabel, QDialog, QFileDialog, QProgressBar, QLineEdit)

from core.config import fetch_options, update_music_paths
from core.downloader import YoutubeDownloader
from core.playlist.storage import create_playlist, read_playlist

class PlaylistManager(QWidget):
    def __init__(self, parent=None):

        QWidget.__init__(self, parent)
        self.setObjectName("Playlist Manager")
        self.setWindowTitle("Playlist Manager")

        self.libraries = QTableWidget()
        self.items = 0
        self.libraries.setRowCount(self.items)
        self.libraries.setColumnCount(1)
        self.libraries.horizontalHeader().setStretchLastSection(True)
        self.libraries.horizontalHeader().hide()


        paths = fetch_options()['paths']['music_path'].split(';')
        self.music_files = {}

        for path in paths:
            for item in listdir(path):
                if isfile(join(path, item)) and item.endswith(".mp3"):
                    self.music_files[item] = join(path, item)
                    self.libraries.setRowCount(self.items+1)
                    self.libraries.setItem(self.items, 0, QTableWidgetItem(item))
                    self.items += 1

        self.playlist = QTableWidget()
        self.playlist_items = 0
        self.playlist.setRowCount(self.playlist_items)
        self.playlist.setColumnCount(1)
        self.playlist.horizontalHeader().setStretchLastSection(True)
        self.playlist.horizontalHeader().hide()

        self.add_button = QToolButton(clicked=self.add_to_table)
        self.add_button.setText("+")
        self.remove_button = QToolButton(clicked=self.remove_from_table)
        self.remove_button.setText("-")

        self.download_label = QLabel()

        self.song_search = QLineEdit()
        self.song_search.textChanged.connect(self.search)
        self.song_search.setClearButtonEnabled(True)

        self.playlist_name = QLineEdit()
        completer = QCompleter()
        self.available_playlist = QStringListModel()
        completer.setModel(self.available_playlist)
        self.playlist_name.setCompleter(completer)
        self.refresh_lists()

        self.load_button = QToolButton(clicked=self.load)
        self.load_button.setText("Load")

        self.save_button = QToolButton(clicked=self.save)
        self.save_button.setText("Save")

        # Shortcuts

        # Layouts

        playlist_controls = QVBoxLayout()
        playlist_controls.addWidget(self.add_button)
        playlist_controls.addWidget(self.remove_button)

        playlist_layout = QHBoxLayout()
        playlist_layout.addWidget(self.libraries)
        playlist_layout.addLayout(playlist_controls)
        playlist_layout.addWidget(self.playlist)

        action_layout = QHBoxLayout()
        action_layout.addWidget(self.playlist_name)
        action_layout.addWidget(self.load_button)
        action_layout.addWidget(self.save_button)

        manager_layout = QVBoxLayout()
        manager_layout.addLayout(playlist_layout)
        manager_layout.addWidget(self.song_search)
        manager_layout.addLayout(action_layout)

        self.setLayout(manager_layout)

    def search(self, part_of_song):
        for index in range(self.playlist.rowCount()):
            item = self.playlist.model().index(index, 0).data().lower()
            self.playlist.setRowHidden(index, part_of_song.lower() not in item)

        for index in range(self.libraries.rowCount()):
            item = self.libraries.model().index(index, 0).data().lower()
            self.libraries.setRowHidden(index, part_of_song.lower() not in item)


    def set_app_associations(self, app, widget):
        self.app = app
        self.widget = widget

    def refresh_lists(self):
        path = fetch_options()['paths']['playlist']

        self.available_playlist.setStringList([ item.split('.')[0] for item in listdir(path)
                                                if isfile(join(path, item)) and item.endswith(".lst")])
        print([ item.split('.')[0] for item in listdir(path)
                                                if isfile(join(path, item)) and item.endswith(".lst")])

    def add_to_table(self):
        for index in sorted(self.libraries.selectedIndexes())[::-1]:
            # TODO: care of duplicates
            item = self.libraries.item(index.row(), 0)
            self.playlist.setRowCount(self.playlist_items + 1)
            self.playlist.setItem(self.playlist_items, 0, QTableWidgetItem(item))
            self.playlist_items += 1

    def remove_from_table(self):
        self.playlist_items -= len(self.playlist.selectedIndexes())
        for index in sorted(self.playlist.selectedIndexes())[::-1]:
            self.playlist.removeRow(index.row())

    def save(self, refresh):
        if self.playlist_name.text():
            playlist =[]
            for path in range(self.playlist.rowCount()):
                item = self.playlist.model().index(path, 0).data()
                if item in self.music_files.keys():
                    playlist.append(self.music_files[item])
                else:
                    playlist.append(item)

            create_playlist(self.playlist_name.text(), playlist)
            self.refresh_lists()
            self.widget.refresh_lists()

    def load(self):
        if self.playlist_name.text():
            songs = read_playlist(self.playlist_name.text()).split('\n')
            if songs:
                self.playlist.clear()
                self.playlist_items = 0
                self.playlist.setRowCount(self.playlist_items)
                for song in songs:
                    self.playlist.setRowCount(self.playlist_items+1)
                    self.playlist.setItem(self.playlist_items, 0, QTableWidgetItem(song))
                    self.playlist_items += 1
                # TODO: hack
                self.playlist.removeRow(self.playlist_items-1)


    def done(self):
        pass
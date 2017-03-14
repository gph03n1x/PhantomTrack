#!/usr/bin/env python
from os import listdir
from os.path import isfile, join, exists
# Third party libraries
from PyQt5.QtGui import QPixmap, QKeySequence, QPalette, QColor
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtWidgets import (QHBoxLayout, QListView, QSlider, QStyle, QLineEdit, QShortcut, QComboBox,
                             QToolButton, QVBoxLayout, QWidget, QLabel)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
# Core libraries
from core.analysis.analysis import WaveConverter
from core.analysis.dialog import WaveGraphic
from core.playlist.model import PlaylistModel
from core.config import fetch_options, similar
from core.playlist.storage import read_playlist

options = fetch_options()
FFMPEG_BIN = options['paths']['ffmpeg_bin']
THUMBNAILS = options['paths']['thumbnails']
THUMB_WIDTH = options['thumbnail']['width']
THUMB_HEIGHT = options['thumbnail']['height']


class MusicPlayer(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.jumping = False
        self.blocked = False
        self.durations = {}
        self.playback_value = 0

        self.text = ["None", "Repeat", "Random"]
        self.playlist_list = []
        self.values = [QMediaPlaylist.Loop, QMediaPlaylist.CurrentItemInLoop, QMediaPlaylist.Random]

        # Thumbnail widget
        self.image_label = QLabel()

        self.figure = plt.figure()
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        #self.figure.axis('off')


        # Control widgets
        self.playButton = QToolButton(clicked=self.play)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        self.stopButton = QToolButton(clicked=self.stop)
        self.stopButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stopButton.setEnabled(False)

        self.playbackButton = QToolButton(clicked=self.playback_mode)
        self.playbackButton.setText(self.text[0])

        self.nextButton = QToolButton(clicked=self.next_song)
        self.nextButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaSkipForward))

        self.previousButton = QToolButton(clicked=self.previous_song)
        self.previousButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaSkipBackward))

        self.muteButton = QToolButton(clicked=self.mute_clicked)
        self.muteButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaVolume))

        self.volumeSlider = QSlider(Qt.Horizontal, sliderMoved=self.change_volume)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setPageStep(1)
        self.volumeSlider.setValue(50)

        #self.waveformButton = QToolButton(clicked=self.get_waveform)
        #self.waveformButton.setText("Waveform")

        # Player and playlist setup

        self.player = QMediaPlayer()
        self.player.setVolume(50)

        self.playlist = QMediaPlaylist()
        self.playlist.setPlaybackMode(self.values[0])
        self.playlist.setCurrentIndex(1)

        self.player.setPlaylist(self.playlist)

        self.playlistModel = PlaylistModel()
        self.playlistModel.setPlaylist(self.playlist)

        self.playlistView = QListView()
        self.playlistView.setModel(self.playlistModel)
        self.playlistView.setCurrentIndex(
            self.playlistModel.index(self.playlist.currentIndex(), 0))
        self.playlistView.activated.connect(self.jump)

        self.playlist.currentIndexChanged.connect(
            lambda position: self.change_thumbnail(position)
        )

        song_search = QLineEdit()
        song_search.textChanged.connect(self.search)
        song_search.setClearButtonEnabled(True)

        # Playlist
        self.playlist_name = QComboBox()
        self.playlist_name.currentTextChanged.connect(self.switch_playlist)
        self.refresh_lists()

        self.up_button = QToolButton(clicked=self.move_up)
        self.up_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
        self.down_button = QToolButton(clicked=self.move_down)
        self.down_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))

        # Soundwave

        self.wg = WaveGraphic()
        self.wg.hide()

        # Shortcuts
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_F), self, song_search.setFocus)

        # Layouts setup

        playlist_layout = QHBoxLayout()
        playlist_layout.addWidget(self.playlist_name)
        playlist_layout.addWidget(self.up_button)
        playlist_layout.addWidget(self.down_button)

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self.stopButton)
        control_layout.addWidget(self.previousButton)
        control_layout.addWidget(self.playButton)
        control_layout.addWidget(self.nextButton)
        control_layout.addWidget(self.muteButton)
        control_layout.addWidget(self.volumeSlider)
        control_layout.addWidget(self.playbackButton)
        #control_layout.addWidget(self.waveformButton)

        display_layout = QVBoxLayout()
        display_layout.addWidget(song_search)
        display_layout.addWidget(self.playlistView)
        display_layout.addLayout(playlist_layout)

        music_layout = QVBoxLayout()
        music_layout.addWidget(self.image_label)
        music_layout.addLayout(control_layout)

        main_layout = QHBoxLayout()
        main_layout.addLayout(music_layout)
        main_layout.addLayout(display_layout)

        main_2_layout = QVBoxLayout()
        main_2_layout.addLayout(main_layout)
        main_2_layout.addWidget(self.wg)

        self.setLayout(main_2_layout)



    def move_up(self):
        index = self.playlistView.currentIndex().row()
        if index - 1 >= 0:
            item, above = self.playlist.media(index), self.playlist.media(index - 1)
            self.playlist.removeMedia(index)
            self.playlist.removeMedia(index - 1)
            self.playlist.insertMedia(index - 1, item)
            self.playlist.insertMedia(index, above)
            self.blocked = True
            self.playlistView.setCurrentIndex(self.playlistModel.index(index - 1, 0))
            self.blocked = False
            self.stop()


    def move_down(self):
        index = self.playlistView.currentIndex().row()
        if index + 1 <= self.playlistModel.rowCount():
            item, below = self.playlist.media(index), self.playlist.media(index + 1)
            self.playlist.removeMedia(index + 1)
            self.playlist.removeMedia(index)
            self.playlist.insertMedia(index, below)
            self.playlist.insertMedia(index + 1, item)
            self.blocked = True
            self.playlistView.setCurrentIndex(self.playlistModel.index(index + 1, 0))
            self.blocked = False
            self.stop()

    def switch_playlist(self, current_text):
        self.playlist.clear()
        if current_text == "No Playlist":
            self.refresh()
        else:
            if read_playlist(current_text):
                songs = read_playlist(current_text).split('\n')
                for song in songs:
                    self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(song)))


    def search(self, part_of_song):
        for index in range(self.playlistModel.rowCount()):
            item = self.playlistModel.data(self.playlistModel.index(index, 0)).lower()
            self.playlistView.setRowHidden(index, part_of_song.lower() not in item)


    def change_thumbnail(self, position=0):

        self.playlistView.setCurrentIndex(self.playlistModel.index(position, 0))

        if self.playlistView.currentIndex().data() is None or self.blocked:
            return

        print("Casted")
        print(self.player.state())
        print(QMediaPlayer.PlayingState)
        if self.player.state() == QMediaPlayer.PlayingState:
            wc_ = WaveConverter(self.playlistView.selectedIndexes()[0].data(), self.wg.set_wav)
            wc_.convert()

        max_ratio = 0
        img = None

        for item in listdir(THUMBNAILS):
            if item.endswith('.jpg'):
                ratio = similar(item, self.playlistView.currentIndex().data().replace('.mp3', '.jpg'))
                if ratio > max_ratio:
                    max_ratio = ratio
                    img = item

        if img:
            p = QPixmap(THUMBNAILS + img)
            self.image_label.setPixmap(p.scaled(THUMB_WIDTH, THUMB_HEIGHT, Qt.KeepAspectRatio))

        #self.wg.animate()

    def refresh(self):
        # Change it so it will go to same song.
        paths = fetch_options()['paths']['music_path'].split(';')

        current_songs = [self.playlistModel.data(self.playlistModel.index(row, 0))
                     for row in range(self.playlistModel.rowCount()) ]

        for path in paths:
            for item in listdir(path):
                if isfile(join(path, item))and item.endswith(".mp3") and (item not in current_songs):
                    self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(join(path, item))))

    def refresh_lists(self):
        path = fetch_options()['paths']['playlist']
        self.playlist_name.clear()
        self.playlist_list = ["No Playlist"]
        self.playlist_name.addItem("No Playlist")
        for item in listdir(path):
            if isfile(join(path, item)) and item.endswith(".lst"):
                self.playlist_list.append(item.split('.')[0])
                self.playlist_name.addItem(item.split('.')[0])


    def playback_mode(self):
        # Normal -> Loop -> Random
        def up_value(value, max_value=3):
            if value+1 == max_value:
                return 0
            return value+1

        self.playback_value = up_value(self.playback_value)
        self.playlist.setPlaybackMode(self.values[self.playback_value])
        self.playbackButton.setText(self.text[self.playback_value])

    def jump(self, index):
        if index.isValid() and not self.blocked:
            self.playlist.setCurrentIndex(index.row())
            self.jumping = True
            self.play()

    def play(self):
        if self.blocked:
            return
        if self.player.state() != QMediaPlayer.PlayingState or self.jumping:
            self.player.play()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.jumping = False
        else:
            self.player.pause()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.stopButton.setEnabled(True)

    def change_volume(self, value):
        self.player.setVolume(value)

    def stop(self):
        if self.player.state() != QMediaPlayer.StoppedState:
            self.player.stop()
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.stopButton.setEnabled(False)
        self.wg.stop = True

    def next_song(self):
        self.playlist.next()
        self.playlistView.setCurrentIndex(
                self.playlistModel.index(self.playlist.currentIndex(), 0))

    def previous_song(self):
        self.playlist.previous()
        self.playlistView.setCurrentIndex(
                self.playlistModel.index(self.playlist.currentIndex(), 0))

    def mute_clicked(self):
        self.player.setMuted(not self.player.isMuted())
        self.muteButton.setIcon(
            self.style().standardIcon(
                QStyle.SP_MediaVolume if not self.player.isMuted()
                else QStyle.SP_MediaVolumeMuted
                )
            )
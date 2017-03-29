#!/usr/bin/env python
from os import listdir
from os.path import isfile, join, exists
# Third party libraries
from PyQt5.QtGui import QPixmap, QKeySequence
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtWidgets import (QHBoxLayout, QListView, QSlider, QStyle, QLineEdit, QShortcut, QComboBox,
                             QToolButton, QVBoxLayout, QWidget, QLabel, QMenu, QAction)

# Core libraries
from core.analysis.analysis import WaveConverter
from core.analysis.widget import WaveGraphic
from core.playlist.model import PlaylistModel
from core.config import fetch_options, similar
from core.playlist.storage import read_playlist
from core.recommendations.youtube import youtube_recommendations, getYoutubeURLFromSearch




class MusicPlayer(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.options = self.parent().options
        
        self.ffmpeg = self.options['paths']['ffmpeg_bin']
        self.thumbnails = self.options['paths']['thumbnails']
        self.thumb_width = self.options['thumbnail']['width']
        self.thumb_height = self.options['thumbnail']['height']

        self.jumping = False
        self.blocked = False
        self.durations = {}
        self.playback_value = 0

        self.text = ["None", "Repeat", "Random"]
        self.playlist_list = []
        self.values = [QMediaPlaylist.Loop, QMediaPlaylist.CurrentItemInLoop, QMediaPlaylist.Random]

        # Thumbnail widget
        self.image_label = QLabel()

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

        # Player and playlist setup

        self.player = QMediaPlayer()
        self.player.setVolume(50)
        self.player.stateChanged.connect(self.waveform)

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
        self.playlistView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.playlistView.customContextMenuRequested.connect(self.list_view_menu)
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

        # Sound wave widget

        self.wave_graphic = WaveGraphic(self)
        self.wave_graphic.hide()

        # Testing slider again
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, self.player.duration() / 1000)
        self.slider.sliderMoved.connect(self.seek)
        self.player.durationChanged.connect(self.durationChanged)
        self.player.positionChanged.connect(self.positionChanged)

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

        display_layout = QVBoxLayout()
        display_layout.addWidget(song_search)
        display_layout.addWidget(self.playlistView)
        display_layout.addLayout(playlist_layout)

        music_layout = QVBoxLayout()
        music_layout.addWidget(self.image_label)
        music_layout.addWidget(self.slider)
        music_layout.addLayout(control_layout)

        main_layout = QHBoxLayout()
        main_layout.addLayout(music_layout)
        main_layout.addLayout(display_layout)

        main_2_layout = QVBoxLayout()
        main_2_layout.addLayout(main_layout)
        main_2_layout.addWidget(self.wave_graphic)

        self.setLayout(main_2_layout)

    def waveform(self, status):
        if status == QMediaPlayer.PlayingState:
            self.wave_graphic.start()
        elif status == QMediaPlayer.PausedState:
            self.wave_graphic.pause()
        else:
            self.wave_graphic.stop()

    def list_view_menu(self, point):
        menu = QMenu("Menu", self)
        recommend_action = QAction('&Recommend Songs', self)
        menu.addAction(recommend_action)

        # TODO: [FEATURE] add rename song
        menu.triggered.connect(lambda: self.parent().call_download_manager(self.get_links()))

        # Show the context menu.
        menu.exec_(self.playlistView.mapToGlobal(point))

    def get_links(self):
        title = self.playlistView.selectedIndexes()[0].data()
        link = getYoutubeURLFromSearch(title)
        if len(link) > 1:
            return youtube_recommendations(link)

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

    def search(self, part_of_song):
        for index in range(self.playlistModel.rowCount()):
            item = self.playlistModel.data(self.playlistModel.index(index, 0)).lower()
            self.playlistView.setRowHidden(index, part_of_song.lower() not in item)

    def change_thumbnail(self, position=0):

        self.playlistView.setCurrentIndex(self.playlistModel.index(position, 0))

        song = self.playlistView.selectedIndexes()[0].data()
        if self.wave_graphic.is_song_cached(song):
            self.wave_graphic.load_waves(song)
        else:
            wc_ = WaveConverter(song, self.wave_graphic.set_wav)
            wc_.convert()

        if self.playlistView.currentIndex().data() is None or self.blocked:
            return

        max_ratio = 0
        img = None

        for item in listdir(self.thumbnails):
            if item.endswith('.jpg'):
                ratio = similar(item, self.playlistView.currentIndex().data().replace('.mp3', '.jpg'))
                if ratio > max_ratio:
                    max_ratio = ratio
                    img = item

        if img:
            p = QPixmap(self.thumbnails + img)
            self.image_label.setPixmap(p.scaled(self.thumb_width, self.thumb_height, Qt.KeepAspectRatio))

    def switch_playlist(self, current_text):
        self.playlist.clear()
        if current_text == "No Playlist":
            self.refresh()
        else:
            if read_playlist(current_text):
                songs = read_playlist(current_text).split('\n')
                for song in songs:
                    self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(song)))

    def refresh(self):
        # Change it so it will go to same song.
        if self.playlist_name.currentText() != "No Playlist":
            return

        paths = fetch_options()['paths']['music_path'].split(';')

        current_songs = [self.playlistModel.data(self.playlistModel.index(row, 0))
                         for row in range(self.playlistModel.rowCount())]

        for path in paths:
            if not path:
                continue
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

    def next_song(self):
        self.playlist.next()
        self.playlistView.setCurrentIndex(
                self.playlistModel.index(self.playlist.currentIndex(), 0))

    def previous_song(self):
        # TODO: [BUG] previous at first should go to last
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

    def durationChanged(self, duration):
        duration /= 1000
        self.slider.setMaximum(duration)

    def positionChanged(self, progress):
        progress /= 1000

        if not self.slider.isSliderDown():
            self.slider.setValue(progress)

    def seek(self, seconds):
        self.player.setPosition(seconds * 1000)
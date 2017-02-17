#!/usr/bin/env python
import re
import random
import hashlib
from os import listdir
from os.path import isfile, join, exists
# Third party libraries
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QUrl, QProcess
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtWidgets import (QHBoxLayout, QListView, QSlider, QStyle, QProgressBar,
                             QToolButton, QVBoxLayout, QWidget, QTextEdit, QLabel)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from scipy.misc import imread
# Core libraries
from core.analysis import WavePlot, WaveAnimator
from core.playlist import PlaylistModel
from core.downloader import YoutubeDownloader
from core.config import fetch_options, add_to_info, parse_command

options = fetch_options()
FFMPEG_BIN = options['paths']['ffmpeg_bin']
DURATION_CMD = options['commands']['duration']
THUMBNAILS = options['paths']['thumbnails']
THUMB_WIDTH = options['thumbnail']['width']
THUMB_HEIGHT = options['thumbnail']['height']

class MusicPlayer(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.jumping = False
        self.durations = {}
        self.playback_value = 0
        self.text = ["None", "Repeat", "Random"]
        self.values = [QMediaPlaylist.Loop, QMediaPlaylist.CurrentItemInLoop, QMediaPlaylist.Random]

        # Thumbnail widget
        self.image_label = QLabel()
        # TODO: animate waveforms

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

        self.waveformButton = QToolButton(clicked=self.get_waveform)
        self.waveformButton.setText("Waveform")

        # Player and playlist setup

        self.player = QMediaPlayer()
        self.player.setVolume(50)


        self.playlist = QMediaPlaylist()
        self.playlist.setPlaybackMode(self.values[0])
        self.playlist.setCurrentIndex(1)

        self.player.setPlaylist(self.playlist)
        self.player.durationChanged.connect(self.duration_changed)
        self.player.positionChanged.connect(self.position_changed)

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

        # Duration widgets

        self.durationSlider = QSlider(Qt.Horizontal)
        self.durationSlider.sliderReleased.connect(self.seek)

        self.duration_label = QLabel()
        self.durationSlider.setRange(0, self.player.duration() / 1000.0)

        # Refresh widgets

        self.refresh_bar = QProgressBar()
        self.refresh_bar.hide()

        self.duration_process = QProcess(self)
        self.duration_process.finished.connect(self.read_duration)

        # Layouts setup

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self.stopButton)
        control_layout.addWidget(self.previousButton)
        control_layout.addWidget(self.playButton)
        control_layout.addWidget(self.nextButton)
        control_layout.addWidget(self.muteButton)
        control_layout.addWidget(self.volumeSlider)
        control_layout.addWidget(self.playbackButton)
        control_layout.addWidget(self.waveformButton)

        duration_layout = QHBoxLayout()
        duration_layout.addWidget(self.durationSlider)
        duration_layout.addWidget(self.duration_label)

        display_layout = QHBoxLayout()
        display_layout.addWidget(self.playlistView)

        music_layout = QVBoxLayout()
        music_layout.addWidget(self.image_label)

        # Disabled duration layout since it is so buggy.
        #music_layout.addLayout(duration_layout)
        music_layout.addLayout(control_layout)
        music_layout.addWidget(self.refresh_bar)

        main_layout = QHBoxLayout()
        main_layout.addLayout(music_layout)
        main_layout.addLayout(display_layout)
        #main_layout.addWidget(self.canvas)

        self.refresh()
        img = random.choice([item for item in listdir(THUMBNAILS) if item.endswith('.jpg')])
        p = QPixmap(THUMBNAILS + img)
        self.image_label.setPixmap(p.scaled(THUMB_WIDTH, THUMB_HEIGHT, Qt.KeepAspectRatio))
        self.setLayout(main_layout)

    def download(self):
        yt = YoutubeDownloader(self.links_to_download.toPlainText().split(','),
                               self.download_label, self.download_button,
                               self.download_status, self.refresh)
        yt.begin()
        self.links_to_download.clear()

    def change_thumbnail(self, position):
        print("called")
        """self.wa = WaveAnimator(self.playlistView.currentIndex().data(), self.durations[self.playlistView.currentIndex().data()] / 1000.0,
                               self.figure, self.canvas)
        self.wa.start()"""
        self.playlistView.setCurrentIndex(self.playlistModel.index(position, 0))

        image_path = THUMBNAILS + self.playlistView.currentIndex().data().replace('.mp3', '.jpg')
        if exists(image_path):
            p = QPixmap(image_path)
            self.image_label.setPixmap(p.scaled(THUMB_WIDTH, THUMB_HEIGHT, Qt.KeepAspectRatio))
        else:
            img = random.choice([item for item in listdir(THUMBNAILS) if item.endswith('.jpg')])
            p = QPixmap(THUMBNAILS + img)
            self.image_label.setPixmap(p.scaled(THUMB_WIDTH, THUMB_HEIGHT, Qt.KeepAspectRatio))

    def refresh(self):
        # Change it so it will go to same song.
        self.durations = {}
        # TODO: move it to data/
        options = fetch_options("data/info.cfg")
        paths = fetch_options("PhantomTrack.cfg")['paths']['music_path'].split(';')
        current_songs = [self.playlistModel.data(self.playlistModel.index(row, 0))
                     for row in range(self.playlistModel.rowCount()) ]

        self.songs_not_in_list = []
        for path in paths:
            for item in listdir(path):
                if isfile(join(path, item))and item.endswith(".mp3") and (item not in current_songs):
                    song_hash = hashlib.sha224(item.encode()).hexdigest()
                    if 'duration' in options and song_hash in options['duration']:
                        self.durations[item] = float(options['duration'][song_hash])
                    else:
                        self.songs_not_in_list.append((join(path, item), item, song_hash))

                    self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(join(path, item))))

        self.refresh_bar.setMaximum(len(self.songs_not_in_list))
        self.refresh_bar.setValue(0)
        self.refresh_bar.show()
        self.duration_next()

    def duration_next(self):
        if len(self.songs_not_in_list) > 0:
            path, self.item, self.song_hash = self.songs_not_in_list.pop()
            command_input = {'ffmpeg': FFMPEG_BIN, 'song':path}
            cmd = parse_command(DURATION_CMD, command_input)
            self.duration_process.start(cmd)
        else:
            self.refresh_bar.hide()


    def read_duration(self):
        output = str(self.duration_process.readAllStandardError())

        duration_time = re.search("Duration:\s[^\s]{0,}", output).group(0).replace("Duration: ", "")[:-1]
        hours, mins, seconds = duration_time.split(":")
        self.durations[self.item] = (float(hours) * 3600 + float(mins) * 60 + float(seconds)) * 1000
        add_to_info(self.song_hash, self.durations[self.item])
        self.refresh_bar.setValue(self.refresh_bar.value()+1)
        self.duration_next()

    def playback_mode(self):
        # Normal -> Loop -> Random
        def up_value(value, max_value=3):
            if value+1 == max_value:
                return 0
            return value+1

        self.playback_value = up_value(self.playback_value)
        self.playlist.setPlaybackMode(self.values[self.playback_value])
        self.playbackButton.setText(self.text[self.playback_value])

    def get_waveform(self):
        self.wave_plot = WavePlot(self.playlistView.selectedIndexes()[0].data())
        self.wave_plot.begin()

    def jump(self, index):
        if index.isValid():
            self.playlist.setCurrentIndex(index.row())
            self.jumping = True
            self.play()

    def play(self):
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

    def duration_changed(self, duration):
        if not self.playlistView.currentIndex().data() in self.durations:
            return
        self.duration_label.setText("00:00/{0:02d}:{1:02d}".format(
            int(self.durations[self.playlistView.currentIndex().data()] / 1000.0) // 60,
            int(self.durations[self.playlistView.currentIndex().data()] / 1000.0) % 60)
        )
        self.durationSlider.setRange(0, self.durations[self.playlistView.currentIndex().data()] / 1000.0)

    def position_changed(self, position):
        if not self.playlistView.currentIndex().data() in self.durations:
            return

        self.duration_label.setText("{0:02d}:{1:02d}/{2:02d}:{3:02d}".format(
            int(position/1000) // 60, int(position/1000) % 60,
            int(self.durations[self.playlistView.currentIndex().data()] / 1000.0) // 60,
            int(self.durations[self.playlistView.currentIndex().data()] / 1000.0) % 60))
        self.durationSlider.setValue(position / 1000)

    def seek(self):
        #self.player.setPosition(self.durationSlider.value()*1000)
        pass
#!/usr/bin/env python
import sys
from os import listdir, rename
from os.path import isfile, join
# Third party libraries
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QListView, QSlider, QStyle,
                             QToolButton, QVBoxLayout, QWidget, QTextEdit, QLabel)
# Core libraries
from core.analysis import WavePlt
from core.dialogs import wave_dialog
from core.playlist import PlaylistModel
from core.config import fetch_options, add_to_info

import os
import subprocess
import re
import hashlib

FFMPEG_BIN = "bin/ffmpeg.exe"
LIBRARY_PATH = "library/"
MUSIC_PATH = "D:/Music/"
PLOT_PATH = LIBRARY_PATH + "plots/"


class MusicPlayer(QWidget):

    def __init__(self, parent=None):

        QWidget.__init__(self, parent)

        self.jumping = False
        self.playback_value = 0
        self.text = ["None", "Repeat", "Random"]
        self.durations = {}
        self.values = [QMediaPlaylist.Loop, QMediaPlaylist.CurrentItemInLoop, QMediaPlaylist.Random]

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

        self.waveformButton = QToolButton(clicked=self.get_waveform)
        self.waveformButton.setText("Waveform")

        self.volumeSlider = QSlider(Qt.Horizontal, sliderMoved=self.change_volume)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setPageStep(1)
        self.volumeSlider.setValue(50)
        self.unmute_value = 50

        self.player = QMediaPlayer()
        self.player.setVolume(50)

        self.durationSlider = QSlider(Qt.Horizontal)
        self.durationSlider.setEnabled(False)
        # There seems to be a bug with setPosition
        #self.durationSlider.sliderReleased.connect(lambda : self.player.setPosition(self.durationSlider.value() * 1000))
        self.duration_label = QLabel()
        self.durationSlider.setRange(0, self.player.duration() / 1000.0)

        self.playlist = QMediaPlaylist()
        self.playlist.setPlaybackMode(self.values[0])

        self.refresh()

        self.playlist.setCurrentIndex(1);
        self.player.setPlaylist(self.playlist)

        self.playlistModel = PlaylistModel()
        self.playlistModel.setPlaylist(self.playlist)

        self.playlistView = QListView()
        self.playlistView.setModel(self.playlistModel)
        self.playlistView.setCurrentIndex(
                self.playlistModel.index(self.playlist.currentIndex(), 0))
        self.playlistView.activated.connect(self.jump)
        self.playlist.currentIndexChanged.connect(lambda pos: self.playlistView.setCurrentIndex(
            self.playlistModel.index(pos, 0))
                                                )
        self.player.durationChanged.connect(self.duration_changed)
        self.player.positionChanged.connect(self.position_changed)

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
        music_layout.addLayout(display_layout)
        music_layout.addLayout(duration_layout)
        music_layout.addLayout(control_layout)

        self.links_to_download = QTextEdit()
        self.download_status = QTextEdit()
        self.download_status.setReadOnly(True)

        self.download_button = QToolButton(clicked=self.download)
        self.download_button.setText("Download")

        download_layout = QVBoxLayout()
        download_layout.addWidget(self.links_to_download)
        download_layout.addWidget(self.download_status)
        download_layout.addWidget(self.download_button)

        main_layout = QHBoxLayout()
        main_layout.addLayout(music_layout)
        main_layout.addLayout(download_layout)

        self.setLayout(main_layout)

    def download(self):
        # TODO: use qProcess for this
        # TODO: empty download list or remove the successful ones
        # Possibly useful regex: \d{1,}\.\d{1,}%
        links = self.links_to_download.toPlainText().split('\n')
        for link in links:
            cmd = 'youtube-dl --ffmpeg-location \"' + FFMPEG_BIN + '\" --extract-audio --audio-format mp3 --audio-quality 0 '+ link
            with open(os.devnull, 'w') as shutup:
                self.download_status.setText(str(subprocess.check_output(cmd)))

        for item in listdir('.'):
            if isfile(item) and item.endswith(".mp3"):
                try:
                    rename(item, MUSIC_PATH+item)
                except Exception as exc:
                    print(exc)
        self.refresh()

    def refresh(self):
        # Change it so it will go to same song.
        # TODO: cache this
        self.durations = {}
        self.playlist.clear()
        options = fetch_options("info.cfg")
        for f in listdir(MUSIC_PATH):
            if isfile(join(MUSIC_PATH, f))and f.endswith(".mp3"):
                song_hash = hashlib.sha224(f.encode()).hexdigest()
                if 'duration' in options and song_hash in options['duration']:
                    self.durations[f] = float(options['duration'][song_hash])
                else:
                    cmd = "\"" + FFMPEG_BIN + "\" -i \"" + join(MUSIC_PATH, f) + "\" -f null pipe:1"
                    output = str(subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stderr.read())
                    duration_time = re.search("time=[^\s]{0,}", output).group(0).replace("time=", "")
                    hours, mins, seconds = duration_time.split(":")

                    self.durations[f] = (float(hours)*3600 + float(mins) * 60 + float(seconds))*1000
                    add_to_info(song_hash, self.durations[f])
                self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(join(MUSIC_PATH, f))))

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
        # TODO: use qProcess for this
        self.thread = WavePlt()
        self.thread.set_(self.playlistView.selectedIndexes()[0].data())
        self.thread.finished.connect(lambda: wave_dialog(self.thread.png_name))
        self.thread.start()

    def jump(self, index):
        if index.isValid():
            # Fix that here :)
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
        self.unmute_value = value

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
    musicplayer = MusicPlayer()
    musicplayer.setWindowTitle("Phantom Track")
    musicplayer.show()
    sys.exit(app.exec_())

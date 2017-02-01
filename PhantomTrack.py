 #!/usr/bin/env python
import sys

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QListView,
        QSlider, QStyle, QToolButton, QVBoxLayout, QWidget)

from os import listdir
from os.path import isfile, join
from core.analysis import WavePlt
from core.dialogs import wave_dialog
from core.playlist import PlaylistModel


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

        self.volumeSlider = QSlider(Qt.Horizontal,
                sliderMoved=self.change_volume)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setPageStep(1)
        self.volumeSlider.setValue(50)
        self.unmute_value = 50

        self.player = QMediaPlayer()
        self.player.setVolume(50)

        self.durationSlider = QSlider(Qt.Horizontal, sliderMoved=lambda pos: self.player.setPosition(pos*1000))
        self.duration_label = QLabel()

        self.player.durationChanged.connect(self.durationChanged)
        self.player.positionChanged.connect(self.positionChanged)

        self.playlist = QMediaPlaylist()
        self.playlist.setPlaybackMode(self.values[0])

        for f in listdir(MUSIC_PATH):
            if isfile(join(MUSIC_PATH, f)):
                print(join(MUSIC_PATH, f))
                self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(join(MUSIC_PATH, f))))

        self.playlist.setCurrentIndex(1);
        self.player.setPlaylist(self.playlist)

        self.playlistModel = PlaylistModel()
        self.playlistModel.setPlaylist(self.playlist)

        self.playlistView = QListView()
        self.playlistView.setModel(self.playlistModel)
        self.playlistView.setCurrentIndex(
                self.playlistModel.index(self.playlist.currentIndex(), 0))
        self.playlistView.activated.connect(self.jump)
        self.playlist.currentIndexChanged.connect(lambda pos: self.playlistView.setCurrentIndex(self.playlistModel.index(pos, 0)))

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

        main_layout = QHBoxLayout()
        main_layout.addLayout(music_layout)

        self.setLayout(main_layout)

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
        self.thread = WavePlt()
        self.thread.set_(self.playlistView.selectedIndexes()[0].data())
        self.thread.finished.connect(lambda : wave_dialog(self.thread.png_name))
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

    def durationChanged(self, duration):
        self.duration_label.setText("{0:.2f}/{1:.2f}".format(0, self.player.duration() / 100000))
        self.durationSlider.setMaximum(duration / 1000)

    def positionChanged(self, position):
        self.duration_label.setText("{0:.2f}/{1:.2f}".format(position / 100000, self.player.duration() / 100000))
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
    musicplayer.setWindowTitle("Data Science Project")
    musicplayer.show()
    sys.exit(app.exec_())

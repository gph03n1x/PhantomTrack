 #!/usr/bin/env python
import sys

from PyQt5.QtCore import Qt, QThread, QTime, QUrl, QRect
from PyQt5.QtGui import QColor, qGray, QImage, QPainter, QPalette, QPixmap
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog, QFileDialog,
        QFormLayout, QHBoxLayout, QLabel, QListView, QMessageBox, QPushButton,
        QSizePolicy, QSlider, QStyle, QToolButton, QVBoxLayout, QWidget)

from os import listdir
from os.path import isfile, join
from core.analysis import WavePlt
from core.playlist import PlaylistModel

# GREATNESS HERE : http://doc.qt.io/qt-5/audiooverview.html
# I AM IN LOVE : http://doc.qt.io/qt-5/qmediaplayer.html
# FUCK CODECS

FFMPEG_BIN = "bin/ffmpeg.exe"
LIBRARY_PATH = "library/"
MUSIC_PATH = "D:/Music/"
PLOT_PATH = LIBRARY_PATH + "plots/"


class MusicPlayer(QWidget):

    def __init__(self, parent = None):

        QWidget.__init__(self, parent)

        self.jumping = False

        self.playButton = QToolButton(clicked=self.play)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        self.stopButton = QToolButton(clicked=self.stop)
        self.stopButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stopButton.setEnabled(False)

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

        self.playlist = QMediaPlaylist()

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



        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self.stopButton)
        control_layout.addWidget(self.previousButton)
        control_layout.addWidget(self.playButton)
        control_layout.addWidget(self.nextButton)
        control_layout.addWidget(self.muteButton)
        control_layout.addWidget(self.volumeSlider)
        control_layout.addWidget(self.waveformButton)

        display_layout = QHBoxLayout()
        display_layout.addWidget(self.playlistView)
        #display_layout.addWidget(self.waveform)

        layout = QVBoxLayout()
        layout.addLayout(display_layout)
        layout.addLayout(control_layout)
        self.setLayout(layout)

    def get_waveform(self):
        self.thread = WavePlt()
        self.thread.set_(self.playlistView.selectedIndexes()[0].data())
        self.thread.finished.connect(self.wave_dialog)
        self.thread.start()


    def wave_dialog(self):
        image = QPixmap(self.thread.png_name)

        Dialog = QDialog()
        Dialog.setWindowModality(Qt.WindowModal )
        Dialog.setObjectName("Dialog")
        Dialog.setWindowTitle("Wave form")

        Dialog.resize(image.width(), image.height())

        waveform = QLabel(Dialog)
        waveform.setPixmap(image)
        waveform.show()
        Dialog.exec_()


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




if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53,53,53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(15,15,15))
    palette.setColor(QPalette.AlternateBase, QColor(53,53,53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53,53,53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(142,45,197).lighter())
    palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(palette)
    musicplayer = MusicPlayer()
    musicplayer.setWindowTitle("Data Science Project")
    musicplayer.show()
    sys.exit(app.exec_())

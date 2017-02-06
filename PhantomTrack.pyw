#!/usr/bin/env python
import sys
from os import listdir, rename
from os.path import isfile, join
# Third party libraries
from PyQt5.QtCore import Qt, QUrl, QProcess
from PyQt5.QtGui import QColor, QPalette, QIcon
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QListView, QSlider, QStyle, QProgressBar,
                             QToolButton, QVBoxLayout, QWidget, QTextEdit, QLabel, QMainWindow, QAction)
# Core libraries
from core.analysis import WavePlt
from core.dialogs import wave_dialog, LibrariesManager
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

class MainApplication(QMainWindow):
    def __init__(self):
        QApplication.__init__(self)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Music')
        edit_libraries_action = QAction('&Library folders', self)
        edit_libraries_action.triggered.connect(self.call_libraries_manager)
        fileMenu.addAction(edit_libraries_action)

        options = fetch_options()
        print(options['paths'])
        if len(options['paths']['music_path']) < 1:
            self.call_libraries_manager()

    def call_libraries_manager(self):
        self.libraries_manager = LibrariesManager()
        self.libraries_manager.show()

    def set_up_gui(self, widget):
        self.setCentralWidget(widget)


class MusicPlayer(QWidget):

    def __init__(self, parent=None):

        QWidget.__init__(self, parent)

        # TODO: set workspaces and library folders

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
        #self.durationSlider.setEnabled(False)
        # There seems to be a bug with setPosition
        #self.durationSlider.sliderReleased.connect(self.seek)
        self.duration_label = QLabel()
        self.durationSlider.setRange(0, self.player.duration() / 1000.0)

        self.playlist = QMediaPlaylist()
        self.playlist.setPlaybackMode(self.values[0])



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

        self.refresh()

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
        self.download_status = QProgressBar()

        self.download_button = QToolButton(clicked=self.download)
        self.download_button.setText("Download")
        self.download_status_label = QLabel()
        # TODO: add the label in the layout

        self.process = QProcess(self)
        # QProcess emits `readyRead` when there is data to be read
        self.process.readyRead.connect(self.data_ready)

        # Just to prevent accidentally running multiple times
        # Disable the button when process starts, and enable it when it finishes
        self.process.started.connect(lambda: self.download_button.setEnabled(False))
        self.process.finished.connect(self.move_files)

        download_controls = QHBoxLayout()
        download_controls.addWidget(self.download_button)
        download_controls.addWidget(self.download_status_label)

        download_layout = QVBoxLayout()
        download_layout.addWidget(self.links_to_download)
        download_layout.addWidget(self.download_status)
        download_layout.addLayout(download_controls)

        main_layout = QHBoxLayout()
        main_layout.addLayout(music_layout)
        main_layout.addLayout(download_layout)

        self.setLayout(main_layout)

    def seek(self):
        print(self.durationSlider.value())
        self.player.setPosition(self.durationSlider.value()*1000*self.player.duration()/self.durations[self.playlistView.currentIndex().data()])
        self.position_changed(self.player.position())

    def data_ready(self):
        data = str(self.process.readAll())
        percentage = re.search("\d{1,}\.\d{1,}%", data)
        if percentage:
            self.download_status.setValue(int(percentage.group(0).replace("%", "").split(".")[0]))

    def download(self):
        # Possibly useful regex: \d{1,}\.\d{1,}%
        self.download_status_label.setText("Downloading ...")
        links = self.links_to_download.toPlainText().split('\n')
        cmd = ""
        for link in links:
            cmd += 'youtube-dl --ffmpeg-location \"' + FFMPEG_BIN + '\" --extract-audio --audio-format mp3 --audio-quality 0 '+ link + ";"
            #with open(os.devnull, 'w') as shutup:
            #    self.download_status.setText(str(subprocess.check_output(cmd)))
        self.links_to_download.clear()
        self.process.start(cmd)


    def move_files(self):
        self.download_status_label.setText("Moving to music folder...")
        default_path = fetch_options("PhantomTrack.cfg")['paths']['music_path'].split(';')[0]+"/"
        for item in listdir('.'):
            if isfile(item) and item.endswith(".mp3"):
                try:
                    rename(item, default_path+item)
                except Exception as exc:
                    print(exc)

        self.refresh()
        self.download_status_label.setText("")
        self.download_button.setEnabled(True)

    def refresh(self):
        # Change it so it will go to same song.
        self.durations = {}

        options = fetch_options("info.cfg")
        paths = fetch_options("PhantomTrack.cfg")['paths']['music_path'].split(';')
        current_songs = [self.playlistModel.data(self.playlistModel.index(row, 0))
                     for row in range(self.playlistModel.rowCount()) ]
        for path in paths:
            for item in listdir(path):
                if isfile(join(path, item))and item.endswith(".mp3") and (item not in current_songs):
                    song_hash = hashlib.sha224(item.encode()).hexdigest()
                    if 'duration' in options and song_hash in options['duration']:
                        self.durations[item] = float(options['duration'][song_hash])
                    else:
                        cmd = "\"" + FFMPEG_BIN + "\" -i \"" + join(path, item) + "\" -f null pipe:1"
                        output = str(subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stderr.read())
                        duration_time = re.search("Duration:\s[^\s]{0,}", output).group(0).replace("Duration: ", "")[:-1]

                        hours, mins, seconds = duration_time.split(":")

                        self.durations[item] = (float(hours)*3600 + float(mins) * 60 + float(seconds))*1000
                        add_to_info(song_hash, self.durations[item])

                    self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(join(path, item))))



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

    music_player = MusicPlayer()

    main_app = MainApplication()
    main_app.setWindowTitle("Phantom Track")
    main_app.set_up_gui(music_player)
    main_app.show()
    sys.exit(app.exec_())

#!/usr/bin/env python
import os
import os.path
import hashlib
from scipy.io.wavfile import read
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QWidget
import numpy as np


WAVES_DIR = "data/waves/"

class WaveGraphic(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        # TODO: add to config
        self.bars = 60
        self.between = 10
        self.input_data = None
        self.setFixedHeight((self.geometry().height()-220)/2)
        self.stop = False

    def is_song_cached(self, song):
        song = song.split(".")[0]
        song_hash = WAVES_DIR + hashlib.sha224(song.encode()).hexdigest() + ".swv"
        return os.path.exists(song_hash)

    def load_load_waves(self, song):
        song = song.split(".")[0]
        self.title = song
        song_hash = WAVES_DIR + hashlib.sha224(song.encode()).hexdigest() + ".swv"
        if not os.path.exists(song_hash):
            print("[-] Attempt to ready non-cached song")
            return

        song_file = open(song_hash, 'rb')

        self.input_data_2 = np.load(song_file)
        song_file.close()
        self.start = 0
        self.stop = False
        self.show()

        self.animate()

    def cache_waves(self, song):
        song = song.split(".")[0]

        song_hash = WAVES_DIR + hashlib.sha224(song.encode()).hexdigest() + ".swv"
        if os.path.exists(song_hash):
            return

        song_file = open(song_hash, 'wb')
        np.save(song_file, self.input_data_2)
        song_file.close()

    def animate(self):
        #self.parent().setWindowTitle(self.title)
        # TODO: [BUG] changing song doesnt change the input here
        step = 500

        self.input_data = self.input_data_2[self.start:self.start+step]
        if len(self.input_data) == 0 or self.stop:
            self.hide()
            return
        #print(self.title)
        self.update()

        self.start += step
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(step)

    def paintEvent(self, e):
        height = self.geometry().height()
        if self.input_data is None:
            return

        qp = QPainter()
        qp.begin(self)
        #qp.setBrush(QBrush(Qt.SolidPattern))
        pen = QPen()
        pen.setWidth(2)
        qp.setPen(pen)
        for i, p in enumerate(self.input_data):
            pen.setColor(QColor(0, 69, 88))
            qp.setPen(pen)
            qp.drawLine((i+1)*self.between, height, (i+1)*self.between, height - p[0]/2)

            pen.setColor(QColor(152, 87, 0))
            qp.setPen(pen)
            qp.drawLine((i + 1) * self.between + self.between/2, height,
                        (i + 1) *self.between +  self.between/2, height - p[1]/2)
        qp.end()

    def set_wav(self, wav, title):
        #self.setWindowTitle(title)
        data = 500 / self.bars
        self.title = title
        self.input_data_2 = read(wav)[1][::int(data)]
        os.remove(wav)

        self.cache_waves(wav)

        self.start = 0
        self.stop = False
        self.show()
        self.animate()
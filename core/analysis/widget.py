#!/usr/bin/env python
import os
import os.path
import hashlib
from scipy.io.wavfile import read
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QWidget
import numpy as np
from core.analysis.storage import Storage


class WaveGraphic(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        # TODO: add to config
        # TODO: clean up the mess.
        self.bars = 60
        self.between = 10
        self.input_data = None
        self.setFixedHeight((self.geometry().height()-220)/2)
        self.storage = Storage()
        #self.stop = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)


    def set_title(self, title):
        self.parent().parent().setWindowTitle("Phantom Track "+title)

    def is_song_cached(self, song):
        song = song.split(".")[0]
        song_hash = hashlib.sha224(song.encode()).hexdigest() + ".swv"
        self.storage.cur.execute("select count(*) from song_info where song_hash = ?", (song_hash,))
        return self.storage.cur.fetchone()[0] != 0

    def load_load_waves(self, song):
        if not self.is_song_cached(song):
            print("Attempt to read non-cached song")
            return

        song = song.split(".")[0]
        song_hash = hashlib.sha224(song.encode()).hexdigest() + ".swv"

        self.storage.cur.execute("select * from song_info where song_hash = ?", (song_hash,))
        results = self.storage.cur.fetchone()
        self.input_data_2 = results[1]

        self.start = 0
        self.set_title(song)

    def cache_waves(self, song):
        if not self.is_song_cached(song):
            song = song.rsplit(".", 1)[0]
            song_hash = hashlib.sha224(song.encode()).hexdigest() + ".swv"
            self.storage.cur.execute("insert into song_info (song_hash, wave_form, duration) values (?,?,?)", (song_hash, self.input_data_2, 0))
            self.storage.con.commit()


    def stop(self):
        self.timer.stop()
        self.hide()

    def animate(self):
        self.show()

        step = 250

        self.input_data = self.input_data_2[self.start:self.start+step]
        if len(self.input_data) == 0:
            self.hide()
            return
        self.update()

        self.start += step

        self.timer.start(step/2)

    def paintEvent(self, e):
        if self.input_data is None:
            return

        height = self.geometry().height()


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
        data = 250 / self.bars
        self.set_title(title)
        self.input_data_2 = read(wav)[1][::int(data)]
        os.remove(wav)

        self.cache_waves(wav)
        self.start = 0

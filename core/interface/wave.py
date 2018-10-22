#!/usr/bin/env python
import os
import os.path
import hashlib
import wave
import contextlib

from scipy.io.wavfile import read
from PyQt5.QtCore import QTimer, QRect, Qt
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QWidget

from core.analysis.storage import Storage


class WaveGraphic(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.options = self.parent().options
        self.bars = int(self.options['waves']['bars'])
        self.step = int(self.options['waves']['refrash-rate'])
        self.between = int(self.options['waves']['between'])

        self.starting_point = 0
        self.data = None
        self.data_to_animate = None

        self.setFixedHeight(int(self.options['waves']['height']))

        self.storage = Storage()
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)

    def stop(self):
        self.timer.stop()
        self.starting_point = 0

    def start(self):
        self.animate()

    def pause(self):
        self.timer.stop()

    def set_title(self, title):
        self.parent().parent().setWindowTitle("Phantom Track " + title)

    @staticmethod
    def get_song_hash(song):
        song = song.rsplit(".", 1)[0]
        return hashlib.sha224(song.encode()).hexdigest()

    def is_song_cached(self, song):
        self.storage.cur.execute("select count(*) from song_info where song_hash = ? AND bars = ? AND step = ?",
                                 (WaveGraphic.get_song_hash(song), self.bars, self.step))

        return self.storage.cur.fetchone()[0] != 0

    def load_waves(self, song):
        if not self.is_song_cached(song):
            print("Attempt to read non-cached song")
            return

        song_hash = WaveGraphic.get_song_hash(song)

        self.storage.cur.execute("select * from song_info where song_hash = ? AND bars = ? AND step = ?",
                                 (song_hash, self.bars, self.step))
        results = self.storage.cur.fetchone()
        self.data = results[1]

        self.starting_point = 0
        self.set_title(song)

    def cache_waves(self, song, data, duration):
        if not self.is_song_cached(song):
            song_hash = WaveGraphic.get_song_hash(song)
            self.storage.cur.execute("insert into song_info (song_hash, wave_form, duration, bars, step)\
             values (?,?,?,?,?)", (song_hash, data, duration, self.bars, self.step))
            self.storage.con.commit()

    def animate(self):
        if self.data is None:
            self.timer.start(self.step)
            return

        self.data_to_animate = self.data[self.starting_point:self.starting_point + self.bars]

        if len(self.data_to_animate) == 0:
            self.timer.start(self.step)
            #self.hide()
            return

        self.update()

        self.starting_point += self.bars

        self.timer.start(self.step)

    def paintEvent(self, e):

        if self.data_to_animate is None:
            return

        height = self.geometry().height()
        width = self.geometry().width()

        pen = QPen()
        pen.setWidth(2)
        pen.setColor(QColor(0, 0, 0))

        qp = QPainter()
        qp.begin(self)
        qp.setPen(pen)
        qp.fillRect(QRect(0, 0, width, height), Qt.white)
        for i, p in enumerate(self.data_to_animate):
            pen.setColor(QColor(0, 69, 88))
            qp.setPen(pen)
            qp.drawLine(int((i + 1) * self.between), height, int((i + 1) * self.between), int(height - p[0] / 2))

            pen.setColor(QColor(152, 87, 0))
            qp.setPen(pen)
            qp.drawLine(int((i + 1) * self.between + self.between / 2), height,
                        int((i + 1) * self.between + self.between / 2), int(height - p[1] / 2))
        qp.end()

    def set_wav(self, wav):
        self.sample_wave_file(wav)

    def sample_wave_file(self, wave_file):
        with contextlib.closing(wave.open(wave_file, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)

        wave_data = read(wave_file)[1]
        os.remove(wave_file)

        rate = int(len(wave_data) * (self.step / 1000) / (duration * self.bars))

        self.data = wave_data[::rate]
        self.cache_waves(wave_file, self.data, duration)
        self.load_waves(wave_file)

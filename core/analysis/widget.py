#!/usr/bin/env python
import os
from scipy.io.wavfile import read
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QWidget


class WaveGraphic(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        # TODO: add to config
        self.bars = 60
        self.between = 10
        self.input_data = None

        self.setFixedHeight((self.geometry().height()-220)/2)

        self.stop = False

    def animate(self):
        step = 500

        data = len(self.input_data_2[self.start:self.start+step]) / self.bars
        self.input_data = self.input_data_2[self.start:self.start+step][::int(data)]
        if len(self.input_data) == 0 or self.stop:
            self.hide()
            return

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
        self.setWindowTitle(title)
        self.input_data_2 = read(wav)[1]
        os.remove(wav)
        self.start = 0
        self.stop = False
        #data = len(self.input_data_2) / self.bars
        #self.input_data = self.input_data_2[::int(data)]
        self.show()
        self.animate()
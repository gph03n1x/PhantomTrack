#!/usr/bin/env python
import os
import os.path
import time
from scipy.io.wavfile import read
import matplotlib.pyplot as plt
from PyQt5.QtCore import QProcess, QThread

from core.config import fetch_options, get_default_path, parse_command
from core.dialogs import wave_dialog

options = fetch_options()
FFMPEG_BIN = options['paths']['ffmpeg_bin']
PLOT_PATH = options['paths']['plot_path']
WAVE_CMD = options['commands']['wave_conversion']
MUSIC_PATH = get_default_path()


class WavePlot:

    def __init__(self, filename, dialog=True):
        self.full_path = MUSIC_PATH + filename
        self.f = filename
        self.dialog = dialog
        self.png_name = PLOT_PATH + self.f.replace(".mp3", ".png")
        self.convert_process = QProcess()
        self.convert_process.finished.connect(self.plot)

    def plot(self):
        print(self.convert_process.readAllStandardError())
        print(self.convert_process.readAllStandardOutput())
        plt.ylabel("Amplitude")
        plt.xlabel("Time")
        input_data = read(self.wav_name)
        audio = input_data[1]

        plt.plot(audio[::22050])

        # TODO: keep wave files mode.
        os.remove(self.wav_name)

        plt.savefig(self.png_name, bbox_inches='tight')
        plt.clf()

        if self.dialog:
            wave_dialog(self.png_name)

    def convert(self):
        self.wav_name = self.f.replace(".mp3", ".wav")
        if os.path.isfile(self.full_path):
            command_input = {'ffmpeg': FFMPEG_BIN, 'song': self.full_path, 'wave':self.wav_name}
            cmd = parse_command(WAVE_CMD, command_input)
            self.convert_process.start(cmd)

    def begin(self):
        self.convert()


# TODO: split into converter and animator
class WaveAnimator(QThread):
    def __init__(self, filename, duration, figure, canvas):
        QThread.__init__(self)
        self.full_path = MUSIC_PATH + filename
        self.f = filename
        self.duration = duration
        #self.convert_process = QProcess()
        #self.convert_process.finished.connect(self.done)
        self.figure = figure
        self.canvas = canvas
        self.audio = None
        self.keep_animating = True

    def run(self):
        print("Started")
        self.wav_name = self.f.replace(".mp3", ".wav")

        input_data = read(self.wav_name)
        self.samples = int(len(input_data[1]) / self.duration)//2
        self.audio = input_data[1]
        self.start = 0

        ax = self.figure.add_subplot(111)

        # discards the old graph
        ax.hold(False)
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)


        # plot data

        while self.keep_animating:
            plot_audio = self.audio[self.start:self.start+self.samples]
            self.start += self.samples
            ax.plot(plot_audio)
            time.sleep(0.5)


            # refresh canvas
            self.canvas.draw()


    def stop(self):
        self.keep_animating = False


    # TODO: convert only




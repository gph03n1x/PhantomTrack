#!/usr/bin/env python
import os
import os.path

from scipy.io.wavfile import read
import matplotlib.pyplot as plt
from PyQt5.QtCore import QProcess

from core.config import fetch_options, get_default_path
from core.dialogs import wave_dialog

options = fetch_options()
FFMPEG_BIN = options['paths']['ffmpeg_bin']
PLOT_PATH = options['paths']['plot_path']
MUSIC_PATH = get_default_path()


class WavePlt:
    def __init__(self, filename):
        self.full_path = MUSIC_PATH + filename
        self.f = filename
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

        os.remove(self.wav_name)

        plt.savefig(self.png_name, bbox_inches='tight')
        plt.clf()

        wave_dialog(self.png_name)

    def convert(self):
        self.wav_name = self.f.replace(".mp3", ".wav")

        if os.path.isfile(self.full_path):
            cmd = FFMPEG_BIN+" -i \""+self.full_path+"\" -acodec pcm_u8 -ar 22050 \""+self.wav_name+"\""

            self.convert_process.start(cmd)

    def begin(self):
        self.convert()





def convert_to_wave():
    pass
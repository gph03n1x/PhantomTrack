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
    def __init__(self, filename, dialog=True, remove_wave_file=True):
        self.dialog = dialog
        self.remove_wave_file = remove_wave_file
        self.converter = WaveConverter(filename, self.plot)

    def plot(self, wav_name, png_name):
        plt.ylabel("Amplitude")
        plt.xlabel("Time")
        input_data = read(wav_name)
        audio = input_data[1]

        plt.plot(audio[::22050])

        if self.remove_wave_file:
            os.remove(wav_name)

        plt.savefig(png_name, bbox_inches='tight')
        plt.clf()

        if self.dialog:
            wave_dialog(png_name)


    def begin(self):
        self.converter.convert()


class WaveConverter:
    def __init__(self, filename, on_finish):
        # TODO: this wont work if the song is not in default folder
        self.full_path = MUSIC_PATH + filename
        self.wav_name = filename.replace(".mp3", ".wav")
        self.png_name = PLOT_PATH + filename.replace(".mp3", ".png")
        self.convert_process = QProcess()
        self.convert_process.finished.connect(lambda : on_finish(self.wav_name, self.png_name))


    def convert(self):
        if os.path.isfile(self.full_path):
            command_input = {'ffmpeg': FFMPEG_BIN, 'song': self.full_path, 'wave':self.wav_name}
            cmd = parse_command(WAVE_CMD, command_input)
            self.convert_process.start(cmd)




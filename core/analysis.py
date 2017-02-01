#!/usr/bin/env python
import os
import os.path
import subprocess
from scipy.io.wavfile import read
import matplotlib.pyplot as plt
from PyQt5.QtCore import QThread

FFMPEG_BIN = "bin/ffmpeg.exe"
LIBRARY_PATH = "library/"
MUSIC_PATH = "D:/Music/"
PLOT_PATH = LIBRARY_PATH + "plots/"


class WavePlt(QThread):
    def set_(self, filename):
        self.full_path = MUSIC_PATH + filename
        self.f = filename
        self.png_name = PLOT_PATH + self.f.replace(".mp3", ".png")

    def run(self):
        wav_name = self.f.replace(".mp3", ".wav")


        if os.path.isfile(self.full_path):
            print(self.full_path)
            cmd = FFMPEG_BIN+" -i \""+self.full_path+"\" -acodec pcm_u8 -ar 22050 \""+wav_name+"\""
            print(cmd)
            with open(os.devnull, 'w') as shutup:

                return_code = subprocess.check_call(cmd, stdout=shutup, stderr=shutup)

            #return_code = subprocess.check_call(cmd)

            plt.ylabel("Amplitude")
            plt.xlabel("Time")
            plt.title(self.f)

            input_data = read(wav_name)
            audio = input_data[1]
            print(len(audio[::22050]))
            # plot the first 1024 samples
            plt.plot(audio[::22050])

            os.remove(wav_name)

            plt.savefig(self.png_name, bbox_inches='tight')
            plt.clf()

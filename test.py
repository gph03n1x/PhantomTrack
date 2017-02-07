#!/usr/bin/env python
import os
import os.path
import subprocess
from scipy.io.wavfile import read
import matplotlib; matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as anim
import tkinter as tk
import numpy as np
import wave
import scipy.signal as signal


LARGE_FONT = ("Verdana", 12)
FFMPEG_BIN = "bin/ffmpeg.exe"
LIBRARY_PATH = "library/"
MUSIC_PATH = "D:/Music/"
PLOT_PATH = LIBRARY_PATH + "plots/"


class FrequencyGraph(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "rtlsdr-quickie")

        container = tk.Frame(self)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid(row=0, column=0)
        input_data = wave.open("Ludvig Forssell - A Phantom Pain [lyric video]-wlp8GimssgI.wav")
        #self.audio = input_data[1][0]
        signal = input_data.readframes(-1)
        signal = np.fromstring(signal, 'Int16')
        self.duration = 5000

        self.start = 0
        #print(self.audio[self.start * self.duration:(self.start + 1) * self.duration])

        f = Figure(figsize=(5, 5), dpi=100)
        print(len(signal))

        self.ax1 = f.add_subplot(111)

        self.ax1.plot(signal[::5000])

        canvas = FigureCanvasTkAgg(f, self)
        anim_void = anim.FuncAnimation(f, self.update_plot, interval=1000, blit=False)
        canvas.show()
        canvas.get_tk_widget().grid(row=0, column=1)
        canvas._tkcanvas.grid(row=0, column=1)


    def update_plot(self, i):
        pass
        #self.ax1.clear()
        #self.start+=1
        #self.ax1.plot(self.audio[self.start*self.duration:(self.start+1)*self.duration])


app = FrequencyGraph()
app.mainloop()
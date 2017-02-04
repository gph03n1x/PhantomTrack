#!/usr/bin/env python
import os
import os.path
import subprocess
from PyQt5.QtCore import QThread

FFMPEG_BIN = "bin/ffmpeg.exe"
LIBRARY_PATH = "library/"
MUSIC_PATH = "D:/Music/"
PLOT_PATH = LIBRARY_PATH + "plots/"

# TODO
class YoutubeDownloader(QThread):
    def set_(self, links):
        self.links = links

    def run(self):
        for link in self.links:
            cmd = 'youtube-dl --ffmpeg-location \"' + FFMPEG_BIN + '\" --extract-audio --audio-format mp3 ' + link
            print(cmd)

            self.download_status.setText(str(subprocess.check_output(cmd)))

        for item in os.listdir('.'):
            if os.path.isfile(item) and item.endswith(".mp3"):
                os.rename(item, MUSIC_PATH + item)

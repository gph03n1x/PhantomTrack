#!/usr/bin/env python
import os
import os.path
import subprocess
from PyQt5.QtCore import QThread

from core.config import fetch_options, get_default_path

options = fetch_options()
FFMPEG_BIN = options['paths']['ffmpeg_bin']
PLOT_PATH = options['paths']['plot_path']
MUSIC_PATH = get_default_path()

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

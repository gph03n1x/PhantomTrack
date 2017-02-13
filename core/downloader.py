#!/usr/bin/env python
import os
import re
import os.path

from PyQt5.QtCore import QProcess

from core.config import fetch_options, get_default_path

options = fetch_options()
FFMPEG_BIN = options['paths']['ffmpeg_bin']
PLOT_PATH = options['paths']['plot_path']
MUSIC_PATH = get_default_path()


class YoutubeDownloader:
    def __init__(self, links, label, button, progress, refresh_method):
        self.links = links
        self.label = label
        self.button = button
        self.progress = progress
        self.refresh_method = refresh_method

        self.process = QProcess()
        self.process.readyRead.connect(self.update_progress)
        self.process.started.connect(lambda: self.button.setEnabled(False))
        self.process.finished.connect(self.download_complete)

    def download_complete(self):
        if len(self.links) > 0:
            self.download()
        else:
            self.move_files()

    def move_files(self):
        self.label.setText("Moving to music folder...")
        default_path = fetch_options("PhantomTrack.cfg")['paths']['music_path'].split(';')[0] + "/"
        for item in os.listdir('.'):
            if os.path.isfile(item) and item.endswith(".mp3"):
                try:
                    os.rename(item, default_path + item)
                except Exception as exc:
                    print(exc)

        self.refresh_method()

        self.label.setText("")
        self.button.setEnabled(True)

    def update_progress(self):
        data = str(self.process.readAll())
        percentage = re.search("\d+\.\d+%", data)
        if percentage:
            self.progress.setValue(int(percentage.group(0).replace("%", "").split(".")[0]))

    def begin(self):
        self.download()

    def download(self):
        link = self.links.pop()
        self.label.setText("Downloading " + link)
        cmd = 'youtube-dl --ffmpeg-location \"' + FFMPEG_BIN + '\" --extract-audio --audio-format mp3 ' + link
        self.process.start(cmd)

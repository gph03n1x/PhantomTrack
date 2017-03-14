#!/usr/bin/env python
import os
import re
import os.path

from PyQt5.QtCore import QProcess

from core.config import fetch_options, get_default_path, parse_command

options = fetch_options()
FFMPEG_BIN = options['paths']['ffmpeg_bin']
MUSIC_PATH = get_default_path()
YOUTUBE_CMD = options['commands']['download']
THUMBNAILS = options['paths']['thumbnails']


class YoutubeDownloader:
    def __init__(self, links, label, button, progress, done_method):
        """
        Initializes class variables and creates a qprocess which is connected with
        the appropriate slots.
        :param links:
        :param label:
        :param button:
        :param progress:
        :param done_method:
        """
        self.links = links
        self.label = label
        self.button = button
        self.progress = progress
        self.done_method = done_method

        self.process = QProcess()
        self.process.readyRead.connect(self.update_progress)
        self.process.started.connect(lambda: self.button.setEnabled(False))
        self.process.finished.connect(self.download_complete)

        self.download_input = {'ffmpeg': FFMPEG_BIN}

    def download_complete(self):
        """
        If there still links to download, downloads next one
        else moves tmp mp3 files.
        :return:
        """
        if len(self.links) > 0:
            self.download()
        else:
            self.move_files()

    def move_files(self):
        """
        Moves mp3 files and thumbnails to the default music folder
        and the thumbnail folder. When it is done calls the done_method.
        :return:
        """
        self.label.setText("Moving to music folder...")
        default_path = fetch_options()['paths']['music_path'].split(';')[0] + "/"
        for item in os.listdir('.'):
            if os.path.isfile(item) and item.endswith(".mp3"):
                try:
                    os.rename(item, default_path + item)
                except Exception as exc:
                    print(exc)
            if os.path.isfile(item) and item.endswith(".jpg"):
                try:
                    os.rename(item, THUMBNAILS + item)
                except Exception as exc:
                    print(exc)

        self.done_method()

    def update_progress(self):
        """
        Reads the percentage of the download progress and updates the progress bar
        :return:
        """
        data = str(self.process.readAll())
        percentage = re.search("\d+\.\d+%", data)
        if percentage:
            self.progress.setValue(int(percentage.group(0).replace("%", "").split(".")[0]))

    def begin(self):
        """
        Starts the first download
        :return:
        """
        self.download()

    def download(self):
        """
        Gets the first link in the list and starts downloading it.
        :return:
        """
        link = self.links.pop()
        self.label.setText("Downloading " + link)
        self.download_input['link'] = link
        cmd = parse_command(YOUTUBE_CMD, self.download_input)
        self.process.start(cmd)

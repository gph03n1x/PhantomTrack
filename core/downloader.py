#!/usr/bin/env python
import os
import re
import os.path

from PyQt5.QtCore import QThread
import youtube_dl
from core.settings import FFMPEG, DOWNLOAD_COMMAND, THUMBNAILS_DIRECTORY
from core.models import MusicPaths


class YoutubeDownloader(QThread):
    def __init__(self, links, label, button, progress, done_method, session):
        QThread.__init__(self)
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
        self.session = session

        self.download_input = {'ffmpeg': FFMPEG}

        self.ydl_opts = {
            'writethumbnail': True,
            'format': 'bestaudio/best',
            'ffmpeg_location': FFMPEG,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [self.update_progress],
        }

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
        default_path = self.session.query(MusicPaths).filter(MusicPaths.is_primary==True)
        for item in os.listdir('.'):
            if os.path.isfile(item) and item.endswith(".mp3"):
                try:
                    os.rename(item, default_path + item)
                except Exception as exc:
                    print(exc)
            if os.path.isfile(item) and item.endswith(".jpg"):
                try:
                    os.rename(item, THUMBNAILS_DIRECTORY + item)
                except Exception as exc:
                    print(exc)

        self.done_method()

    def update_progress(self, status):
        """
        Reads the percentage of the download progress and updates the progress bar
        :return:
        """
        percentage = re.search("\d+\.\d+%", str(status))
        if percentage:
            self.progress.setValue(int(percentage.group(0).replace("%", "").split(".")[0]))

    def run(self):
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

        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([link])
        self.download_complete()

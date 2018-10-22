#!/usr/bin/env python
import os
import os.path
from PyQt5.QtCore import QProcess
from coreconfig import fetch_options, parse_command, find_path


options = fetch_options()
FFMPEG_BIN = options['paths']['ffmpeg_bin']
WAVE_CMD = options['commands']['wave_conversion']


class WaveConverter:

    def __init__(self, filename, on_finish):
        self.full_path = find_path(filename)
        self.wav_name = filename.replace(".mp3", ".wav")
        self.convert_process = QProcess()
        self.convert_process.finished.connect(lambda: on_finish(self.wav_name))

    def convert(self):
        """
        Calls the wave conversion command.
        """
        if os.path.isfile(self.full_path):
            command_input = {'ffmpeg': FFMPEG_BIN, 'song': self.full_path, 'wave': self.wav_name}
            cmd = parse_command(WAVE_CMD, command_input)
            self.convert_process.start(cmd)

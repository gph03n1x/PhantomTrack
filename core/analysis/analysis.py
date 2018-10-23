#!/usr/bin/env python
import os
import os.path
from PyQt5.QtCore import QProcess
from core.utils import parse_command
from core.settings import WAVE_COMMAND, FFMPEG




class WaveConverter:

    def __init__(self, filename, on_finish):
        self.full_path = filename
        self.wav_name = filename.replace(".mp3", ".wav")
        self.convert_process = QProcess()
        self.convert_process.finished.connect(lambda: on_finish(self.wav_name))

    def convert(self):
        """
        Calls the wave conversion command.
        """
        if os.path.isfile(self.full_path):
            command_input = {'ffmpeg': FFMPEG, 'song': self.full_path, 'wave': self.wav_name}
            cmd = parse_command(WAVE_COMMAND, command_input)
            self.convert_process.start(cmd)

#!/usr/bin/env python
from difflib import SequenceMatcher


def similar(a, b):
    """
    http://stackoverflow.com/questions/17388213/find-the-similarity-percent-between-two-strings
    Gets the similar ratio of two strings.
    :return:
    """
    return SequenceMatcher(None, a, b).ratio()


def parse_command(command, keys):
    """
    Parses the arguments from a dictionary in a command.
    :param command:
    "{ffmpeg}" -i "{song}" -acodec pcm_u8 -ar 22050 "{wave}"
    :param keys:
    {'ffmpeg': "path/ffmpeg.exe", 'song': "1234.mp3", 'wave': "1234.wav"}
    :return:
    "path/ffmpeg.exe" -i "1234.mp3" -acodec pcm_u8 -ar 22050 "1234.wav"
    """
    return command.format(**keys)


def get_commit_hash():
    """
    Gets current commit's hash from .git/refs/heads/master
    """
    master_file = open(".git/refs/heads/master", "r")
    version = master_file.read().strip()
    master_file.close()
    return version
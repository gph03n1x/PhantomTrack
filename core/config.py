#!/usr/bin/env python
import configparser
import os
import os.path
from difflib import SequenceMatcher


def similar(a, b):
    """
    http://stackoverflow.com/questions/17388213/find-the-similarity-percent-between-two-strings
    Gets the similar ratio of two strings.
    :return:
    """
    return SequenceMatcher(None, a, b).ratio()

def rename_config():
    """
    Creates a pt.cfg if there isn't one by renaming
    the pt.example.cfg.
    :return:
    """
    if not os.path.exists('pt.cfg'):
        try:
            os.rename('pt.example.cfg', 'pt.cfg')
        except OSError:
            print("[-] You are missing your pt.cfg and the app couldn't find pt.example.cfg to substitute it.")


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


def get_default_path():
    """
    Returns the first path defined in music_path as default path.
    :return:
    """
    return fetch_options()['paths']['music_path'].split(';')[0] + '/'


def find_path(filename):
    """
    retrieves a song path
    :param filename:
    :return:
    """
    paths = fetch_options()['paths']['music_path'].split(';')
    for path in paths:
        full_path = path+"/"+filename
        if os.path.exists(full_path):
            return full_path
    raise IOError("File was removed or doesn't exist")


def update_music_paths(paths):
    """
    joins the paths with ';', updates the music_path
    :param paths:
    :return:
    """
    paths = ";".join(paths)

    config = configparser.ConfigParser()
    config.read('pt.cfg')

    if not config.has_section('paths'):
        config.add_section('paths')

    config.set('paths', 'MUSIC_PATH', paths)

    with open('pt.cfg', 'w') as configfile:
        config.write(configfile)


def fetch_options(cfg_file="pt.cfg"):
    """
    Creates a dictionary with the configure options.
    :param cfg_file:
    :return:
    """
    rename_config()
    options = {}
    config = configparser.RawConfigParser()

    if __name__ == '__main__':
        config.read('../'+cfg_file)
    else:
        config.read(cfg_file)

    for sect in config.sections():
        options[sect] = {}
        for option in config.options(sect):
            # If it is a number we will attempt to convert to int
            try:
                value = int(config.get(sect, option))
            except ValueError:
                value = config.get(sect, option)

            options[sect][option] = value

    return options

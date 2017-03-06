#!/usr/bin/env python
from core.config import fetch_options

def create_playlist(name, songs):
    playlist = open(fetch_options()['paths']['playlist'] + name + ".lst", "wb")
    for song in songs:
        song_newline = song + "\n"
        playlist.write(song_newline.encode())
    playlist.close()

def read_playlist(name):
    try:
        playlist = open(fetch_options()['paths']['playlist'] + name + ".lst", "rb")
    except IOError:
        return None
    data = playlist.read().decode()
    playlist.close()
    return data
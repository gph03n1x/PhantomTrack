#!/usr/bin/env python
import os

from core.settings import fetch_options

def create_playlist(name, songs):
    if not songs:
        if os.path.exists(fetch_options()['paths']['playlist'] + name + ".lst"):
            os.remove(fetch_options()['paths']['playlist'] + name + ".lst")
        return
        # delete the playlist
    playlist = open(fetch_options()['paths']['playlist'] + name + ".lst", "wb")
    for song in songs:
        song_newline = song.split("\\")[-1] + "\n"
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
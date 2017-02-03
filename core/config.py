#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import configparser


def get_commit_hash():
    master_file = open(".git/refs/heads/master", "r")
    version = master_file.read().strip()
    master_file.close()
    return version


def add_to_info(song, duration):
    # TODO: Improve this
    config = configparser.ConfigParser()
    config.read('info.cfg')

    if not config.has_section('duration'):
        print("doesn't have")
        config.add_section('duration')

    config.set('duration', song, str(duration))
    with open('info.cfg', 'w') as configfile:
        config.write(configfile)


def fetch_options(cfg_file="PhantomTrack.cfg"):
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

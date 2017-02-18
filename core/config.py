#!/usr/bin/env python
# -*- coding: utf-8 -*-
import configparser
import os
import os.path


def rename_config():
    if not os.path.exists('pt.cfg'):
        try:
            os.rename('pt.example.cfg', 'pt.cfg')
        except OSError:
            print("[-] You are missing your pt.cfg and the app couldn't find pt.example.cfg to substitute it.")



def parse_command(command, keys):
    return command.format(**keys)


def get_commit_hash():
    master_file = open(".git/refs/heads/master", "r")
    version = master_file.read().strip()
    master_file.close()
    return version


def get_default_path():
    return fetch_options()['paths']['music_path'].split(';')[0] + '/'


def update_music_paths(paths):
    paths = ";".join(paths)

    config = configparser.ConfigParser()
    config.read('pt.cfg')

    if not config.has_section('paths'):
        config.add_section('paths')

    config.set('paths', 'MUSIC_PATH', paths)

    with open('pt.cfg', 'w') as configfile:
        config.write(configfile)


def fetch_options(cfg_file="pt.cfg"):
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

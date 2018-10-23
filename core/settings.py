#!/usr/bin/env python
from decouple import Config, RepositoryEnv

DOTENV_FILE = 'phantom.env'
env_config = Config(RepositoryEnv(DOTENV_FILE))

# use the Config().get() method as you normally would since
# decouple.config uses that internally.
FFMPEG = env_config.get('FFMPEG')
PRIMARY_MUSIC_PATH = env_config.get('PRIMARY_MUSIC_PATH')

THUMBNAILS_DIRECTORY = env_config.get('THUMBNAILS_DIRECTORY')
THUMBNAILS_HEIGHT = env_config.get('THUMBNAILS_HEIGHT', cast=int)
THUMBNAILS_WIDTH = env_config.get('THUMBNAILS_WIDTH', cast=int)

WAVE_WIDGET_ENABLED = env_config.get('WAVE_WIDGET_ENABLED', cast=bool)
WAVE_WIDGET_BARS = env_config.get('WAVE_WIDGET_BARS', cast=int)
WAVE_WIDGET_REFRESH_RATE = env_config.get('WAVE_WIDGET_REFRESH_RATE', cast=int)
WAVE_WIDGET_BETWEEN = env_config.get('WAVE_WIDGET_BETWEEN', cast=int)
WAVE_WIDGET_HEIGHT = env_config.get('WAVE_WIDGET_HEIGHT', cast=int)

DOWNLOAD_COMMAND = env_config.get('DOWNLOAD_COMMAND')
WAVE_COMMAND = env_config.get('WAVE_COMMAND')

DB_ECHO = True
DB_URL = "sqlite:///sqlite.db"
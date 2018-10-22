#!/usr/bin/env python
from decouple import Config, RepositoryEnv

DOTENV_FILE = '~/phantom.env'
env_config = Config(RepositoryEnv(DOTENV_FILE))

# use the Config().get() method as you normally would since
# decouple.config uses that internally.
# i.e. config('SECRET_KEY') = env_config.get('SECRET_KEY')
SECRET_KEY = env_config.get('SECRET_KEY')

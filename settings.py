from os import path
from dotenv import load_dotenv

import moncli

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '../.env'))

moncli.api.connection_timeout = 60
load_dotenv()


import os

import flask

from icv7 import config
from icv7.utilities import clients
from monday.base import BaseItem


def create_app():
    configuration = os.environ['APP_SETTINGS']

    app = flask.Flask('eric')

    app.config.from_object(configuration)

    return app

test = BaseItem(1649471278)
import os

import flask

from icv7 import config
from icv7.utilities import clients


def create_app():
    configuration = os.environ['APP_SETTINGS']

    app = flask.Flask('eric')

    app.config.from_object(configuration)

    return app

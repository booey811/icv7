import os

import flask

from icv7 import config
from icv7.utilities import clients


def create_app():
    if os.environ['ENV'] == 'prod':
        configuration = config.ProdConfig
    else:
        configuration = config.DevConfig

    app = flask.Flask('eric')

    app.config.from_object(configuration)

    return app

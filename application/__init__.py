import os
from datetime import datetime
import json

import flask

from . import config
from .monday import BaseItem, inventory
from .utilities import clients
from .phonecheck import phonecheck, CannotFindReportThroughIMEI

log_board = clients.monday.system.get_boards(ids=[1760764088])[0]


class CustomLogger:
    """Object for managing logging as Flask logging is a nightmare
    Dumps information to a monday item with log file"""

    def __init__(self):
        if os.environ['ENV'] in ['production', 'test']:
            self.debug = False
        else:
            self.debug = True

        self._log_file_path = None
        self._log_name = self._generate_log_file_name()
        self._log_board = log_board

        self._log_lines = []

    @staticmethod
    def _generate_log_file_name():
        now = datetime.now()
        date_time = now.strftime("%d%b|%H-%M-%S")
        name = f'Instance-{date_time}.txt'
        return name

    def _create_log(self):
        with open(self.log_file_path, 'w') as log:
            for line in self._log_lines:
                log.write(line)
                log.write('\n')

        return True

    @property
    def log_file_path(self):
        if not self._log_file_path:
            self._log_file_path = f'tmp/logs/{self._log_name}'
        return self._log_file_path

    def log(self, log_line):
        self._log_lines.append(log_line)
        if self.debug:
            print(log_line)

    def soft_log(self):
        """creates a log entry in the logs board but does not halt execution"""
        # Create the log file

        self.log('==== SOFT LOG REQUESTED =====')
        self._create_log()
        col_vals = {
            'status': {'label': 'Soft'}
        }
        log_item = self._log_board.add_item(
            item_name=self._log_name,
            column_values=col_vals
        )
        file_column = log_item.get_column_value(id='file')
        log_item.add_file(file_column, self._log_file_path)

        print('==== SOFT LOG REQUESTED =====')

        return log_item

    def hard_log(self):
        """creates a log entry in the logs board and halts execution"""
        self.log('==== HARD LOG REQUESTED =====')
        # Create the log file
        self._create_log()
        col_vals = {
            'status': {'label': 'Hard'}
        }
        log_item = self._log_board.add_item(
            item_name=self._log_name,
            column_values=col_vals
        )
        file_column = log_item.get_column_value(id='file')
        log_item.add_file(file_column, self._log_file_path)

        self.clear()
        raise Exception(f'Hard Log Requested: {self._log_name}')

    def clear(self):
        """Delete the generated log file"""
        try:
            os.remove(self.log_file_path)
        except FileNotFoundError:
            pass


# App functions
def verify_monday(webhook):
    """Takes webhook information, authenticates if required, and decodes information
    Args:
        webhook (request): Payload received from Monday's Webhooks
    Returns:
        dictionary: contains various information from Monday, dependent on type of webhook sent
    """

    data = webhook.decode('utf-8')
    data = json.loads(data)
    if "challenge" in data.keys():
        authtoken = {"challenge": data["challenge"]}
        raise ChallengeReceived(authtoken)
    else:
        return data


def create_app():
    # Detect Environment & Retreive config
    env = os.environ['ENV']
    if env == 'production':
        print('Config:Production')
        configuration = config.ProdConfig()
    elif env in ['devlocal', 'devserver']:
        print('Config:DevLocal')
        configuration = config.DevConfig()
    else:
        raise Exception('ENV config var is not set correctly - cannot boot')

    # Create and configure app
    app = flask.Flask('eric')
    app.config.from_object(configuration)
    return app


class ChallengeReceived(Exception):
    """
    Exception that is thrown when the Monday challenge is received, stores the challenge token for return to app
    level function
    """

    def __init__(self, token):
        self.token = token

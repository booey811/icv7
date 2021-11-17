import time

import pytest

from application.utilities import clients
from application import CustomLogger, BaseItem


@pytest.fixture(scope='session')
def clients_object():
    return clients


@pytest.fixture(scope='function')
def logger():
    logger = CustomLogger()
    yield logger
    logger.clear()


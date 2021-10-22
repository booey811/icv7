import pytest

from icv7.utilities import clients
from icv7 import CustomLogger


@pytest.fixture(scope='session')
def clients_object():
    return clients


@pytest.fixture(scope='function')
def logger():
    logger = CustomLogger()
    yield logger
    logger.clear()

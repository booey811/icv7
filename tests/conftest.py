import pytest

from icv7.utilities import clients


@pytest.fixture(scope='session')
def clients_object():
    return clients

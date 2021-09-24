import pytest

from icv7.utilities import clients
from icv7.monday.base import BaseItem


@pytest.fixture(scope='session')
def read_only_item_id():
    return '1649471278'


@pytest.fixture(scope='session')
def system_item_id():
    return '1139943185'


@pytest.fixture(scope='session')
def email_item_id():
    return '1649459824'


@pytest.fixture(scope='session')
def error_item_id():
    return '1649463539'


@pytest.fixture(scope='session')
def dev_test_board_id():
    return '1139943160'


@pytest.fixture(scope='session')
def moncli_read_only_item(read_only_item_id):
    return clients.monday.system.get_items(ids=[read_only_item_id])[0]


@pytest.fixture(scope='session')
def moncli_system_item(system_item_id):
    return clients.monday.system.get_items(ids=[system_item_id])[0]


@pytest.fixture(scope='session')
def moncli_email_item(email_item_id):
    return clients.monday.system.get_items(ids=[email_item_id])[0]


@pytest.fixture(scope='session')
def moncli_error_item(error_item_id):
    return clients.monday.system.get_items(ids=[error_item_id])[0]


@pytest.fixture(scope='session')
def eric_read_only_item(read_only_item_id):
    return BaseItem(read_only_item_id)

@pytest.fixture(scope='class')
def eric_system_item(system_item_id):
    return BaseItem(system_item_id)


@pytest.fixture(scope='session')
def eric_email_item(email_item_id):
    return BaseItem(email_item_id)


@pytest.fixture(scope='session')
def eric_error_item(error_item_id):
    return BaseItem(error_item_id)

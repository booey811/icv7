"""
Once all column values are complete, a fixture for reverting test items to their default state will be required, to be
called at the end of a column_value test class
"""



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


@pytest.fixture(scope='function')
def eric_system_item(moncli_system_item):
    """Returns an Eric item retrieved with the monday.system client
    Need to add the item as yield instead of return then change the item to default state afterwards"""
    return BaseItem(moncli_system_item)


@pytest.fixture(scope='function')
def eric_email_item(moncli_email_item):
    """Returns an Eric item retrieved with the monday.email client
    Need to add the item as yield instead of return then change the item to default state afterwards"""
    return BaseItem(moncli_email_item)


@pytest.fixture(scope='function')
def eric_error_item(moncli_error_item):
    """Returns an Eric item retrieved with the monday.error client
    Need to add the item as yield instead of return then change the item to default state afterwards"""
    return BaseItem(moncli_error_item)

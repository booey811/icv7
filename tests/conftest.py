import pytest


@pytest.fixture(scope='session')
def dev_test_board_system_item_id():
    return '1139943185'


@pytest.fixture(scope='session')
def dev_test_board_email_item_id():
    return '1649459824'


@pytest.fixture(scope='session')
def dev_test_board_error_item_id():
    return '1649463539'


@pytest.fixture(scope='session')
def dev_test_board_id():
    return '1139943160'

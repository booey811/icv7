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


@pytest.fixture(scope="session")
def temp_mainboard_item(logger):
    item = BaseItem(logger, board_id=349212843)
    item.notifications_status.label = "OFF"
    item.email.value = "blankemail@te811est.com"
    item.phone.value = 4474206920
    item.new_item('Test Item', convert_eric=True)
    time.sleep(1)
    yield item
    item.moncli_obj.delete()


@pytest.fixture(scope="session")
def temp_devtest_item(logger):
    item = BaseItem(logger, board_id=1139943160)
    item.text.value = "TEST TEXT"
    item.numbers.value = 98426742
    item.new_item('Test Item', convert_eric=True)
    time.sleep(8)
    yield item
    item.moncli_obj.delete()

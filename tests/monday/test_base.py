import moncli.entities
import pytest

from icv7.monday import base
from icv7.utilities import clients
from icv7.monday import config


@pytest.fixture()
def system_client_test_moncli_item(dev_test_board_system_item_id):
    return clients.monday.system.get_items(ids=[dev_test_board_system_item_id])[0]


@pytest.fixture(scope='class')
def example_item_from_item_id(dev_test_board_system_item_id):
    return base.BaseItem(dev_test_board_system_item_id)


@pytest.fixture(scope='class')
def example_item_from_board_id(dev_test_board_id):
    return base.BaseItem(board_id=dev_test_board_id)


@pytest.fixture(scope='module')
def column_mapping_data_for_test_board(dev_test_board_id):
    return config.BOARD_MAPPING_DICT[dev_test_board_id]


class TestItemAttributesFromItemID:

    def test_id_is_correct(self, example_item_from_item_id, dev_test_board_system_item_id):
        '''
        test that the eric item acquired through an item is search has the same id as the monday item used to create it
        :param example_item_from_item_id:
        :param dev_test_board_system_item_id:
        :return:
        '''
        assert example_item_from_item_id._id == dev_test_board_system_item_id

    def test_board_id_is_correct(self, example_item_from_item_id, dev_test_board_id):
        '''
        test that the board acquired through the monday item has the correct id
        :param example_item_from_item_id:
        :param dev_test_board_id:
        :return:
        '''
        assert example_item_from_item_id._moncli_board_obj.id == dev_test_board_id

    def test_moncli_item_object_is_present_and_correct(self, example_item_from_item_id):
        assert type(example_item_from_item_id._moncli_obj) == moncli.entities.Item

    def test_moncli_board_object_is_present_and_correct(self, example_item_from_item_id):
        assert type(example_item_from_item_id._moncli_board_obj) == moncli.entities.Board

    def test_no_column_changes_are_staged_after_instantiation(self, example_item_from_item_id):
        assert example_item_from_item_id._staged_changes == {}


class TestItemAttributesFromBoardID:

    def test_board_id_is_correct(self, example_item_from_board_id, dev_test_board_id):
        assert example_item_from_board_id._board_id == dev_test_board_id

    def test_moncli_board_object_is_present_and_correct(self, example_item_from_board_id):
        assert type(example_item_from_board_id._moncli_board_obj) == moncli.entities.Board

    def test_no_column_changes_are_staged_after_instantiation(self, example_item_from_board_id):
        assert example_item_from_board_id._staged_changes == {}


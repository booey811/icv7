import moncli.entities
import pytest

from icv7.monday import base
from icv7.utilities import clients


@pytest.fixture()
def system_client_test_moncli_item(dev_test_board_system_item_id):
    return clients.monday.system.get_items(ids=[dev_test_board_system_item_id])[0]


@pytest.fixture(scope='class')
def example_item_from_item_id(dev_test_board_system_item_id):
    print('INIT FROMID')
    return base.BaseItem(dev_test_board_system_item_id)


@pytest.fixture(scope='class')
def example_item_from_board_id(dev_test_board_id):
    print('INIT FROM BOARD')
    return base.BaseItem(board_id=dev_test_board_id)


class TestItemFromItemID:

    def test_id_is_correct(self, example_item_from_item_id, dev_test_board_system_item_id):
        assert example_item_from_item_id._id == dev_test_board_system_item_id

    def test_board_id_is_correct(self, example_item_from_item_id, dev_test_board_id):
        assert example_item_from_item_id._moncli_board_obj.id == dev_test_board_id

    def test_moncli_item_object_is_present_and_correct(self, example_item_from_item_id):
        assert type(example_item_from_item_id._moncli_obj) == moncli.entities.Item

    def test_moncli_board_object_is_present_and_correct(self, example_item_from_item_id):
        assert type(example_item_from_item_id._moncli_board_obj) == moncli.entities.Board

    def test_no_column_changes_are_staged_after_instantiation(self, example_item_from_item_id):
        assert example_item_from_item_id._staged_changes == {}


class TestItemFromBoardID:

    def test_board_id_is_correct(self, example_item_from_board_id, dev_test_board_id):
        assert example_item_from_board_id._board_id == dev_test_board_id

    def test_moncli_board_object_is_present_and_correct(self, example_item_from_board_id):
        assert type(example_item_from_board_id._board_id)


class TestItemsAreSimilarObjects:
    pass


class TestGenericBoardAttributes:

    def test_one(self, example_item_from_item_id, example_item_from_board_id):
        print('test one results')

    def test_two(self, example_item_from_item_id, example_item_from_board_id):
        print('test two results')

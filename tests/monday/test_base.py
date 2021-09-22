import moncli.entities
import pytest

from icv7.monday import base
from icv7.utilities import clients


@pytest.fixture()
def system_client_test_moncli_item(dev_test_board_system_item_id):
    return clients.monday.system.get_items(ids=[dev_test_board_system_item_id])[0]


class TestCreationFromID:

    @pytest.fixture(scope='class')
    def example_item(self, dev_test_board_system_item_id):
        return base.BaseItem(dev_test_board_system_item_id)

    def test_id_is_correct(self, example_item, dev_test_board_system_item_id):
        assert example_item._id == dev_test_board_system_item_id

    def test_board_id_is_correct(self, example_item, dev_test_board_id):
        assert example_item._moncli_board_obj.id == dev_test_board_id

    def test_moncli_item_object_is_present_and_correct(self, example_item):
        assert type(example_item._moncli_obj) == moncli.entities.Item

    def test_moncli_board_object_is_present_and_correct(self, example_item):
        assert type(example_item._moncli_board_obj) == moncli.entities.Board

    def test_no_column_changes_are_staged_after_instantiation(self, example_item):
        assert example_item._staged_changes == {}

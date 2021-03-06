import moncli.entities
import pytest

from application.monday import base
from application.utilities import clients
from application.monday import config
from application import BaseItem


@pytest.fixture(scope='class')
def example_item_from_item_id(logger, system_item_id):
    return base.BaseItem(logger, system_item_id)


@pytest.fixture(scope='class')
def example_item_from_board_id(logger, dev_test_board_id):
    return base.BaseItem(logger, board_id=dev_test_board_id)


@pytest.fixture(scope='module')
def column_mapping_data_for_test_board(dev_test_board_id):
    return config.BOARD_MAPPING_DICT[dev_test_board_id]


class TestItemAttributesFromItemID:

    def test_id_is_correct(self, eric_system_item, system_item_id):
        """
        test that the eric item acquired through an item is search has the same id as the monday item used to create it
        """
        assert eric_system_item.mon_id == system_item_id

    def test_board_id_is_correct(self, eric_system_item, dev_test_board_id):
        """
        test that the board acquired through the monday item has the correct id
        :param example_item_from_item_id:
        :param dev_test_board_id:
        :return:
        """
        assert eric_system_item.moncli_board_obj.id == dev_test_board_id

    def test_moncli_item_object_is_present_and_correct(self, eric_read_only_item):
        assert type(eric_read_only_item.moncli_obj) == moncli.entities.Item

    def test_moncli_board_object_is_present_and_correct(self, eric_read_only_item):
        assert type(eric_read_only_item.moncli_board_obj) == moncli.entities.Board

    def test_no_column_changes_are_staged_after_instantiation(self, eric_read_only_item):
        assert eric_read_only_item.staged_changes == {}


class TestItemAttributesFromBoardID:

    def test_board_id_is_correct(self, eric_read_only_item, dev_test_board_id):
        assert eric_read_only_item.board_id == dev_test_board_id

    def test_moncli_board_object_is_present_and_correct(self, eric_read_only_item):
        assert type(eric_read_only_item.moncli_board_obj) == moncli.entities.Board

    def test_no_column_changes_are_staged_after_instantiation(self, eric_read_only_item):
        assert eric_read_only_item.staged_changes == {}


class TestNewItemCreation:

    def test_create_simple_new_monday_item(self, dev_test_board_id, logger):

        eric = base.BaseItem(logger, board_id=dev_test_board_id)
        item = eric.new_item('NEW TEST ITEM')

        assert type(item) == moncli.entities.Item

        item.delete()

    def test_creating_a_blank_monday_item_from_an_eric_item_and_adopting_its_values(self, temp_mainboard_item, logger):
        blank_eric_item = temp_mainboard_item
        # Create and adopt monday item
        blank_eric_item.new_item('Test Item', convert_eric=True)
        blank_eric_item.imeisn.value = "Test"
        blank_eric_item.commit()

        # Create check eric item
        check_eric_item = BaseItem(logger, blank_eric_item.mon_id)

        assert blank_eric_item.imeisn.value == check_eric_item.imeisn.value


class TestLogger:

    @pytest.fixture(scope='function')
    def logger(self, eric_read_only_item):
        return eric_read_only_item.logger

    def test_adding_log_line(self, logger):
        ori = len(logger._log_lines)
        logger.log('First Line')
        assert len(logger._log_lines) == ori + 1


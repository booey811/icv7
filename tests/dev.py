import pytest

from application import BaseItem, CustomLogger


@pytest.fixture
def temp_mainboard_item():
    item = BaseItem(CustomLogger(), board_id=349212843).new_item('Test Item')
    yield item
    item.de



def test_to_print_stock_levels_for_repair_to_an_item(temp_mainboard_item):
    """test creates a MainBoard Item for iPhone 7 Screen & Battery Repair, then checks the relvant stock levels and prints
    to the item """
    item = temp_mainboard_item
    assert True



def test_checking_stock_level_for_a_given_monday_repair_and_adjusting_staus():
    """test to adjust the stock level status of Mainboard item dependant on it's repairs"""


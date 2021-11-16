import pytest

from application import BaseItem, CustomLogger, inventory


@pytest.fixture
def ip8_batt_screen_repair(temp_mainboard_item):
    item = temp_mainboard_item
    item.device.add('iPhone 8')
    item.repairs.add(['Front Screen Universal', 'Battery'])
    item.commit()
    return item


def test_ip8_batt_screen_repair_fixture(ip8_batt_screen_repair):
    item = ip8_batt_screen_repair
    assert sorted(item.device.labels) == sorted(['iPhone 8'])
    assert sorted(item.repairs.labels) == sorted(['Front Screen Universal', 'Battery'])


def test_creating_a_blank_monday_item_from_an_eric_item_and_adopting_its_values(temp_mainboard_item):
    blank_eric_item = temp_mainboard_item
    # Create and adopt monday item
    blank_eric_item.new_item('Test Item', convert_eric=True)
    blank_eric_item.imeisn.value = "Test"
    blank_eric_item.commit()

    # Create check eric item
    check_eric_item = BaseItem(CustomLogger(), blank_eric_item.mon_id)

    assert blank_eric_item.imeisn.value == check_eric_item.imeisn.value


# def test_to_print_stock_levels_for_repair_to_an_item(ip8_batt_screen_repair):
#     """test creates a MainBoard Item for iPhone 7 Screen & Battery Repair, then checks the relvant stock levels and prints
#     to the item """
#     # Create test item
#     item = ip8_batt_screen_repair
#
#     # Get the required parts
#     inventory.check_stock()
#
#     assert True


def test_checking_stock_level_for_a_given_monday_repair_and_adjusting_staus():
    """test to adjust the stock level status of Mainboard item dependant on it's repairs"""

@pytest.mark.slow
class TestColumnValueSearches:

    def test_text_column_search(self, temp_devtest_item):
        test_item = temp_devtest_item
        item_ids = test_item.text.search(test_item.text.value)
        assert [item['id'] for item in item_ids] == [test_item.mon_id]

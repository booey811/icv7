import pytest

from application import BaseItem, CustomLogger

@pytest.fixture()
def eric_test_part_item():
    return BaseItem(CustomLogger(), 1226905145)  # TEST DEVICE TEST Screen Black

@pytest.mark.fully_functional
@pytest.mark.slow
class TestInventoryHelper:

    def test_adjust_stock_level(self, eric_test_part_item):
        """test that inventory.adjust_stock_level changes the stock level of an item on Monday"""
        eric_test_part_item = BaseItem(CustomLogger(), 1226905145)  # TEST DEVICE TEST Screen Black
        ori_value = eric_test_part_item.stock_level.value
        difference = 7  # arbitrary difference
        new_value = ori_value - difference

        eric_test_part_item.stock_level.value = new_value
        eric_test_part_item.commit()

        refetched_eric_test_part_item = BaseItem(CustomLogger(), 1226905145)
        refetched_value = refetched_eric_test_part_item.stock_level.value

        assert new_value == refetched_value



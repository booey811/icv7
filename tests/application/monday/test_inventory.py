import pytest

from application import BaseItem, inventory, CustomLogger


@pytest.fixture(scope="module")
def eric_test_part_item():
    eric = BaseItem(CustomLogger(), board_id=985177480)
    eric.new_item('TEST PART ITEM', convert_eric=True)
    yield eric
    eric.moncli_obj.delete()


@pytest.fixture
def ip8_batt_screen_repair(temp_mainboard_item):
    item = temp_mainboard_item
    item.device.add('iPhone 8')
    item.repairs.add(['Front Screen Universal', 'Battery'])
    item.device_colour.label = "Black"
    item.commit()
    return item


def test_ip8_batt_screen_repair_fixture(ip8_batt_screen_repair):
    item = ip8_batt_screen_repair
    assert sorted(item.device.labels) == sorted(['iPhone 8'])
    assert sorted(item.repairs.labels) == sorted(['Front Screen Universal', 'Battery'])


@pytest.mark.slow
class TestInventoryHelper:

    def test_adjust_stock_level(self, eric_test_part_item):
        """test that inventory.adjust_stock_level changes the stock level of an item on Monday"""
        test_item = eric_test_part_item
        ori_value = test_item.stock_level.value
        difference = 7  # arbitrary difference
        new_value = ori_value - difference

        test_item.stock_level.value = new_value
        test_item.commit()

        refetched_eric_test_part_item = BaseItem(CustomLogger(), test_item.mon_id)
        refetched_value = refetched_eric_test_part_item.stock_level.value

        assert new_value == refetched_value

    def test_low_stock_checker_adjusts_part_to_low_stock_when_stock_level_is_below_reorder_uncommitted(
            self,
            eric_test_part_item
    ):
        # Set stock_level < reorder point
        eric_test_part_item.stock_level.value = 15  # Arbitrary
        eric_test_part_item.reorder_point.value = 20  # Arbitrary

        calculated_low_stock_status = inventory._check_stock_against_reorder(eric_test_part_item)

        assert calculated_low_stock_status == "Below Reorder"

    def test_low_stock_checker_adjusts_part_to_healthy_stock_when_stock_level_is_above_reorder_uncommitted(
            self,
            eric_test_part_item
    ):
        # Set stock_level > reorder point
        eric_test_part_item.stock_level.value = 20  # Arbitrary
        eric_test_part_item.reorder_point.value = 15  # Arbitrary

        calculated_low_stock_status = inventory._check_stock_against_reorder(eric_test_part_item)

        assert calculated_low_stock_status == "Above Reorder"

    def test_low_stock_checker_adjusts_part_to_low_stock_when_stock_level_is_below_reorder_committed(
            self,
            eric_test_part_item
    ):
        # Set stock_level < reorder point
        eric_test_part_item.stock_level.value = 15  # Arbitrary
        eric_test_part_item.reorder_point.value = 20  # Arbitrary
        eric_test_part_item.commit()

        refresh_eric = BaseItem(CustomLogger(), eric_test_part_item.mon_id)

        calculated_low_stock_status = inventory._check_stock_against_reorder(refresh_eric)

        assert calculated_low_stock_status == "Below Reorder"

    def test_low_stock_checker_adjusts_part_to_healthy_stock_when_stock_level_is_above_reorder_committed(
            self,
            eric_test_part_item
    ):
        # Set stock_level > reorder point
        eric_test_part_item.stock_level.value = 20  # Arbitrary
        eric_test_part_item.reorder_point.value = 15  # Arbitrary
        eric_test_part_item.commit()

        refresh_eric = BaseItem(CustomLogger(), eric_test_part_item.mon_id)

        calculated_low_stock_status = inventory._check_stock_against_reorder(refresh_eric)

        assert calculated_low_stock_status == "Above Reorder"

    @pytest.mark.develop
    @pytest.mark.fully_functional
    def test_integrated_stock_adjustment_also_adjusts_stock_status_level_to_low_stock(self, eric_test_part_item):
        # Set stock_level < reorder
        eric_test_part_item.stock_level.value = 20  # Arbitrary
        eric_test_part_item.reorder_point.value = 15  # Arbitrary
        eric_test_part_item.commit()

        inventory.adjust_stock_level(eric_test_part_item.logger, eric_test_part_item,
                                     -10, eric_test_part_item)  # Sets stock_level to 20 - 10 < 15

        refresh_eric = BaseItem(CustomLogger(), eric_test_part_item.mon_id)

        assert refresh_eric.low_stock_status.label == "Below Reorder"

    @pytest.mark.fully_functional
    def test_integrated_stock_adjustment_also_adjusts_stock_status_level_to_low_stock(self, eric_test_part_item):
        # Set stock_level > reorder
        eric_test_part_item.stock_level.value = 15  # Arbitrary
        eric_test_part_item.reorder_point.value = 20  # Arbitrary
        eric_test_part_item.commit()

        inventory.adjust_stock_level(eric_test_part_item.logger, eric_test_part_item,
                                     10, eric_test_part_item)  # Sets stock_level to 15 + 10 > 20

        refresh_eric = BaseItem(CustomLogger(), eric_test_part_item.mon_id)

        assert refresh_eric.low_stock_status.label == "Above Reorder"

    def test_to_print_stock_levels_for_repair_to_an_item(self, ip8_batt_screen_repair):
        """test creates a MainBoard Item for iPhone 7 Screen & Battery Repair, then checks the relvant stock levels and prints
        to the item """
        # Create test item
        test_item = ip8_batt_screen_repair

        # Get the required parts
        stock_info = inventory.get_stock_info(test_item)

        stock_list = []
        for item in stock_info:
            stock_list.append(f"{item}: {stock_info[item]['stock_level']}")

        stock_string = "\n".join(stock_list)

        update = f"""STOCK LEVELS\n\n{stock_string}"""

        update_info = test_item.moncli_obj.add_update(body=update)

        assert "STOCK LEVELS" in update_info["body"]
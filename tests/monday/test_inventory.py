import pytest

from application import BaseItem, CustomLogger, inventory


@pytest.fixture(scope="module")
def eric_test_part_item():
    return BaseItem(CustomLogger(), 1226905145)  # TEST DEVICE TEST Screen Black


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

        refresh_eric = BaseItem(CustomLogger(), 1226905145)

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

        refresh_eric = BaseItem(CustomLogger(), 1226905145)

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
                                     -10)  # Sets stock_level to 20 - 10 < 15

        refresh_eric = BaseItem(CustomLogger(), 1226905145)

        assert refresh_eric.low_stock_status.label == "Below Reorder"

    @pytest.mark.fully_functional
    def test_integrated_stock_adjustment_also_adjusts_stock_status_level_to_low_stock(self, eric_test_part_item):
        # Set stock_level > reorder
        eric_test_part_item.stock_level.value = 15  # Arbitrary
        eric_test_part_item.reorder_point.value = 20  # Arbitrary
        eric_test_part_item.commit()

        inventory.adjust_stock_level(eric_test_part_item.logger, eric_test_part_item,
                                     10)  # Sets stock_level to 15 + 10 > 20

        refresh_eric = BaseItem(CustomLogger(), 1226905145)

        assert refresh_eric.low_stock_status.label == "Above Reorder"

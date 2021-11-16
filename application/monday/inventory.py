"""This module helps with the management of stock within monday, with most functions accepting item IDs, moncli objects
or eric objects """

from moncli.entities import Item as moncli_item

from .base import BaseItem

from typing import Union


# class PartsRetriever:
#     """deals with the messy conversions required to get parts items from mainboard items"""
#
#     def



def adjust_stock_level(logger, part_reference: Union[str, int], quantity, absolute=False):
    logger.log('Adjusting Stock Level')
    # Check part_reference input is valid
    if type(part_reference) in [str, int]:
        part = BaseItem(logger, part_reference)
    elif type(part_reference) is BaseItem:
        part = part_reference
    elif type(part_reference) is moncli_item:
        part = BaseItem(logger, moncli_item.id)
    else:
        logger.log(f'Invalid part_reference supplied to InventoryHelper.adjust_stock_level: '
                   f'{type(part_reference)}')
        logger.soft_log()
        raise Exception(f'Invalid part_reference supplied to InventoryHelper.adjust_stock_level: '
                        f'{type(part_reference)}')

    # Check part is from the PartsBoard
    if part.moncli_board_obj.id != '985177480':  # Parts Board ID
        logger.log(f'Invalid Monday Item supplied to InventoryHelper.adjust_stock_level: '
                   f'{part.moncli_board_obj.name}')
        raise Exception(f'Invalid Monday Item supplied to InventoryHelper.adjust_stock_level: '
                        f'{part.moncli_board_obj.name}')

    # Get current level (for logs)
    try:
        current_level = int(part.stock_level.value)
    except TypeError:
        current_level = 0

    # Adjust Stock Level
    if absolute:
        new_level = quantity
    else:
        new_level = current_level + quantity

    part.stock_level.value = new_level

    logger.log(f'Part: {part.name} | ID: {part.mon_id}')
    logger.log(f'Current: {current_level} | New: {new_level} | Diff: {quantity}')

    _check_and_adjust_for_low_stock(part)

    # Commit Changes
    part.commit()

    logger.log('Stock Level Adjusted')
    return new_level


def _check_stock_against_reorder(part_item: BaseItem) -> str:
    """
    Checks stock level of an item against it's reorder point, returning strings for the required Low Stock Status Label
    Args:
        part_item: Part Item to Check

    Returns:
        str: Required Label of the Low Stock Status

    """
    stock_level = part_item.stock_level.value
    reorder_point = part_item.reorder_point.value

    if stock_level > reorder_point:
        return "Above Reorder"
    elif stock_level <= reorder_point:
        return "Below Reorder"
    else:
        raise Exception(
            f'Stock Level and Reorder Point are Mathematically Impossible ({stock_level}, {reorder_point})')


def _check_and_adjust_for_low_stock(part_item: BaseItem):
    """Performs a quick check to see if a part is below/above it's reorder point, and acts accordingly"""

    # compare stock level with reorder point
    low_stock_status = part_item.low_stock_status.label

    # check 'Low Stock' status to see if this is correct
    low_stock_level = _check_stock_against_reorder(part_item)

    if low_stock_level != low_stock_status:
        part_item.low_stock_status.label = low_stock_level

    # Do not need to commit item as it is always committed when adjusting stock level


def get_stock_info(mainboard_item: BaseItem):
    """returns a dictionary of repair items and some basic info"""
    # get monday items
    # build dict: {name: NAME, eric: ERIC ITEM, stock: STOCK LEVEL, available: bool}
    result = {}
    return result

def get_parts(mainboard_item: BaseItem):
    """"""



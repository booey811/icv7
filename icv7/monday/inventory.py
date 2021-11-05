"""This module helps with the management of stock within monday, with most functions accepting item IDs, moncli objects
or eric objects """

from moncli.entities import Item as moncli_item

from .base import BaseItem

from typing import Union


def adjust_stock_level(logger, part_reference: Union[str, int], quantity):
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
    if part.moncli_board_obj.id != '985177480':
        logger.log(f'Invalid Monday Item supplied to InventoryHelper.adjust_stock_level: '
                   f'{part.moncli_board_obj.name}')
        raise Exception(f'Invalid Monday Item supplied to InventoryHelper.adjust_stock_level: '
                        f'{part.moncli_board_obj.name}')

    # Adjust Stock Level
    current_level = int(part.stock_level.value)
    new_level = current_level + quantity
    part.stock_level.value = new_level

    # Commit Changes
    part.commit()

    return new_level



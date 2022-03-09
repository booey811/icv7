"""This module helps with the management of stock within monday, with most functions accepting item IDs, moncli objects
or eric objects """

from moncli.entities import Item as moncli_item

import application
from .base import BaseItem
from .config import BOARD_MAPPING_DICT
from . import exceptions

from typing import Union

COLOURED_PARTS = [
    'TrackPad',
    'Charging Port',
    'Headphone Jack',
    'Home Button',
    'Front Screen Universal',
    'Front Screen',
    'Rear Glass',
    'Front Screen (LG)',
    'Front Screen (Tosh)',
    'Rear Housing',
    'TEST Screen'
]


def construct_search_terms_for_parts(mainboard_item: BaseItem, generic=False):
    mainboard_item.log(f"Generating Search Terms for {mainboard_item.name}: {mainboard_item.mon_id}")

    terms = []

    # If no repair is supplied, retrieve the following
    if not mainboard_item.repairs.ids or generic:
        mainboard_item.log("No Repairs Supplied - Fetching Screens, Battery & Rear Cam")
        terms.append(f"{mainboard_item.device.ids[0]}-{69}-{10}")  # Device screen black uni
        terms.append(f"{mainboard_item.device.ids[0]}-{84}-{10}")  # Device screen black tosh
        terms.append(f"{mainboard_item.device.ids[0]}-{83}-{10}")  # Device screen black lg
        terms.append(f"{mainboard_item.device.ids[0]}-{69}-{16}")  # Device screen white uni
        terms.append(f"{mainboard_item.device.ids[0]}-{84}-{16}")  # Device screen white tosh
        terms.append(f"{mainboard_item.device.ids[0]}-{83}-{16}")  # Device screen white lg
        terms.append(f"{mainboard_item.device.ids[0]}-{71}")  # Device battery
        terms.append(f"{mainboard_item.device.ids[0]}-{70}")  # Device r cam

    else:
        for repair_id in mainboard_item.repairs.ids:

            label = mainboard_item.repairs.settings[str(repair_id)]

            mainboard_item.log(f"Generating for {label}")

            if label in COLOURED_PARTS:
                if not mainboard_item.device_colour.index:
                    mainboard_item.log(f"No Colour Supplied - Autogenerating for Black and White")
                    terms.append(f"{mainboard_item.device.ids[0]}-{repair_id}-10")
                    terms.append(f"{mainboard_item.device.ids[0]}-{repair_id}-16")
                    continue
                else:
                    search_term = f"{int(mainboard_item.device.ids[0])}-{int(repair_id)}-{int(mainboard_item.device_colour.index)}"
            else:
                search_term = f"{mainboard_item.device.ids[0]}-{repair_id}"

            mainboard_item.log(f"Generated {search_term}")

            terms.append(search_term)

    return terms


def adjust_stock_level(logger, part_reference: Union[str, int, BaseItem], quantity, source_object: BaseItem,
                       absolute=False):
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
        new_level = current_level - quantity

    part.stock_level.value = new_level

    logger.log(f'Part: {part.name} | ID: {part.mon_id}')
    logger.log(f'Current: {current_level} | New: {new_level} | Diff: {quantity}')
    try:
        new_movement_item = _create_movement_record(
            eric_source_item=source_object,
            part_item=part,
            starting_stock_level=current_level,
            ending_stock_level=new_level
        )
    except exceptions.TagsOnPartsNotAvailableOnMovements as e:
        raise e

    _check_and_adjust_for_low_stock(part)

    # Commit Changes
    part.commit()




    logger.log('Stock Level Adjusted')
    return new_movement_item


def _create_movement_record(
        eric_source_item: BaseItem,
        part_item: BaseItem,
        starting_stock_level: int,
        ending_stock_level: int):
    """
function to construct an inventory movements item. Must be supplied with an eric source object, which can be a financial
board subitem (for completed repairs), a stock count item, an order item or a waste item which will be pointed back
to by the resultant Movements Board Item. Also requires a Parts Item and Stock Adjustment Data.
    Args:
        eric_source_item: the eric item that is in charge of checking out the required stock
        part_item: the eric part that is undergoing adjustment
        starting_stock_level: the initial stock level of the eric part_item
        ending_stock_level: the final stock level of the eric part_item

    Returns:
        moncli_item: resultant moncli item from calling board.create_item()
    """

    source_board = BOARD_MAPPING_DICT[eric_source_item.board_id]["name"]

    eric_source_item.log(f"Creating Movement Record From: {source_board}[{eric_source_item.name}]")

    if source_board == "stock_counts":
        eric_source_item.log("Stock Count Movement - Values will be assigned absolutely")
        url = f"https://icorrect.monday.com/boards/1008986497/pulses/{eric_source_item.mon_id}"
        text = f"Count: {eric_source_item.name}"
        mov_type = "Stock Count"
        mov_dir = "Stock Count"
    elif source_board == "main":
        eric_source_item.log("Device Repairs Movement - Values will be adjusted according to consumption")
        url = f"https://icorrect.monday.com/boards/349212843/pulses/{eric_source_item.mon_id}"
        text = f"Repair: {eric_source_item.name}"
        mov_type = "iCorrect Repairs"
        mov_dir = "Out"
    elif source_board == "parts":
        eric_source_item.log("Parts Movement - Values will be adjusted according to provided values (testing)")
        url = f"https://icorrect.monday.com/boards/985177480/pulses/{eric_source_item.mon_id}"
        text = f"Parts: {eric_source_item.name}"
        mov_type = "Parts Manipulation"
        mov_dir = "Parts Manipulation"
    elif source_board == "movements":
        eric_source_item.log("Void Request - Returning Part to Stock")
        url = f"https://icorrect.monday.com/boards/989490856/pulses/{eric_source_item.mon_id}"
        text = f"Movements: {eric_source_item.name}"
        mov_type = "Void"
        mov_dir = "Void"
    else:
        raise Exception(
            f"Movements Record Function Not Completed for Items from {eric_source_item.moncli_board_obj.name}")

    movement = BaseItem(eric_source_item.logger, board_id=989490856)  # Inventory Movements Board ID
    part_url = f"https://icorrect.monday.com/boards/985177480/pulses/{part_item.mon_id}"
    part_text = part_item.name

    movement.mov_type.value = mov_type
    movement.mov_dir.value = mov_dir
    movement.before.value = int(starting_stock_level)
    movement.after.value = int(ending_stock_level)
    movement.difference.value = int(ending_stock_level) - int(starting_stock_level)
    movement.source_id.value = eric_source_item.mon_id
    movement.source_url.value = [url, text]
    movement.parts_id.value = part_item.mon_id
    movement.parts_url.value = [part_url, part_text]
    try:
        movement.tags.replace(part_item.tags.labels)
    except exceptions.IndexOrIDConversionError:
        raise exceptions.TagsOnPartsNotAvailableOnMovements(part_item.tags.labels)

    new_item = movement.new_item(part_item.name)

    eric_source_item.log(f"{part_item.name}: Change ({int(ending_stock_level) - int(starting_stock_level)}) | New "
                         f"Stock Level: {ending_stock_level}")

    return new_item


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

    part_item.log(f"Checking Stock for {part_item.name} ({stock_level}) against Reorder({reorder_point})")

    if stock_level > reorder_point:
        part_item.log("Above Reorder")
        return "Above Reorder"
    elif stock_level <= reorder_point:
        part_item.log("Below Reorder")
        return "Below Reorder"
    else:
        raise Exception(
            f'Stock Level and Reorder Point are Mathematically Impossible ({stock_level} and {reorder_point})')


def _check_and_adjust_for_low_stock(part_item: BaseItem):
    """Performs a quick check to see if a part is below/above it's reorder point, and acts accordingly"""

    part_item.log(f"Checking Low Stock Status for {part_item.name}")

    if str(part_item.board_id) != "985177480":
        raise Exception(
            f"_check_and_adjust_for_low_stock provided with NON part item ({part_item.name} | {part_item.mon_id} | {part_item._mapper.eric_name})")

    # compare stock level with reorder point
    low_stock_status = part_item.low_stock_status.label
    part_item.log(low_stock_status)

    # check 'Low Stock' status to see if this is correct
    low_stock_level = _check_stock_against_reorder(part_item)

    if low_stock_level != low_stock_status:
        part_item.log(f"Adjusting to: {low_stock_level}")
        part_item.low_stock_status.label = low_stock_level

    # Do not need to commit item as it is always committed when adjusting stock level


def get_stock_info(mainboard_item: BaseItem):
    """returns a dictionary of repair items and some basic info"""

    mainboard_item.log(f"Getting Stock Info: {mainboard_item.name}: {mainboard_item.mon_id}")

    result = {}
    # get monday items
    for repair in get_repairs(mainboard_item):
        # build dict: {name: NAME, eric: ERIC ITEM, stock: STOCK LEVEL, stock_status: MONDAY LABEL}
        try:
            part_id = repair.connect_parts.value[0]

            part = BaseItem(mainboard_item.logger, part_id)

            result[repair.name] = {
                'repair': repair,
                'part': part,
                'stock_level': int(part.stock_level.value),
                'low_stock_status': part.low_stock_status.value,
            }
        except IndexError:
            mainboard_item.logger.log(f"Repair[{repair.name}] Has No Linked Part - Likely This Product Does Not Exist")
            mainboard_item.logger.soft_log()

    return result


def get_repairs(mainboard_item: BaseItem, create_if_not=False, generic=False):
    """"""

    mainboard_item.log(f"Getting Repairs for {mainboard_item.name}: {mainboard_item.mon_id}")

    # Create an eric item of the repairs board to search with
    repairs_search_item = BaseItem(mainboard_item.logger, board_id=984924063)

    repair_ids = []
    eric_repairs = []

    # Get search terms from device and repairs (and colour) columns
    if generic:
        search_terms = construct_search_terms_for_parts(mainboard_item, generic)
    else:
        search_terms = construct_search_terms_for_parts(mainboard_item)

    for item in search_terms:
        # Search using search item's relevant column search method
        found_ids = [item["id"] for item in repairs_search_item.combined_id.search(item)]

        # If no repairs found
        if not found_ids:
            # If create is selected, create the repair
            if create_if_not:
                eric_repairs.append(item)
            else:
                continue

        mainboard_item.log(f"Found IDS: {found_ids}")
        diff = list(set(found_ids) - set(repair_ids))
        mainboard_item.log(f"New IDs: {diff}")
        repair_ids.extend(diff)

    # Get eric parts
    for repair_id in repair_ids:
        eric_repairs.append(BaseItem(mainboard_item.logger, repair_id))

    return eric_repairs


def create_repair_item(logger, dropdown_ids: list, dropdown_names: list, device_type: str):
    if isinstance(logger, str):
        logger = application.CustomLogger()

    logger.log("Creating Repair Item")

    # Construct Combined ID & Name
    combined_id = "-".join([str(item) for item in dropdown_ids])
    dual_only = combined_id
    repair_name = " ".join(dropdown_names)

    logger.log(f"{repair_name} | Comb ID: {combined_id} | {device_type}")

    if len(dropdown_ids) > 2:
        dual_only = f"{dropdown_ids[0]}-{dropdown_ids[1]}"

    blank_item = BaseItem(logger, board_id=984924063)

    # Search Repairs Board to see if this combined ID already exists
    found_items = blank_item.combined_id.search(combined_id)
    if found_items:
        logger.log(f"Already found items with Combined ID: {combined_id}")
        for item in found_items:
            logger.log(f"{item.name} has Combined ID {combined_id}")
        logger.hard_log()

    # Set IDs
    blank_item.combined_id.value = combined_id
    blank_item.dual_id.value = dual_only
    blank_item.d_id.value = dropdown_ids[0]
    blank_item.r_id.value = dropdown_ids[1]
    try:
        blank_item.c_id.value = dropdown_ids[2]
    except IndexError:
        pass

    # Set Labels
    blank_item.d_label.value = dropdown_names[0]
    blank_item.r_label.value = dropdown_names[1]
    try:
        blank_item.c_label.value = dropdown_names[2]
    except IndexError:
        pass

    # Set Other
    blank_item.device_type.label = device_type

    # Commit
    blank_item.new_item(repair_name)


def _void_stock_change(logger, movementboard_reference):
    if isinstance(movementboard_reference, (str, int)):
        movement = BaseItem(logger, movementboard_reference)
    elif isinstance(movementboard_reference, BaseItem):
        movement = movementboard_reference
    else:
        raise Exception(f"void_stock_change requires a movement board item, got: {type(movementboard_reference)}")

    logger.log(f"Voiding Movement Entry")

    part = BaseItem(logger, movement.parts_id.value)
    diff = int(movement.difference.value)
    adjust_stock_level(logger, part, diff, movement)
    movement.void_status.label = "Voided"
    movement.commit()


def check_repairs_are_valid(logger, repairs: list):
    logger.log("Checking Repair Validity")

    for repair in repairs:
        if isinstance(repair, str):
            logger.log(f"Repair is string (has not been created yet): {repair}")
            continue
        logger.log(f"Checking {repair.name}[{repair.mon_id}]")
        if str(repair.moncli_obj.get_group('id')['id']) == "new_group89925":  # Does Not Exist Group ID
            logger.log("DOES NOT EXIST")
            raise exceptions.RepairDoesNotExist(repair)

    return True


def void_repairs_profile(financial_item):
    financial_item.logger.log(f"Voiding Finance Profile: {financial_item.name}")

    if not financial_item.moncli_obj.subitems:
        # nothing to void
        financial_item.logger.log("Nothing to Void")
        return True

    subitems = [BaseItem(financial_item.logger, item.id) for item in financial_item.moncli_obj.subitems]

    for item in subitems:
        if item.movement_id.value:
            financial_item.logger.log("Stock Movement Detected - Reversing")
            movement = BaseItem(financial_item.logger, item.movement_id.value)
            _void_stock_change(financial_item.logger, movement)
        item.moncli_obj.delete()

    financial_item.repair_profile.label = "Voided"
    financial_item.stock_adjust.label = "Voided"

    financial_item.commit()


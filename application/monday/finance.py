from rq import Queue

from worker import conn
import application
from .exceptions import ExternalDataImportError
from .inventory import adjust_stock_level

q_hi = Queue("high", connection=conn)


def checkout_stock_for_line_item(subitem_id, main_reference):
    if isinstance(main_reference, str):
        logger = application.CustomLogger()
        main = application.BaseItem(logger, main_reference)
    else:
        logger = main_reference.logger
        main = main_reference

    line = application.BaseItem(logger, subitem_id)

    logger.log(f"Checking Out Stock: {main.name} | {line.name}")

    part = application.BaseItem(logger, line.parts_id.value)

    consumption = line.quantity_used.value
    new_movement = adjust_stock_level(logger, part, consumption, main)
    line.sale_price.value = part.sale_price.value
    line.supply_price.value = part.supply_price.value
    line.parts_url.value = [
        f"https://icorrect.monday.com/boards/985177480/pulses/{part.mon_id}",
        f"{part.name}"
    ]
    line.movement_url.value = [
        f"https://icorrect.monday.com/boards/989490856/pulses/{new_movement.id}",
        f"{new_movement.name}"
    ]
    line.movement_id.value = new_movement.id

    if part.function.label == "Admin":
        line.eod_status.label = "Admin"

    logger.log("Line Checkout Complete")
    line.commit()


def mark_entry_as_complete(finance_reference):
    if isinstance(finance_reference, (str, int)):
        finance_item = application.BaseItem(application.CustomLogger(), finance_reference)

    else:
        finance_item = finance_reference

    finance_item.log("Checkout Complete")

    finance_item.stock_adjust.label = "Complete"

    finance_item.commit()


ZARA_SHORTCODES = {
    "ZARA": "zara.uk",
    "MASSIMO DUTTI": "zara.massimo",
    "PULL & BEAR": "zara.pb",
    "BERSHKA": "zara.bershka",
    "ZARA HOME": "zara.home",
    "STRADIVARIUS": "zara.strad",
    "PDAs": "zara.pda"
}


def import_account_specific_data(finance_item, external_item):
    board_name = external_item._mapper.eric_name

    finance_item.logger.log(f"Spinning up account specific actions for {board_name}")

    if board_name == "zara_ext":

        # move store and company information in from the zara board

        store = external_item.store.value
        company = external_item.company.label
        shortcode = ZARA_SHORTCODES[company]

        if not all([store, company, shortcode]):
            raise ExternalDataImportError(external_item, ["Store Code", "Company", "Invoicing Shortcode"])

        finance_item.shortcode.value = shortcode
        finance_item.store.value = store
        finance_item.sales_status.label = "Zara iPods"
        finance_item.commit()
        return True

    else:
        finance_item.log(f"No Account Specific Processes Defined for {board_name}")
        raise Exception(f"Need to define Account Specific Processes for {board_name}")
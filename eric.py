import os
import datetime
from functools import wraps

import rq

from moncli.api_v2.exceptions import MondayApiError

from application import BaseItem, clients, phonecheck, inventory, CannotFindReportThroughIMEI, accounting, \
    EricTicket, financial, CustomLogger, slack, blocks, xero_ex, mon_ex
from utils.tools import refurbs
from application.monday import config as mon_config
from worker import conn

q_hi = rq.Queue("high", connection=conn)


def log_catcher_decor(eric_function):
    @wraps(eric_function)
    def wrapper(webhook, test=None):
        logger = CustomLogger()
        # Attempt to execute the Eric function
        try:
            logger.func = str(eric_function.__name__)
            eric_function(webhook, logger, test)
            logger.commit("success")
        except MondayApiError as e:
            logger.log("============================ MONDAY SUBMISSION ERROR ==============================")
            for item in e.messages:
                logger.log(item)
            logger.summary = '\n'.join(e.messages)
            logger.commit("raised")
        except UserError as e:
            logger.log("User Error Encountered")
            logger.summary = e.summary
            logger.commit("user")
        except BaseException as e:
            logger.log(str(e))
            logger.summary = str(e)
            logger.commit("error")
    return wrapper


@log_catcher_decor
def process_stock_count(webhook, logger, test=None):
    logger.log('Process Stock Count Requested')

    # Get Stock Count Board (Needed for creating New Group and getting New Count Group)
    logger.log('Getting Count Board')
    count_board = clients.monday.system.get_boards('id', ids=[1008986497])[0]
    # Create Group for Processed Count
    logger.log('Creating Group')
    processed_group = count_board.add_group(f'Count | {datetime.datetime.today().strftime("%A %d %m %y")}')

    # Get Current Count Group
    logger.log('Getting Items')
    if test:
        mon_item = BaseItem(logger, test)
        new_count_group = count_board.get_groups('id', ids=[mon_item.group.id])[0]
    else:
        group_id = webhook['groupId']
        new_count_group = count_board.get_groups(ids=[group_id])[0]
    logger.log('Got Items')

    # Iterate Through Counted Items & Consolidate Results into dict of {Part ID: Total Quantities}
    count_totals = {}  # dict of Part ID against Eric Part Item, Expected Quantity and Counted Quantity

    # Consolidate results
    for item in new_count_group.items:

        count_item = BaseItem(logger, item.id)

        part_id = count_item.part_id.value
        count_num = count_item.count_num.value
        if count_num is None:
            count_num = 0

        if part_id not in count_totals:
            part_item = BaseItem(logger, part_id)
            count_totals[part_id] = {
                'count': count_item,
                'part': part_item,
                'expected': part_item.stock_level.value,
                'actual': count_num
            }
        else:
            count_totals[part_id]['actual'] += count_num
            count_item.moncli_obj.archive()

    # Adjust Part stock levels and Count Item Status & Group
    for result in count_totals:
        inventory.adjust_stock_level(
            logger=logger,
            part_reference=count_totals[result]['part'],
            quantity=count_totals[result]['actual'],
            source_object=count_totals[result]["count"],
            absolute=True
        )

        count_totals[result]['count'].count_status.label = 'Confirmed'
        count_totals[result]['count'].count_num.value = count_totals[result]['actual']
        count_totals[result]['count'].expected_num.value = count_totals[result]['expected']
        count_totals[result]['count'].moncli_obj.move_to_group(processed_group.id)
        count_totals[result]['count'].commit()

    logger.clear()
    return True


@log_catcher_decor
def fetch_pc_report(webhook, logger, test=None):
    if test:
        repair_item = BaseItem(logger, test)
    else:
        repair_item = BaseItem(logger, webhook['pulseId'])

    try:
        # Get Device info via IMEI
        logger.log(f'Fetching Phonecheck Report for IMEI: {repair_item.imeisn.value}')
        report_info = phonecheck.get_info(repair_item.imeisn.value)
    except CannotFindReportThroughIMEI:
        logger.log(f'No Phonecheck Report Found')
        repair_item.pc_reports_status.label = 'No Report Found'
        repair_item.commit()
        logger.hard_log()
        return ''

    #  Fetch the HTML Report for the check instance via report ID
    logger.log(f'Fetching HTML Report {report_info["A4Reports"]}')
    html_report = phonecheck.get_certificate(report_info['A4Reports'])

    # Converting to PDF
    path_to_pdf_report = phonecheck.new_convert_to_pdf(html_report, report_info['A4Reports'])

    # Add PDF File to Repair Item
    repair_item.pc_reports.files = f'tmp/pc_reports/report-{report_info["A4Reports"]}.pdf'

    # Delete the report file - helps clean local development dir clean
    os.remove(f'tmp/pc_reports/report-{report_info["A4Reports"]}.pdf')

    return True


@log_catcher_decor
def print_stock_info_for_mainboard(webhook, logger, test=None):
    logger.log("Checking Stock For MainBoard Item")

    if test:
        main_item = BaseItem(logger, test)
    else:
        main_item = BaseItem(logger, webhook["pulseId"])

    stock_info = inventory.get_stock_info(main_item)

    # Create Monday Friendly Update from Stock Info
    stock_list = []
    for item in stock_info:
        stock_list.append(f"{item}: {stock_info[item]['stock_level']}")
    stock_string = "\n".join(stock_list)
    update = f"""STOCK LEVELS\n\n{stock_string}"""

    try:
        update_info = main_item.moncli_obj.add_update(body=update)
        logger.log(f"Update Added: {update_info['body']}")
    except MondayApiError as e:
        logger.log("Monday API Error Occurred")
        logger.log(e.messages)
        logger.hard_log()

    logger.soft_log()

    return True


# noinspection PyTypeChecker
@log_catcher_decor
def create_enquiry_ticket(webhook, logger, test=None):
    def extract_enquiry_data(enquiry_item):

        # params to extract
        name = enquiry_item.name
        device_type = "Not Provided"
        model = "Not Provided"
        message = "Not Provided"

        try:
            value = enquiry_item.device_type.value
            if value:
                device_type = value
        except AttributeError:
            pass

        try:
            value = enquiry_item.model.value
            if value:
                model = value
        except AttributeError:
            pass

        try:
            value = enquiry_item.message.value
            if value:
                message = value
        except AttributeError:
            pass

        return [name, device_type, model, message]

    logger.log("Creating Panrix Enquiry Ticket")

    if test:
        item = BaseItem(logger, test)
    else:
        item = BaseItem(logger, webhook["pulseId"])

    # create eric ticket for panrix brand
    uncommitted_ticket = EricTicket(logger, None, new=item)
    uncommitted_ticket.zenpy_ticket.brand_id = 360004939497  # panrix brand ID

    enq_type = item.moncli_board_obj.name

    enq_data = extract_enquiry_data(item)

    # add enquiry message
    comment = \
        f"""Enquiry Type: {enq_type}
Client Name: {enq_data[0]}
Device: {enq_data[1]}
Model: {enq_data[2]}

Message: {enq_data[3]}
"""
    if enq_type == "Diagnostic Requests":
        turn_on_value = "Not Provided"
        exposed_to_liquid = "Not Provided"
        try:
            turn_on_value = item.turn_on_status.value
        except AttributeError:
            pass

        try:
            exposed_to_liquid = item.exposed_to_liquid.value
        except AttributeError:
            pass

        comment += f"\n\nDoes the device turn on?\n{turn_on_value}\n\nHas the device been exposed to liquid?\n{exposed_to_liquid}"

    uncommitted_ticket.add_comment(comment)
    new_zen_ticket = uncommitted_ticket.commit()

    # add other data & intro macro
    new_eric_ticket = EricTicket(logger, new_zen_ticket)
    macro_effect = clients.zendesk.tickets.show_macro_effect(new_eric_ticket.zenpy_ticket,
                                                             360128472418)  # New Panrix Enquiry Macro
    clients.zendesk.tickets.update(macro_effect.ticket)

    logger.soft_log()

    return True


@log_catcher_decor
def refurb_phones_initial_pc_report(webhook, logger, test=None):
    logger.log("Fetching Phonecheck Data for Refurb iPhones")

    if test:
        item = BaseItem(logger, test)
    else:
        item = BaseItem(logger, webhook["pulseId"])

    # Get info from phonecheck
    try:
        logger.log(f"Searching for IMEI[{item.imeisn.value}]")
        report_info = phonecheck.get_info(item.imeisn.value)
    except CannotFindReportThroughIMEI as e:
        # Cannot find report - IMEI entered incorrectly or device not checked
        item.pc_report_status_pre.label = "No Report Found"
        item.add_update(f"Cannot Find A Report for IMEI: {item.imeisn.value}. Check the IMEI number or make sure you "
                        f"have completed a phonecheck test run for this device.")
        logger.log("No report found")
        logger.hard_log()
        raise e

    # Sync Actual Condition Values (set by user when receiving) with Init and Working Values
    refurbs.sync_i_a_and_w_values(item)

    # Use Phonecheck Data to set required repairs
    summary = f"PHONECHECK REPORT DATA\nDate of Check: {report_info['DeviceUpdatedDate']}\n" \
              f"Target Grade: {item.target_grade.label}\n\n\fFace ID Condition: {item.a_face_id.label}\n\n===== FAILED =====\n"

    phonecheck.generate_and_store_pc_report(item.imeisn.value, item.pre_report)

    refurbs.sync_pc_to_status_values(item, report_info, summary)

    batt_health = report_info["BatteryHealthPercentage"]
    batt_cycles = report_info["BatteryCycle"]

    refurbs.process_battery_data(item, batt_health, initial=True)

    summary += f"\n===== BATTERY STATS =====\nHealth: {batt_health}\nCycles: {batt_cycles}"

    item.pc_report_status_pre.label = "Captured"
    item.report_summary.value = summary
    item.pc_report_id.value = report_info["A4Reports"]
    item.add_update(summary)
    item.commit()

    logger.soft_log()


@log_catcher_decor
def create_repairs_profile(webhook, logger, test=None):
    def add_financial_subitem(financial_item, repair_item):

        if isinstance(financial_item, (str, int)):
            financial_item = BaseItem(CustomLogger(), financial_item)
        if isinstance(repair_item, (str, int)):
            repair_item = BaseItem(CustomLogger(), repair_item)

        blank_subitem = BaseItem(financial_item.logger, board_id=989906488)

        blank_subitem.parts_id.value = repair_item.parts_id.value
        blank_subitem.quantity_used.value = 1
        if str(repair_item.parts_id.value) == '1112258883':  # No Parts Used Part ID TODO: Setup monday parts[Function] Column to control this automatically
            blank_subitem.eod_status.value = "Admin"

        financial_item.logger.log(f"Adding Subitem - {financial_item.name} | {repair_item.name}")

        financial_item.moncli_obj.create_subitem(
            item_name=repair_item.name,
            column_values=blank_subitem.staged_changes
        )

    logger.log("Creating Repairs Financial Profile")

    if test:
        finance = BaseItem(logger, test)
    else:
        finance = BaseItem(logger, webhook["pulseId"])

    # void processed subitems (if present)
    inventory.void_repairs_profile(finance)

    # Get Main Item
    main = BaseItem(logger, finance.main_id.value)

    # Check colour has been selected
    if main.device_colour.label in ["Not Selected", "PLEASE SELECT"] or not main.device_colour.label:
        main.add_update("No Colour Provided for this Device, please correct this -"
                        " Colourless devices would be incredibly difficult for people to use!")
        main.user_errors.label = "No Colour Given"
        raise UserError("No Colour Provided for this Device, please correct this -"
                        " Colourless devices would be incredibly difficult for people to use!")

    # Fetch Repairs and make sure there are some
    repairs = inventory.get_repairs(main, create_if_not=True)
    if len(repairs) == 0:
        finance.repairs_profile.label = "Failed"
        finance.add_update("Cannot Create Repairs Profile - No Repairs Supplied")
        main.user_errors.label = "No Repair Given"
        main.add_update("Cannot Checkout this repair as no repairs have been provided")
        main.commit()
        finance.commit()
        raise UserError("Cannot Create Repairs Profile - No Repairs Supplied")

    # Check Repairs Exist
    try:
        inventory.check_repairs_are_valid(logger, repairs)
    except mon_ex.RepairDoesNotExist as e:
        main.add_update("This Repair has been submitted but is impossible - please select the correct repair"
                        "It is likely that you have selected a Screen Manufacturer that is not compatible with your "
                        "device\n\n "
                        f"{e.error_message}")
        main.user_errors.label = "Does Not Exist"
        main.commit()
        finance.repair_profile.label = "Failed"
        finance.commit()
        finance.add_update(e.error_message)
        raise UserError(f"Impossible Repair Encounter: {e.repair.name}")

    # import external board data (if needed)
    if finance.external_board_id.value:
        external = BaseItem(logger, finance.external_board_id.value)
        try:
            financial.import_account_specific_data(finance, external)
        except mon_ex.ExternalDataImportError as e:
            finance.repair_profile.label = "Failed"
            finance.add_update(e.error_message)
            finance.commit()
            raise UserError(f"Data missing from External Board item: "
                            f"{external.moncli_board_obj.name}: {external.name} ({external.mon_id})")

    repair_profile = "Complete"
    stock_adjust = "Do Now!"

    for repair in repairs:
        if isinstance(repair, BaseItem):
            if repair.parts_id.value == "1112258883":  # No Parts Used Item ID
                logger.log("No Parts Used Detected - Switching to Manual Stock Checkout")
                stock_adjust = "Manual"
            # noinspection PyTypeChecker
            add_financial_subitem(finance, repair)
        elif isinstance(repair, str):
            logger.log("Repair Not Found - Beginning Creation Process and Setting Stock Checkout to Manual")
            stock_adjust = "Manual"
            repair_profile = "Failed - Creation"
            device_type = "Device"
            for option in mon_config.STANDARD_REPAIR_OPTIONS:
                if option in main.device.labels[0]:
                    device_type = option
            dropdown_ids = repair.split("-")
            if len(dropdown_ids) == 3:
                dropdown_labels = [
                    main.device.settings[str(dropdown_ids[0])],
                    main.repairs.settings[str(dropdown_ids[1])],
                    main.device_colour.settings[str(dropdown_ids[2])]
                ]
            else:
                dropdown_labels = [main.device.settings[str(dropdown_ids[0])],
                                   main.repairs.settings[str(dropdown_ids[1])]]

            if os.environ["ENV"] == 'devlocal':
                inventory.create_repair_item(
                    logger=logger,
                    dropdown_ids=dropdown_ids,
                    dropdown_names=dropdown_labels,
                    device_type=device_type
                )
            else:
                q_hi.enqueue(f=inventory.create_repair_item, args=("new", dropdown_ids, dropdown_labels, device_type))

    finance.repair_profile.label = repair_profile
    finance.stock_adjust.label = stock_adjust
    logger.log("Financial Profile Creation Complete")
    finance.commit()


@log_catcher_decor
def checkout_stock_profile(webhook, logger, test=None):
    if test:
        finance = BaseItem(logger, test)
    else:
        finance = BaseItem(logger, webhook["pulseId"])

    logger.log(f"Checking Out Stock: {finance.name}")

    if finance.repair_profile.label != "Complete":
        logger.log("Repair Profile Not Complete - Cancelling")
        raise UserError("Cannot Checkout Stock - No Repair Profile Created")
    try:
        for subitem in finance.moncli_obj.subitems:
            financial.checkout_stock_for_line_item(subitem.id, finance.main_id.value)
        financial.mark_entry_as_complete(finance)
    except mon_ex.TagsOnPartsNotAvailableOnMovements as e:
        logger.log(e.error_message)
        finance.repair_profile.label = 'Failed'
        finance.add_update("Please get Gabe to check Eric's Logs & Update the Tag Transfer from Parts to Movements")
        finance.commit()
        raise DataError(f"Tag Discrepancy Between Parts and Inventory Movements:\n{e.tags}")


@log_catcher_decor
def void_financial_profile(webhook, logger, test=None):
    if test:
        finance = BaseItem(logger, test)
    else:
        finance = BaseItem(logger, webhook["pulseId"])

    inventory.void_repairs_profile(finance)


@log_catcher_decor
def create_or_update_invoice(webhook, logger, test=None):
    if test:
        finance = BaseItem(logger, test)
    else:
        finance = BaseItem(logger, webhook["pulseId"])

    logger.log(f"Creating/Updating Invoice from Financial: {finance.name}")

    # Assemble Items
    subitems = [BaseItem(finance.logger, item.id) for item in finance.moncli_obj.subitems]
    main = BaseItem(logger, finance.main_id.value)
    ticket = None
    if main.zendesk_id.value:
        ticket = EricTicket(logger, main.zendesk_id.value)

    corp_search_item = BaseItem(logger, board_id=1973442389)  # Corporate Board ID
    if finance.shortcode.value:
        corp_items = corp_search_item.shortcode.search(finance.shortcode.value)
        if not corp_items:
            logger.log(f"CANNOT CREATE INVOICE: No Corporate Account Setup for {finance.name}")
            finance.invoice_generation.label = "Validation Error"
            finance.commit()
            raise UserError(f"CANNOT CREATE INVOICE: No Corporate Account Setup for {finance.name}")
    elif ticket and ticket.organisation:
        corp_items = corp_search_item.zendesk_org_id.search(ticket.organisation['id'])
    elif ticket and not ticket.organisation:
        logger.log(f"CANNOT CREATE INVOICE: Ticket[{ticket.id}] used to process invoice, "
                   f"but User[{ticket.user['name']}] is not part of an organisation")
        finance.invoice_generation.label = "Validation Error"
        finance.commit()
        raise UserError(f"CANNOT CREATE INVOICE: Ticket[{ticket.id}] used to process invoice, "
                   f"but User[{ticket.user['name']}] is not part of an organisation")
    else:
        logger.log("CANNOT CREATE INVOICE: No Ticket Associated with Financial Item, and no Shortcode Provided")
        finance.invoice_generation.label = "Validation Error"
        finance.commit()
        raise UserError("CANNOT CREATE INVOICE: No Ticket Associated with Financial Item, and no Shortcode Provided")

    if len(corp_items) > 1:
        accs = '\n'.join([f"{item.name}:{item.id}" for item in corp_items])
        logger.log(f"CANNOT CREATE INVOICE: Too Many Corporate Accounts Found\n\n{accs}")
        finance.invoice_generation.label = "Validation Error"
        finance.commit()
        raise UserError(f"CANNOT CREATE INVOICE: Too Many Corporate Accounts Found\n\n{accs}")
    elif not corp_items:
        logger.log(f"CANNOT CREATE INVOICE: No Corporate Account Setup for {finance.name}")
        finance.invoice_generation.label = "Validation Error"
        finance.commit()
        raise UserError(f"CANNOT CREATE INVOICE: No Corporate Account Setup for {finance.name}")
    else:
        corporate = BaseItem(logger, corp_items[0].id)

    # Check financial Item validity against corporate item
    try:
        results = accounting.check_financial_against_requirements(corporate, finance)
    except xero_ex.FinancialAndCorporateItemIncompatible as e:
        finance.add_update(e.corp_requirements)
        finance.invoice_generation.label = "Validation Error"
        finance.add_update(f"Financial Item[{finance.name}] Does not Match Requirements from Corp Item[{corporate.name}]")
        finance.commit()
        raise UserError(f"Financial Item[{finance.name}] Does not Match Requirements from Corp Item[{corporate.name}]")

    # Construct Line Data from Items
    repair_line_data = accounting.construct_repair_line_item(finance, subitems, main, ticket, corporate)
    courier_line_data = accounting.construct_courier_line_item(main, corporate, finance)
    line_items = [item for item in [repair_line_data, courier_line_data] if item]

    # Calculate Courier Service Type & Level
    if corporate.payment_method.label == "Business (Xero) Invoice":
        if corporate.payment_terms.label == "Monthly Payments":
            # Get invoice and update
            invoice_search = accounting.get_invoice(corporate.invoice_id.value)["Invoices"]
            if len(invoice_search) == 1:
                inv = invoice_search[0]
                assert inv["Status"] == "DRAFT"
                inv["LineItems"] += line_items
                inv = accounting.update_invoice(inv)
                finance.invoice_generation.label = "Complete"
                finance.invoice_number.value = inv["InvoiceNumber"]
            else:
                finance.invoice_generation.label = "Get Invoice Error"
                finance.add_update(
                    f"Too Many Invoices Found When Searching: {corporate.invoice_id.value} | {corporate.name}")
                finance.commit()
                raise DataError(f"Too Many Invoices Found When Searching: {corporate.invoice_id.value} | {corporate.name}")

        elif corporate.payment_terms.label == "Pay Per Repair":
            # Create one-off invoice
            inv = accounting.create_invoice(corporate, finance, line_items)
            finance.invoice_generation.label = "Complete"
            finance.invoice_number.value = inv["InvoiceNumber"]
        else:
            finance.invoice_generation.label = "Failed"
            finance.add_update(
                f"Corporate Item Has Unacceptable Label for 'Payment Terms': {corporate.payment_terms.label} | {corporate.name}")
            finance.commit()
            raise UserError(f"Corporate Item Has Unacceptable Label for 'Payment Terms': {corporate.payment_terms.label} | {corporate.name}")

    elif corporate.payment_method.label == "Card Payment (In Person)":
        finance.add_update(
            f"Corporate Item Has Unacceptable Label for 'Payment Terms': {corporate.payment_terms.label} | {corporate.name}")
        finance.invoice_generation.label = "Failed"
        finance.commit()
        raise UserError(f"Corporate Item Has Unacceptable Label for 'Payment Terms': {corporate.payment_terms.label} | {corporate.name}")

    elif corporate.payment_method.label == "Consumer (Sumup) Invoice":
        finance.add_update(
            f"Corporate Item Expects a Sumup Invoice: {corporate.payment_terms.label} | {corporate.name}")
        finance.invoice_generation.label = "Failed"
        finance.commit()
        raise UserError(f"Corporate Item Expects a Sumup Invoice: {corporate.payment_terms.label} | {corporate.name}")

    else:
        finance.add_update(
            f"Corporate Item Has Unacceptable Label for 'Payment Method': {corporate.payment_terms.label} | {corporate.name}")
        finance.invoice_generation.label = "Failed"
        finance.commit()
        raise UserError(f"Corporate Item Has Unacceptable Label for 'Payment Method': {corporate.payment_terms.label} | {corporate.name}")

    finance.commit()


@log_catcher_decor
def create_monthly_invoice(webhook, logger, test=None):
    if test:
        corporate = BaseItem(logger, test)
    else:
        corporate = BaseItem(logger, webhook["pulseId"])

    logger.log(f"Creating Invoice (Monthly) From Corporates: {corporate.name}")

    inv = accounting.create_invoice(corporate, None, monthly=True)

    corporate.invoice_id.value = inv["InvoiceID"]
    corporate.create_invoice.label = "Complete"
    corporate.invoice_link.value = [
        f"https://invoicing.xero.com/edit/{inv['InvoiceID']}",
        inv["InvoiceNumber"]
    ]

    corporate.commit()


@log_catcher_decor
def check_and_notify_for_stock(webhook, logger, test=None):
    if test:
        main = BaseItem(logger, test)
    else:
        main = BaseItem(logger, webhook["pulseId"])

    repairs = inventory.get_repairs(main)

    for repair in repairs:
        # Check stock level
        # Check whether item can be refurbed
        # Commission Refurb or Notify CS to Delay Client
        if int(repair.stock_level.value) < 1:  # Checking against 1 (not 0) to be safe

            if repair.refurb_poss.value == 'On Refurb':  # Part can be refurbed - notify Refurb Dept.
                pass
            else:  # Part cannot be refurbed - Notify CS
                pass

        else:  # Part in Stock - Proceed with Booking
            pass


class EricLevelException(Exception):

    def __init__(self):
        pass


class UserError(Exception):

    def __init__(self, summary="User Error: Not Supplied"):
        self.summary = summary


class DataError(Exception):

    def __init__(self, summary="Data Error: Not supplied"):
        self.summary = summary


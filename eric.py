import os
import datetime

from moncli.api_v2.exceptions import MondayApiError

from application import BaseItem, clients, CustomLogger, phonecheck, inventory, CannotFindReportThroughIMEI, accounting, \
    EricTicket


def process_stock_count(webhook, test=None):
    logger = CustomLogger()
    logger.log('Process Stock Count Requested')

    # Get Stock Count Board (Needed for creating New Group and getting New Count Group)
    logger.log('Getting Count Board')
    count_board = clients.monday.system.get_boards('id', ids=[1008986497])[0]
    # Create Group for Processed Count
    logger.log('Creating Group')
    processed_group = count_board.add_group(f'Count | {datetime.datetime.today().strftime("%A %d %m %y")}')

    try:
        # Get Current Count Group
        logger.log('Getting Items')
        if test:
            item = clients.monday.system.get_items(test)[0]
            new_count_group = count_board.get_groups('id', ids=[item.group.id])[0]
        else:
            group_id = webhook['groupId']
            new_count_group = count_board.get_groups(ids=[group_id])[0]
        logger.log('Got Items')
    except Exception as e:
        logger.log('Monday API Error Occurred')
        # messages = "/n".join(e.messages)
        # logger.log(f'MESSAGES:\n\n{messages}')
        logger.hard_log()
        return False

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
        inventory.adjust_stock_level(logger, count_totals[result]['part'], count_totals[result]['actual'],
                                     absolute=True)

        count_totals[result]['count'].count_status.label = 'Confirmed'
        count_totals[result]['count'].count_num.value = count_totals[result]['actual']
        count_totals[result]['count'].expected_num.value = count_totals[result]['expected']
        count_totals[result]['count'].moncli_obj.move_to_group(processed_group.id)
        count_totals[result]['count'].commit()

    logger.clear()
    return True


def fetch_pc_report(webhook, test=None):
    logger = CustomLogger()

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
    except Exception as e:
        logger.log('phonecheck get info by IMEI failed with an unknown error')
        logger.log(f'Raised Exception: {e}')
        logger.hard_log()
        return ''

    try:
        #  Fetch the HTML Report for the check instance via report ID
        logger.log(f'Fetching HTML Report {report_info["A4Reports"]}')
        html_report = phonecheck.get_certificate(report_info['A4Reports'])
    except Exception as e:
        # Unknown Error
        logger.log('An Unknown Error Occurred while fetching the HTML Report')
        logger.log(f'Raised Exception: {e}')
        repair_item.pc_reports_status.label = 'Error'
        repair_item.commit()
        logger.hard_log()
        return ''

    try:
        # Converting to PDF
        path_to_pdf_report = phonecheck.new_convert_to_pdf(html_report, report_info['A4Reports'])
    except Exception as e:
        # Unknown Error - This is a very volatile function currently
        logger.log('An Unknown Error Occurred while converting to PDF')
        logger.log(f'Raised Exception: {e}')
        repair_item.pc_reports_status.label = 'Error'
        repair_item.commit()
        logger.hard_log()
        return ''

    try:
        # Add PDF File to Repair Item
        repair_item.pc_reports.files = f'tmp/pc_reports/report-{report_info["A4Reports"]}.pdf'

    except Exception as e:
        logger.log('An Unknown Error Occurred while converting to PDF')
        logger.log(f'Raised Exception: {e}')
        repair_item.pc_reports_status.label = 'Error'
        repair_item.commit()
        logger.hard_log()

    # Delete the report file - helps clean local development dir clean
    os.remove(f'tmp/pc_reports/report-{report_info["A4Reports"]}.pdf')

    logger.clear()

    return True


def print_stock_info_for_mainboard(webhook, test=None):
    logger = CustomLogger()
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

    logger.clear()

    return True


# noinspection PyTypeChecker
def create_enquiry_ticket(webhook, test=None):
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

    logger = CustomLogger()
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
    macro_effect = clients.zendesk.tickets.show_macro_effect(new_eric_ticket.zenpy_ticket, 360128472418)  # New Panrix Enquiry Macro
    clients.zendesk.tickets.update(macro_effect.ticket)

    logger.clear()

    return True

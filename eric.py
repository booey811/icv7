import os
import datetime

from application import BaseItem, clients, CustomLogger, phonecheck, inventory, CannotFindReportThroughIMEI


def process_stock_count(webhook, test=None):

    logger = CustomLogger()

    # Get Stock Count Board (Needed for creating New Group and getting New Count Group)
    count_board = clients.monday.system.get_boards('id', ids=[1008986497])[0]
    # Create Group for Processed Count
    processed_group = count_board.add_group(f'Count | {datetime.datetime.today().strftime("%A %d %m %y")}')

    # Get Current Count Group
    if test:
        item = clients.monday.system.get_items(test)[0]
        new_count_group = count_board.get_groups('id', ids=[item.group.id])[0]
    else:
        group_id = webhook['groupId']
        print(group_id)
        new_count_group = count_board.get_groups(ids=[group_id])[0]

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
        inventory.adjust_stock_level(logger, count_totals[result]['part'], count_totals[result]['actual'])

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

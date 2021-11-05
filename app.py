import datetime
import os
import json

import flask

from icv7 import create_app, clients, BaseItem, CustomLogger, phonecheck, inventory

from icv7.phonecheck.pc import CannotFindReportThroughIMEI

# App Creation
app = create_app()


# App functions
def verify_monday(webhook):
    """Takes webhook information, authenticates if required, and decodes information
    Args:
        webhook (request): Payload received from Monday's Webhooks
    Returns:
        dictionary: contains various information from Monday, dependent on type of webhook sent
    """
    data = webhook.decode('utf-8')
    data = json.loads(data)
    if "challenge" in data.keys():
        authtoken = {"challenge": data["challenge"]}
        return authtoken
    else:
        return data


# Routes
# Index/Home
@app.route('/', methods=['GET'])
def index():
    print('Hello World')
    return 'Hello Returns'


# Process Stock Count
@app.route('/monday/stock/process-count', methods=['POST'])
def process_stock_count(test_id=None):
    # Check for whether monday auth is needed or the function is being run under a test
    if not test_id:
        webhook = flask.request.get_data()
        data = verify_monday(webhook)
        if len(data) == 1:
            return data
        else:
            data = data['event']
    else:
        data = test_id

    logger = CustomLogger()

    # Get Stock Count Board (Needed for creating New Group and getting New Count Group)
    count_board = clients.monday.system.get_boards('id', ids=[1008986497])[0]
    # Get Current Count Group
    new_count_group = count_board.get_groups('id', ids=['new_group26476'])[0]
    # Create Group for Processed Count
    processed_group = count_board.add_group(f'Count | {datetime.datetime.today()}')

    # Iterate Through Counted Items & Consolidate Results into dict of {Part ID: Total Quantities}
    count_totals = {}  # dict of Part ID against Eric Part Item, Expected Quantity and Counted Quantity
    count_items = {}  # For use later, to adjust status and group position

    # Consolidate results
    for item in new_count_group.items:

        count_item = BaseItem(logger, item.id)

        part_id = count_item.part_id.value
        count_num = count_item.count_num.value

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

    # Adjust Part stock levels and Count Item Status & Group
    for result in count_totals:

        inventory.adjust_stock_level(logger, count_totals[result]['part'], count_totals[result]['actual'])

        count_totals[result]['count'].count_status.label = 'Confirmed'
        count_totals[result]['count'].expected_num.value = count_totals[result]['expected']
        count_totals[result]['count'].moncli_obj.move_to_group(processed_group.id)
        count_totals[result]['count'].commit()


# Get Phonecheck Report and Add to Monday
@app.route('/monday/repairers/get-pc-report', methods=['POST'])
def repairers_pc_report_fetch(test_id=None):
    # Check for whether monday auth is needed or the function is being run under a test
    if not test_id:
        webhook = flask.request.get_data()
        data = verify_monday(webhook)
        if len(data) == 1:
            return data
        else:
            data = data['event']
    else:
        data = test_id

    logger = CustomLogger()
    repair_item = BaseItem(logger, data)

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
        path_to_pdf_report = phonecheck.convert_to_pdf(html_report, report_info['A4Reports'])
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
        repair_item.pc_reports.files = f'tmp/ph_chk_reports/report-{report_info["A4Reports"]}.pdf'

    except Exception as e:
        logger.log('An Unknown Error Occurred while converting to PDF')
        logger.log(f'Raised Exception: {e}')
        repair_item.pc_reports_status.label = 'Error'
        repair_item.commit()
        logger.hard_log()

    # Delete the report file - helps clean local development dir clean
    os.remove(f'tmp/ph_chk_reports/report-{report_info["A4Reports"]}.pdf')

    logger.clear()
    return ''


if __name__ == '__main__' and os.environ['ENV'] != 'devlocal':
    # App Entry Point
    app.run()
else:
    # App Testing
    print('Testing App.py')
    base_log = CustomLogger()
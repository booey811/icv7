import os
import json

import flask

from icv7 import create_app, clients, BaseItem, CustomLogger, phonecheck

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
    repairers_pc_report_fetch(1801613065)

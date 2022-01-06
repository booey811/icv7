import datetime
import os
import json

import flask
from rq import Queue
from worker import conn

from application import create_app, verify_monday, ChallengeReceived
import eric

# App Creation
app = create_app()

q_lo = Queue("low", connection=conn, default_timeout=3600)
q_def = Queue("default", connection=conn)
q_hi = Queue("high", connection=conn)


# Routes
# Index/Home
@app.route('/', methods=['GET'])
def index():
    print('Hello World')
    return 'Hello Returns'


# Process Stock Count
@app.route('/monday/stock/process-count', methods=['POST'])
def process_stock_count(test_id=None):
    # Check for whether monday auth is needed or the function is being run under a test, instantiate logger
    webhook = flask.request.get_data()
    try:
        data = verify_monday(webhook)['event']
    except ChallengeReceived as e:
        return e.token

    if os.environ['ENV'] == 'devlocal':
        if not test_id:
            raise Exception('test_id is required when testing locally')
        eric.process_stock_count(None, test_id)
    elif os.environ['ENV'] in ['devserver', 'production']:
        result = q_lo.enqueue(eric.process_stock_count, data)
    else:
        raise Exception(f'Unknown ENV: {os.environ["ENV"]}')

    return ''


# Get Phonecheck Report and Add to Monday
@app.route('/monday/repairers/get-pc-report', methods=['POST'])
def repairers_pc_report_fetch(test_id=None):
    # Check for whether monday auth is needed or the function is being run under a test, instantiate logger
    webhook = flask.request.get_data()
    try:
        data = verify_monday(webhook)['event']
    except ChallengeReceived as e:
        return e.token

    if os.environ['ENV'] == 'devlocal':
        if not test_id:
            raise Exception('test_id is required when testing locally')
        eric.fetch_pc_report(None, test_id)
    elif os.environ['ENV'] in ['devserver', 'production']:
        result = q_hi.enqueue(eric.fetch_pc_report, data)
    else:
        raise Exception(f'Unknown ENV: {os.environ["ENV"]}')

    return ''


# Check Stock for a repair and print to the Main Board Item
@app.route("/monday/main/check-stock", methods=["POST"])
def check_stock_for_mainboard_item(test_id=None):
    webhook = flask.request.get_data()
    try:
        data = verify_monday(webhook)['event']
    except ChallengeReceived as e:
        return e.token

    if os.environ['ENV'] == 'devlocal':
        if not test_id:
            raise Exception('test_id is required when testing locally')
        eric.print_stock_info_for_mainboard(None, test_id)
    elif os.environ['ENV'] in ['devserver', 'production']:
        result = q_hi.enqueue(eric.print_stock_info_for_mainboard, data)
    else:
        raise Exception(f'Unknown ENV: {os.environ["ENV"]}')

    return ''


# Create a Zendesk Ticket for New Enquiries
@app.route("/monday/enquiries/new-enquiry", methods=["POST"])
def create_zendesk_ticket_for_enquiry(test_id=None):
    webhook = flask.request.get_data()
    try:
        data = verify_monday(webhook)['event']
    except ChallengeReceived as e:
        return e.token

    if os.environ['ENV'] == 'devlocal':
        if not test_id:
            raise Exception('test_id is required when testing locally')
        eric.create_enquiry_ticket(None, test_id)
    elif os.environ['ENV'] in ['devserver', 'production']:
        result = q_def.enqueue(eric.create_enquiry_ticket, data)
    else:
        raise Exception(f'Unknown ENV: {os.environ["ENV"]}')

    return ''


if __name__ == '__main__':
    app.run()

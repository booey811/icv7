import logging
import os
import json

import flask

from worker import q_lo, q_def, q_hi

from application import create_app, verify_monday, ChallengeReceived
import eric
from utils import exec as utils_exec
from slack_factory import create_slack_app

# Setup
logging.basicConfig(level=logging.DEBUG)


# ===================================== SLACK APP =====================================
# Slack App in Socket Mode, or not if SLACK is OFF
slacker = create_slack_app()

# ===================================== ERIC APP =====================================

# Eric/Flask App Creation
app = create_app()


# Index/Home
@app.route('/', methods=['GET'])
def index():
	return 'Index Route'


@app.route("/monday/repair-events", methods=["POST"])
def process_repair_event(test_id=None):
	webhook = flask.request.get_data()
	try:
		data = verify_monday(webhook)['event']
	except ChallengeReceived as e:
		return e.token

	if os.environ['ENV'] == 'devlocal':
		if not test_id:
			raise Exception('test_id is required when testing locally')
		eric.handle_repair_events(None, test_id)
	else:
		q_hi.enqueue(
			eric.handle_repair_events,
			data
		)
	return ''


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


# Repair Profile Generation
@app.route("/monday/financial/create_profile", methods=["POST"])
def create_repairs_profile(test_id=None):
	webhook = flask.request.get_data()
	try:
		data = verify_monday(webhook)['event']
	except ChallengeReceived as e:
		return e.token

	if os.environ['ENV'] == 'devlocal':
		if not test_id:
			raise Exception('test_id is required when testing locally')
		eric.create_repairs_profile(None, test_id)
	elif os.environ['ENV'] in ['devserver', 'production']:
		result = q_hi.enqueue(eric.create_repairs_profile, data)
	else:
		raise Exception(f'Unknown ENV: {os.environ["ENV"]}')

	return ''


# Repair Profile Stock Checkouts
@app.route("/monday/financial/checkout_stock_profile", methods=["POST"])
def checkout_stock_profile(test_id=None):
	webhook = flask.request.get_data()
	try:
		data = verify_monday(webhook)['event']
	except ChallengeReceived as e:
		return e.token

	if os.environ['ENV'] == 'devlocal':
		if not test_id:
			raise Exception('test_id is required when testing locally')
		eric.checkout_stock_profile(None, test_id)
	elif os.environ['ENV'] in ['devserver', 'production']:
		result = q_hi.enqueue(eric.checkout_stock_profile, data)
	else:
		raise Exception(f'Unknown ENV: {os.environ["ENV"]}')

	return ''


# Add the Appropriate Repair to The Appropriate Invoice
@app.route("/monday/financial/create_or_update_invoice", methods=["POST"])
def create_or_update_invoice(test_id=None):
	webhook = flask.request.get_data()
	try:
		data = verify_monday(webhook)['event']
	except ChallengeReceived as e:
		return e.token

	if os.environ['ENV'] == 'devlocal':
		if not test_id:
			raise Exception('test_id is required when testing locally')
		eric.create_or_update_invoice(None, test_id)
	elif os.environ['ENV'] in ['devserver', 'production']:
		result = q_hi.enqueue(eric.create_or_update_invoice, data)
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


# Generate Rolling Monthly Invoice
@app.route("/monday/corporate/create_monthly_invoice", methods=["POST"])
def create_monthly_invoice(test_id=None):
	webhook = flask.request.get_data()
	try:
		data = verify_monday(webhook)['event']
	except ChallengeReceived as e:
		return e.token

	if os.environ['ENV'] == 'devlocal':
		if not test_id:
			raise Exception('test_id is required when testing locally')
		eric.create_monthly_invoice(None, test_id)
	elif os.environ['ENV'] in ['devserver', 'production']:
		result = q_hi.enqueue(eric.create_monthly_invoice, data)
	else:
		raise Exception(f'Unknown ENV: {os.environ["ENV"]}')

	return ''


# Generate Set of Repairs for Given model on Product Creator Item (Main Board)
@app.route("/executables/generate_repair_set", methods=["PUT"])
def generate_repair_set(test_id=None):
	result = q_lo.enqueue(utils_exec.generate_repair_set)
	return ''


# Get & process Phonecheck Data for rrefurb phones
@app.route("/monday/refurbs/pc_report_pre", methods=["POST"])
def refurb_phones_initial_pc_report(test_id=None):
	webhook = flask.request.get_data()
	try:
		data = verify_monday(webhook)['event']
	except ChallengeReceived as e:
		return e.token

	if os.environ['ENV'] == 'devlocal':
		if not test_id:
			raise Exception('test_id is required when testing locally')
		eric.refurb_phones_initial_pc_report(None, test_id)
	elif os.environ['ENV'] in ['devserver', 'production']:
		result = q_def.enqueue(eric.refurb_phones_initial_pc_report, data)
	else:
		raise Exception(f'Unknown ENV: {os.environ["ENV"]}')

	return ''


# Slack Callback URL
@app.route("/slack/cb811slack/cb811", methods=["POST", "GET"])
def slack_callbacks(test_id=None):
	from pprint import pprint as p
	from urllib.parse import parse_qs

	webhook_dec = flask.request.get_data().decode('utf-8')

	webhook_human = parse_qs(webhook_dec)['payload']

	webhook_dct = json.loads(webhook_human[0])

	p(webhook_dct)

	info = webhook_dct['events']['body']['payload']

	p(info)

	p(json.loads(info))
	return ''


@app.route("/api/generate_products", methods=["POST"])
def generate_products_from_product_generator():
	q_hi.enqueue(
		f=utils_exec.generate_repair_set
	)

	return ""


if __name__ == '__main__':
	app.run()

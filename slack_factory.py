import os
import time

import eric
from pprint import pprint as p

from slack_bolt import App
from slack_bolt.error import BoltError
from slack_bolt.adapter.socket_mode import SocketModeHandler
import flask


def create_slack_app():
	if os.environ['SLACK'] == "OFF":
		app = flask.Flask('fake_slack')
		_add_routing(app)
	elif os.environ['SLACK'] == "ON":
		if os.environ["ENV"] == 'devlocal':
			print("CONNECTING TO SLACK/DEV")
			bot_token = os.environ["SLACK_DEV_BOT_TOKEN"]
			app_token = os.environ["SLACK_DEV_APP_TOKEN"]
		else:
			bot_token = os.environ["SLACK_BOT_TOKEN"]
			app_token = os.environ["SLACK_APP_TOKEN"]

		app = App(token=bot_token)
		_add_routing(app)
		handler = SocketModeHandler(app, app_token)
		handler.connect()
	else:
		raise Exception("Slack App initialised with incorrect SLACK env var")

	return app


def loader(footnotes=''):
	"""returns the view for the modal screen showing that the application has received a request and is processing it
	adds in a footnote to the loading screen for more specific information"""

	blocks = [{
				"type": "header",
				"text": {
					"type": "plain_text",
					"text": "Please wait... Eric is thinking big thoughts",
					"emoji": True
				}
			}]

	if footnotes:
		context = {
			"type": "context",
			"elements": [
				{
					"type": "mrkdwn",
					"text": footnotes
				}
			]
		}
		blocks.append(context)

	view = {
		"type": "modal",
		"title": {
			"type": "plain_text",
			"text": "Creating User"
		},
		"blocks": blocks
	}
	return view


def _add_routing(app):
	if os.environ["SLACK"] == "ON":

		# =========== Commands

		@app.command("/test")
		def run_test_action(ack, body, logger, client, say):
			ack(
				text="TEST LOAD SCREEN",
				blocks=loader("TESTER")
			)

			time.sleep(2)

			eric.test_route(body, client)

		@app.command("/devrepair")
		def begin_slack_repair_process(ack, body, logger, client):
			"""
			occurs when user types /devrepair
			pushes a loading view while fetching the repair at the top of the users monday group
			updates view to pre-repair overview showing deadlines and model details and a button to begin the repair,
			which triggers on view submission
			view submission = pre_repair_info
			"""
			logger.info("Repair process request received")
			ack()
			eric.begin_slack_repair_process(body, client)
			return True

		@app.command("/users")
		def begin_user_search(ack, body, logger, client):
			"""
			pops open a search input box that sends a request on search
			pushes a new view with results
			Args:
				ack:
				body:
				logger:
				client:

			Returns:

			"""

			logger.info("User Search Begin request received")
			ack()
			eric.slack_user_search_init(body, client)

		@app.command("/bookings")
		def show_todays_repairs(ack, body, logger, client):
			logger.info("Showing todays repairs")
			ack()

			eric.show_todays_repairs_group(body, client)

		@app.command("/devbookings")
		def show_dev_group_repairs(ack, body, logger, client):
			logger.info("Showing dev repairs")
			ack()
			eric.show_todays_repairs_group(body, client, dev=True)

		@app.command("/stock")
		def check_stock_levels(ack, body, logger, client):
			logger.info("Beginning Stock Check Flow")
			ack()
			eric.check_stock(body, client)

		# =========== Action Block Submissions
		# Working Theory: Should be responded to with 'Push'

		# Stock Checking Routes

		@app.action("stock_device_type")
		def check_stock_device_type_entry(ack, body, logger, client):
			logger.info("Checking stock after device selection")
			ack()
			eric.check_stock(body, client)

		@app.action("select_stock_device")
		def check_stock_device_entry(ack, body, logger, client):
			logger.info("Checking stock after repair selection")
			ack()
			eric.check_stock(body, client)

		@app.action("select_stock_repair")
		def check_stock_repair_entry(ack, body, logger, client):
			logger.info("Checking stock after repair selection")
			ack()
			eric.check_stock(body, client, get_level=True)

		# Other Action Routes

		@app.action("DEPRECATED1")
		def create_new_walkin_repair(ack, body, logger, client):
			logger.info("Request received to book in new repair")
			ack()

			eric.new_walkin_repair(body, client)

		@app.action("user_search")
		def user_search_results(ack, body, logger, client):
			logger.info("Searching Zendesk for User Input")
			ack({"response_action": "clear"})

			eric.slack_user_search_results(body, client)

		@app.action("button_new_user")
		def get_new_user_input(ack, body, logger, client):
			logger.info("New User Request Received - Providing Inputs")
			ack()

			eric.show_new_user_form(body, client)

		@app.action("new_walkin_repair")
		def accept_walkin_from_user_select(ack, body, logger, client):
			logger.info("New Walk-In Request from User Select Menu")
			p("-================================= CAUGHT")
			ack()

			eric.show_walk_in_info(body, client, from_search=True)

		@app.action("select_booking")
		def begin_walk_in_receipt(ack, body, logger, client):
			logger.info('Beginning walk in acceptance process')
			ack()

			eric.show_walk_in_info(body, client, from_booking=True)

		@app.action("end_repair_phase")
		def end_repair_phase(ack, body, logger, client):
			logger.info("Response to Repair Phase Complete")
			ack()

			selected = None
			for action in body['actions']:
				if action['action_id'] == 'end_repair_phase':
					selected = action['selected_option']['value']

			if not selected:
				raise Exception(
					f"Unexpected Action ID in 'actions' object after end_repair_phase, could not find: 'end_repair_phase'")

			if selected == 'repaired':
				eric.begin_parts_search(body, client)
			elif selected == 'client':
				eric.handle_other_repair_issue(body, client)
			elif selected == 'parts':
				eric.cannot_complete_repair_no_parts(body, client)
			elif selected == 'urgent':
				eric.handle_urgent_repair(body, client)
			elif selected == 'other':
				eric.handle_other_repair_issue(body, client)
			else:
				raise Exception(f"Unexpected Value from Static Select Actions End Repair Phase: {selected}")

		@app.action('repair_search')
		def search_and_show_repairs(ack, body, logger, client):

			logger.info("Searching for repairs (first time)")
			ack()

			eric.display_repairs_search_results(body, client)

		@app.action("select_part")
		def add_part_to_repair(ack, body, logger, client):
			logger.info("Adding Part to Repair")
			ack()

			eric.continue_parts_search(body, client)

		@app.action('waste_opt_in')
		def register_waste_entry(ack, body, logger, client):
			logger.info("Waste Entry process request")
			ack()

			selected = None
			for action in body['actions']:
				if action['action_id'] == 'waste_opt_in':
					selected = action['selected_option']['value']

			if not selected:
				raise Exception("Unexpexcted Action ID in 'actions' object after repair_complete")

			print("SELECTED ========================")
			print(selected)

			if selected == 'yes':
				# Waste recording flow
				eric.process_waste_entry(body, client)
			elif selected == 'no':
				# Do Nothing
				pass
			else:
				raise Exception("Unexpected value received in action for waste_opt_in")

		@app.action("parts_selection")
		def validate_repair_selection(ack, body, logger, client):
			logger.info("Parts Validation/Selection process request")
			ack()

		# =========== View Submissions

		@app.view("pre_repair_info")
		def begin_specific_slack_repair(ack, body, logger, client):
			logger.info("Response to Repair Beginning Received")
			ack()
			eric.begin_specific_slack_repair(body, client)
			return True

		@app.view("new_user_input")
		def add_new_user(ack, body, logger, client):
			logger.info("New User Inputs Received, Adding User")

			eric.check_and_create_new_user(body, client, ack)

		@app.view("accept_walkin_repair")
		def accept_walkin_repair_data(ack, body, logger, client):
			logger.info("Walk In Repair Accepted - Processing")
			ack()
			eric.accept_walkin_repair_data(ack, body, logger, client)


	elif os.environ["SLACK"] == "OFF":
		print("Slack has been turned off, not listening to events")

		@app.route('/', defaults={'path': ''})
		@app.route('/<path:path>')
		def catch_all(path):
			return 'Slack Has Been Turned Off For this Application' % path

	else:
		raise Exception("Slack App initialised with incorrect SLACK env var")

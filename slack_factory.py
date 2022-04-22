import os
import time

import eric
from application import add_repair_event, s_help, clients
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

		@app.command('/repair')
		def begin_slack_repair_process(ack, body, logger, client):
			"""
			occurs when user types /devrepair
			pushes a loading view while fetching the repair at the top of the users monday group
			updates view to pre-repair overview showing deadlines and model details and a button to begin the repair,
			which triggers on view submission
			view submission = pre_repair_info
			"""
			logger.info("Repair process request received")
			eric.begin_slack_repair_process(body, client, ack)
			return True

		@app.command("/devrepair")
		def begin_slack_repair_process_dev(ack, body, logger, client):
			"""
			occurs when user types /devrepair
			pushes a loading view while fetching the repair at the top of the users monday group
			updates view to pre-repair overview showing deadlines and model details and a button to begin the repair,
			which triggers on view submission
			view submission = pre_repair_info
			"""
			logger.info("Repair process request received")
			eric.begin_slack_repair_process(body, client, ack, dev=True)
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
			eric.check_stock(body, client, initial=True)

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

		# Repair Issue Submit Routes
		@app.action("dropdown_repair_issue_selector_action")
		def handle_repair_issue_selection(ack, body, logger, client):
			selected = body["actions"][0]["selected_option"]["value"]

			if selected in ["charge", "parts", "passcode"]:
				eric.handle_other_repair_issue(body, client, ack, initial=False, more_info=False)
			elif selected == "other":
				eric.handle_other_repair_issue(body, client, ack, initial=False, more_info=True)
			else:
				raise Exception(
					f"Slack dropdown_repair_issue_selector_action listener got unepexpected selected value: {selected}"
				)

		# Other Action Routes

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
			ack()

			eric.show_walk_in_info(body, client, from_search=True)

		@app.action("select_accept_device_type")
		def accept_walkin_device_type(ack, body, logger, client):
			logger.info("Walkin Accept Device Type Selected")
			ack()

			eric.handle_walk_in_updates(body, client, "device_type")

		@app.action("select_accept_device")
		def accept_walkin_device(ack, body, logger, client):
			logger.info("Walkin Accept Device Selected")
			ack()

			eric.handle_walk_in_updates(body, client, "device")

		@app.action("radio_accept_device")
		def accept_walkin_repair_type(ack, body, logger, client):
			logger.info("Walkin Accept Device Selected")
			ack()

			eric.handle_walk_in_updates(body, client, "repair_type")

		@app.action("select_booking")
		def begin_walk_in_receipt(ack, body, logger, client):
			logger.info('Beginning walk in acceptance process')
			ack()

			eric.show_walk_in_info(body, client, from_booking=True)

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

		@app.action("parts_selection")
		def validate_repair_selection(ack, body, logger, client):
			logger.info("Parts Validation/Selection process request")
			ack()

		@app.action("repairs_parts_select")
		def add_part_to_repair(ack, body, logger, client):
			logger.info("Adding Part to Repair")
			ack()
			eric.add_parts_to_repair(body, client, ack=ack, initial=False)

		@app.action("repairs_parts_remove")
		def remove_parts_from_repair(ack, body, logger, client):
			logger.info("Removing Part from Repair")
			eric.add_parts_to_repair(body, client, ack=ack, initial=False, remove=True)

		@app.action("button_waste_selection")
		def update_waste_record_view(ack, body, logger, client):
			logger.info("Waste Record Request Received")
			eric.process_waste_entry(ack, body, client)

		@app.action("button_waste_remove")
		def handle_some_action(ack, body, logger, client):
			logger.info("Removing Part From Waste Record")
			eric.process_waste_entry(ack, body, client, remove=True)

		# =========== View Submissions

		@app.view("pre_repair_info")
		def begin_specific_slack_repair(ack, body, logger, client):
			logger.info("Response to Repair Beginning Received")
			eric.begin_specific_slack_repair(body, client, ack)
			return True

		@app.view("new_user_input")
		def add_new_user(ack, body, logger, client):
			logger.info("New User Inputs Received, Adding User")

			eric.check_and_create_new_user(body, client, ack)

		@app.view("new_user_walkin_submission")
		def port_new_user_to_booking_info(ack, body, logger, client):
			logger.info("New User Created and Repair Acceptance Begun")

			eric.show_walk_in_info(body, client, from_create=ack)

		@app.view("walkin_acceptance_submission")
		def handle_final_walkin_submission(ack, body, logger, client):
			logger.info("Walk In Repair Accepted - Processing")
			errors = {}
			repair_type = body["view"]["state"]["values"]['text_pc']["text_accept_pc"]["value"]
			pc = body["view"]["state"]["values"]['text_pc']["text_accept_pc"]["value"]
			p(body)
			if not pc and repair_type == "Diagnostic":
				errors["text_accept_pc"] = "Passcodes are required for Diagnostics"

			if len(errors) > 0:
				ack(
					response_action="errors",
					errors=errors
				)
				return

			ack(
				response_action="clear"
			)
			logger.info(body)
			eric.process_walkin_submission(body, client, ack)

		@app.view("repair_phase_ended")
		def end_repair_phase(ack, body, logger, client):
			logger.info("Response to Repair Phase Complete")

			selected = \
				body['view']['state']['values']['repair_result_select']['repair_result_select']['selected_option'][
					'value']

			if not selected:
				raise Exception(
					f"Unexpected Action ID in 'actions' object after end_repair_phase, could not find: 'end_repair_phase'")

			if selected == 'repaired':
				eric.add_parts_to_repair(body, client, initial=True, ack=ack)
			elif selected == 'client':
				eric.handle_other_repair_issue(body, client, ack, initial=True, more_info=False)
			elif selected == 'other':
				eric.handle_other_repair_issue(body, client, ack, initial=True, more_info=False)
			else:
				raise Exception(f"Unexpected Value from Static Select Actions End Repair Phase: {selected}")

		@app.view("repair_issue_submit")
		def process_repair_issue(body, client, ack, logger):
			logger.info("Logging Repair Issue")
			selected = body["view"]["state"]["values"]["dropdown_repair_issue_selector"]["dropdown_repair_issue_selector_action"]["selected_option"]["value"]
			eric.process_repair_issue(body, client, ack, standard=selected)

		@app.view("repairs_parts_submission")
		def validate_submitted_parts_selection(ack, body, logger, client):
			logger.info("Parts Submitted - Providing Summary Route")
			eric.show_variant_selections(body, client, ack)

		@app.view("variant_selection_submission")
		def add_variants_to_repair_and_confirm(ack, body, logger, client):
			logger.info("Variants Selected, Adding to Repair and Confirming")
			eric.show_repair_and_parts_confirmation(body, client, ack, from_variants=True)

		@app.view("repair_completion_confirmation")
		def process_repair_completion_confirmation(ack, body, logger, client):
			logger.info("Repair Confirmation Submitted: Checking for Waste and Processing")
			logger.info("Calling eric.finalise_repair_data")
			logger.debug(body)
			eric.finalise_repair_data_and_request_waste(body, client, ack)

		@app.view("waste_opt_in")
		def validate_wasted_parts(ack, body, logger, client):
			logger.info("Validating Wasted Repair Info")

			selected = body["view"]["state"]["values"]["waste_opt_in"]["waste_opt_in_action"]["selected_option"]["value"]

			if selected == "waste":
				eric.process_waste_entry(ack, body, client, initial=True)
			elif selected == "no_waste":
				ack({"response_action": "clear"})
			else:
				raise Exception(f"slack waste_opt_in received unknown response selection: {selected}")

		@app.view("waste_parts_submission")
		def validate_wasted_parts(ack, body, logger, client):
			logger.info("Validating Wasted Repair Info")
			eric.show_waste_validations(body, client, ack)

		@app.view("waste_validation_submission")
		def confirm_waste_quantities(ack, body, logger, client):
			logger.info("Confirming Quantities of Wasted Parts")
			eric.confirm_waste_quantities(body, client, ack)

		@app.view("waste_quantity_submission")
		def capture_waste_item_data(ack, body, client, logger):
			logger.info("Emitting Waste Events")
			ack()
			eric.emit_waste_events(body, client, ack)

		# view closed routes

		# repair phase abort
		@app.view_closed("repair_phase_ended")
		@app.view_closed("repair_issue_submit")
		@app.view_closed("repairs_parts_submission")
		@app.view_closed("variant_selection_submission")
		@app.view_closed("repair_completion_confirmation")
		@app.view_closed("waste_parts_submission")
		@app.view_closed("waste_validation_submission")
		@app.view_closed("waste_quantity_submission")
		@app.view_closed("waste_opt_in")
		def abort_repair_phase(ack, body, logger, client):
			logger.info("User Closed a Repair Phase Modal")
			ack({
				"response_action": "clear"
			})
			eric.abort_repair_phase(body)

	elif os.environ["SLACK"] == "OFF":
		print("Slack has been turned off, not listening to events")

		@app.route('/', defaults={'path': ''})
		@app.route('/<path:path>')
		def catch_all(path):
			return 'Slack Has Been Turned Off For this Application' % path

	else:
		raise Exception("Slack App initialised with incorrect SLACK env var")

import os
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
		token = os.environ["SLACK_BOT_TOKEN"]
		app = App(token=token)
		_add_routing(app)
		handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
		handler.connect()
	else:
		raise Exception("Slack App initialised with incorrect SLACK env var")

	return app


def _add_routing(app):
	if os.environ["SLACK"] == "ON":

		# =========== Commands

		@app.command("/test")
		def run_test_action(ack, body, logger, client, say):
			ack()
			eric.test_route(body, client, say)

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

		# =========== Action Block Submissions
		@app.action("repair_complete")
		def repair_info_submission(ack, body, logger, client):
			logger.info("Response to Repair Info Submission")
			ack()

			selected = None
			for action in body['actions']:
				print("ACTION ID ====================")
				print(action['action_id'])
				if action['action_id'] == 'repair_complete':
					selected = action['selected_option']['value']

			if not selected:
				raise Exception("Unexpexcted Action ID in 'actions' object after repair_complete")

			if selected == 'complete':
				eric.repair_info_submission(body, client)
			elif selected == 'failed':
				eric.tech_unable_to_complete_repair(body, client)
			elif selected == 'urgent':
				eric.handle_urgent_repair(body, client)
			elif selected == 'other':
				eric.handle_other_repair_issue(body, client)
			else:
				raise Exception("Unexpected Value from Static Select Actions Repair Submission")

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

		# =========== View Submissions

		@app.view("pre_repair_info")
		def begin_specific_slack_repair(ack, body, logger, client):
			logger.info("Response to Repair Beginning Received")
			ack()
			eric.begin_specific_slack_repair(body, client)
			return True



	elif os.environ["SLACK"] == "OFF":
		print("Slack has been turned off, not listening to events")

		@app.route('/', defaults={'path': ''})
		@app.route('/<path:path>')
		def catch_all(path):
			return 'Slack Has Been Turned Off For this Application' % path

	else:
		raise Exception("Slack App initialised with incorrect SLACK env var")

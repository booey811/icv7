import os
import eric

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
			logger.info("Repair process request received")
			ack()
			eric.begin_slack_repair_process(body, client)
			return True

		# =========== Action Block Submissions

		@app.action("begin-repair-button-confirm")
		def begin_specific_slack_repair(ack, body, logger, client):
			logger.info("Response to Repair Beginning Received")
			ack()
			eric.begin_specific_slack_repair(body, client)
			return True

		# =========== View Submissions

		@app.view("repair_submission")
		def repair_info_submission(ack, body, logger, client):
			logger.info("Response to Repair Info Submission")
			ack()
			eric.repair_info_submission(body, client)

	elif os.environ["SLACK"] == "OFF":
		print("Slack has been turned off, not listening to events")

		@app.route('/', defaults={'path': ''})
		@app.route('/<path:path>')
		def catch_all(path):
			return 'Slack Has Been Turned Off For this Application' % path

	else:
		raise Exception("Slack App initialised with incorrect SLACK env var")

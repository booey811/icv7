import os
import json
from datetime import datetime

import flask


from . import config
from .monday import BaseItem, inventory, financial, mon_ex, mon_config
from .utilities import clients, add_repair_event, get_timestamp
from .zendesk.ticket import EricTicket
from .phonecheck import phonecheck, CannotFindReportThroughIMEI
from .xero import accounting, xero_ex
from .zendesk import helper as zen_help
from .zendesk import fields
from .slack import views, config as slack_config, helper as s_help, exceptions as slack_ex
from .stuart import couriers

log_board = clients.monday.system.get_boards(ids=[1760764088])[0]

def add_to_brick_chain(event_id):
	event = BaseItem(CustomLogger(), event_id)
	blank_brick = BaseItem(event.logger, board_id=2593044634)
	new_item = blank_brick.new_item(event.name)
	event.bricks_link.value = [new_item.id]


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
		raise ChallengeReceived(authtoken)
	else:
		return data




def create_app():
	# Detect Environment & Retrieve config
	env = os.environ['ENV']
	if env == 'production':
		print('Config:Production')
		configuration = config.ProdConfig()
	elif env in ['devlocal', 'devserver']:
		print('Config:DevLocal')
		configuration = config.DevConfig()
	else:
		raise Exception('ENV config var is not set correctly - cannot boot')

	# Create and configure app
	app = flask.Flask('eric')
	app.config.from_object(configuration)
	return app


class ChallengeReceived(Exception):
	"""
	Exception that is thrown when the Monday challenge is received, stores the challenge token for return to app
	level function
	"""

	def __init__(self, token):
		self.token = token


class HardLog(Exception):

	def __init__(self, message):
		print(message)


class CustomLogger:
	"""Object for managing logging as Flask logging is a nightmare
	Dumps information to a monday item with log file"""

	def __init__(self):
		if os.environ['ENV'] in ['production', 'test']:
			self.debug = False
		else:
			self.debug = True

		self.func = 'Not Supplied'
		self.summary = "Not Supplied"

		self._log_file_path = None
		self._log_name = self._generate_log_file_name()
		self._log_board = log_board

		self._log_lines = []

		self.log_file_path = True

	@staticmethod
	def _generate_log_file_name():
		now = datetime.now()
		date_time = now.strftime("%d%b|%H-%M-%S")
		name = f'Instance-{date_time}.txt'
		return name

	def _create_log(self):
		with open(self.log_file_path, 'w') as log:
			for line in self._log_lines:
				log.write(line)
				log.write('\n')

		return True

	@property
	def log_file_path(self):
		return self._log_file_path

	@log_file_path.setter
	def log_file_path(self, value=True):
		if not self._log_file_path:
			if os.environ["ENV"] == 'devlocal':
				directory = os.path.dirname(__file__)[:-12]
				self._log_file_path = directory + f'/tmp/logs/{self._log_name}'
			else:
				self._log_file_path = f'tmp/logs/{self._log_name}'

	def log(self, log_line):
		self._log_lines.append(log_line)
		if self.debug:
			print(log_line)

	def soft_log(self, for_records=False):
		"""creates a log entry in the logs board but does not halt execution"""
		# Create the log file

		self.log('==== SOFT LOG REQUESTED =====')
		if os.environ['ENV'] == 'prod' or for_records:
			self._create_log()
			col_vals = {
				'status': {'label': 'Soft'}
			}
			log_item = self._log_board.add_item(
				item_name=self._log_name,
				column_values=col_vals
			)
			file_column = log_item.get_column_value(id='file')
			log_item.add_file(file_column, self._log_file_path)
			return log_item

	def hard_log(self, for_records=False):
		"""creates a log entry in the logs board and halts execution"""
		self.log('==== HARD LOG REQUESTED =====')

		if os.environ['ENV'] == 'prod' or for_records:
			# Create the log file
			self._create_log()
			col_vals = {
				'status': {'label': 'Hard'}
			}
			log_item = self._log_board.add_item(
				item_name=self._log_name,
				column_values=col_vals
			)
			file_column = log_item.get_column_value(id='file')
			log_item.add_file(file_column, self._log_file_path)

		raise HardLog(f'Hard Log Requested: {self._log_name}')

	def clear(self):
		"""Delete the generated log file"""
		try:
			os.remove(self.log_file_path)
		except FileNotFoundError:
			pass

	def commit(self, log_level="success"):

		LABELS = {
			"success": "Success",
			"raised": "Raised",
			"error": "Unexpected",
			"user": "User Error",
			'waiting': "Waiting for User"
		}

		log_label = LABELS[log_level]

		col_vals = {
			'new_log_type': {'label': log_label},
			"text7": str(self.func),
			"text2": str(os.getenv("ENV")),
			"long_text": str(self.summary).replace('"', '').replace('/', '')
		}

		if log_level == "success":
			col_vals["status7"] = {"label": "Not Needed"}

		log_item = self._log_board.add_item(
			item_name=self._log_name,
			column_values=col_vals
		)

		if log_level != 'success':
			self._create_log()
			file_column = log_item.get_column_value(id='file')
			log_item.add_file(file_column, self._log_file_path)


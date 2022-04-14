import os
from datetime import datetime, timezone
import json

from moncli.entities import MondayClient, Item
from zenpy import Zenpy

import settings


def add_repair_event(main_item_or_id, event_name, event_type, summary='', actions_dict=()):

	actions_status = "Not Done"

	if type(main_item_or_id) in (str, int):
		main_item = clients.monday.system.get_items(ids=[main_item_or_id])[0]
	elif type(main_item_or_id) is Item:
		main_item = main_item_or_id
	else:
		raise Exception(f"Cannot Add Repair Event: MainItem or ID was given as {str(main_item_or_id)}")

	if not summary:
		summary = "Not Provided"

	if not actions_dict:
		actions_dict = 'No Actions To Perform'
		actions_status = "No Actions Required"
	else:
		actions_dict = json.dumps(actions_dict)

	if not event_type:
		event_type = "Not Assigned"

	timestamp_val = datetime.now(timezone.utc).strftime("%Y-%m-%d %X")

	main_item.create_subitem(
		item_name=event_name,
		column_values={
			"date": timestamp_val,
			"status1": {"label": str(event_type)},
			"long_text": summary,
			"long_text2": actions_dict,
			"status0": {'label': actions_status}
		}
	)


def create_monday_client(user: str = 'system') -> MondayClient:
	"""
Function to create and return a moncli client relating to the specified user

    :param user: the user to create the client as (default 'system')
    :return: MondayClient created with requested user credentials
    """
	if user == 'error':
		key = os.getenv('MONV2ERR')
	elif user == 'email':
		key = os.getenv('MONV2EML')
	elif user == 'system':
		key = os.getenv('MONV2SYS')
	else:
		raise Exception(f'"{user}" provided as user for Moncli client, not valid')

	client = MondayClient()
	client.api_key = key
	return client


def create_zendesk_client():
	creds = {
		"email": 'admin@icorrect.co.uk',
		"token": os.environ["ZENDESKADMIN"],
		"subdomain": "icorrect"
	}
	client = Zenpy(
		email='admin@icorrect.co.uk',
		token=os.environ["ZENDESKADMIN"],
		subdomain="icorrect"
	)
	return client


class MondayClientCollection:

	def __init__(self):
		self._system = None
		self._error = None
		self._email = None

	@property
	def system(self) -> MondayClient:
		"""
Used to access the Monday Client acting as the 'System' User
This is the default client to be used for Monday interactions
        :return: Monday 'System' Client
        """
		if self._system:
			return self._system
		else:
			self.system = create_monday_client()
			return self._system

	@system.setter
	def system(self, monday_client):
		"""
Used to set the Monday Client for the 'System' User
        :param monday_client: The 'System' Monday Client
        """
		self._system = monday_client

	@property
	def email(self) -> MondayClient:
		"""
Used to access the Monday Client acting as the 'Email' User
        :return: Monday 'Email' Client
        """
		if self._email:
			return self._email
		else:
			self.email = create_monday_client('email')
			return self._email

	@email.setter
	def email(self, monday_client):
		"""
    Used to set the Monday Client for the 'Email' User
        :param monday_client: The 'Email' Monday Client
        """
		self._email = monday_client

	@property
	def error(self) -> MondayClient:
		"""
Used to access the Monday Client acting as the 'Error' User
        :return: Monday 'Email' Client
        """
		if self._error:
			return self._error
		else:
			self._error = create_monday_client('error')
			return self._error

	@error.setter
	def error(self, monday_client):
		"""
    Used to set the Monday Client for the 'Error' User
        :param monday_client: The 'Error' Monday Client
        """
		self._error = monday_client


class ClientsObject:
	def __init__(self):
		self.monday = MondayClientCollection()
		self.zendesk = create_zendesk_client()


clients = ClientsObject()

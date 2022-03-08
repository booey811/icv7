import requests
import json
import os
from pprint import pprint as p

from .components import SINGLE_SELECT_OPTION, SINGLE_SELECT_BLOCK_WITH_RESPONSE
from . import exceptions

BASE_URL = "https://slack.com/api/"

HEADERS = {
	"Authorization": f"Bearer {os.environ['SLACKBOT']}",
	"Content-Type": "application/json"
}

TEST_CHANNEL = "C036M43NBR6"


def _test_auth():
	url = "auth.test"
	method = 'POST'
	info = _send_request(url, method)
	return info


def _send_request(url_end, method, data=''):
	"""base function for sending Slack requests - attaches url_end to BASEURL, converts data (if supplied) and
	analyses response"""

	url = BASE_URL + url_end

	if data:
		response = requests.request(method=method, url=url, headers=HEADERS, data=data)
	else:
		response = requests.request(method=method, url=url, headers=HEADERS)

	return response


class MessageBuilder:

	def __init__(self):
		self._body = {}
		self._reset()
		self.blocks = BlockBuilder()

	def post(self, channel=TEST_CHANNEL):
		method = 'POST'
		self._body['channel'] = channel
		data = json.dumps(self._body)
		info = _send_request('chat.postMessage', method, data)
		print(f'=================== STATUS {info.status_code} ======================')
		if info.status_code == 200:
			return json.loads(info.text)
		else:
			p(json.loads(info.text))

	def construct_message(self, key_value_dict):
		block = self.blocks.construct_actions_block(static_select=key_value_dict)
		self._body['blocks'].append(block)

	def _reset(self):
		dct = {
			'channel': '',
			'blocks': []
		}
		self._body = dct


class BlockBuilder:
	def __init__(self):
		self.elementor = ElementBuilder()

	def construct_actions_block(self, static_select: dict = None):

		BL_TYPES = [
			'actions'
		]

		block = self._basic_block_structure('actions')

		if static_select:
			element = self.elementor.construct_element('static_select', static_select)
		else:
			raise exceptions.InvalidTypeSet(self, 'NOT DEVELOPED', BL_TYPES)

		block['elements'].append(element)

		return block

	@staticmethod
	def _basic_block_structure(bl_type):
		dct = {
			'type': bl_type,
			'elements': [],
			'block_id': 'BLOCKID-GABE'
		}
		return dct


class ElementBuilder:
	def __init__(self):
		self._options = OptionsBuilder()

	def construct_element(self, el_type, text_value_dictionary):

		EL_TYPES = (
			'static_select',
		)

		if el_type not in EL_TYPES:
			raise exceptions.InvalidTypeSet(self, el_type, EL_TYPES)

		element = self._basic_element_structure(el_type)

		for key in text_value_dictionary:
			option = self._options.construct_single_select_option(key, text_value_dictionary[key])
			element['options'].append(option)

		return element

	@staticmethod
	def _basic_element_structure(el_type):
		dct = {
			'type': el_type,
			'placeholder': {
				'type': 'plain_text',
				'text': 'Default Placeholder Text',
				'emoji': True
			},
			'options': [],
			'action_id': 'ELEMENTID-GABE'
		}
		return dct


class OptionsBuilder:
	"""object to construct options for nesting within elements. should contain methods to produce the options array
	for all elements"""
	def __init__(self):
		pass

	def construct_single_select_option(self, label, value):
		"""constructs a response option for a single select block question in Slack

		Args:
		label (str): the label that should be present on the option
		value (str): an external reference to tie the response into eric (usually some sort of Monday ID)

		Returns:
		dict: the formatted single select option dictionary
		"""
		option = self._single_select_option()
		option["text"]["text"] = label
		option["value"] = str(value)

		return option

	@staticmethod
	def _single_select_option():
		dct = {
			"text": {
				"type": "plain_text",
				"text": "",
				"emoji": True
			},
			"value": ""
		}
		return dct

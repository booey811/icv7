import requests
import json
import os
from pprint import pprint as p

from .components import SINGLE_SELECT_OPTION, SINGLE_SELECT_BLOCK_WITH_RESPONSE
from . import exceptions, config

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

	def post(self):
		method = 'POST'
		data = json.dumps(self._body)
		info = _send_request('chat.postMessage', method, data)
		self._reset()
		if info.status_code == 200:
			return json.loads(info.text)
		else:
			raise exceptions.CouldNotPostMessage(info)

	def attach_static_select_block(self, static_select_dictionary):
		block = blocks.construct_actions_block(static_select_dictionary)
		self._attach_block(block)

	def attach_header_block(self, header_text):
		block = blocks.construct_header_block(header_text)
		self._attach_block(block)

	def attach_markdown_block(self, markdown_text):
		block = blocks.construct_markdown_block(markdown_text)
		self._attach_block(block)

	def set_channel(self, channel):
		if channel not in config.CHANNELS:
			raise exceptions.CannotGetChannel(channel, config.CHANNELS)
		else:
			self._body['channel'] = config.CHANNELS[channel]

	def _attach_block(self, block):
		self._body['blocks'].append(block)

	def _reset(self):
		dct = {
			'channel': config.CHANNELS['devtest'],
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
			element = elements.construct_element('static_select')
			for key in static_select:
				option = options.construct_single_select_option(key, static_select[key])
				element['options'].append(option)
		else:
			raise exceptions.InvalidTypeSet(self, 'NOT DEVELOPED', BL_TYPES)

		block['elements'].append(element)

		return block

	@staticmethod
	def construct_header_block(header_text):
		dct = options.construct_header_option(header_text)
		dct['type'] = 'header'
		return dct

	@staticmethod
	def construct_markdown_block(markdown_text):
		dct = options.construct_markdown_option(markdown_text)
		dct['type'] = 'section'
		return dct

	@staticmethod
	def _basic_block_structure(block_type):
		dct = {
			'type': block_type,
			'elements': [],
			'block_id': 'BLOCKID-GABE'
		}
		return dct


class ElementBuilder:
	def __init__(self):
		pass

	def construct_element(self, el_type):
		EL_TYPES = (
			'static_select',
		)
		if el_type not in EL_TYPES:
			raise exceptions.InvalidTypeSet(self, el_type, EL_TYPES)
		elif el_type == 'static_select':
			element = self._static_select_element(el_type)
		else:
			raise exceptions.InvalidTypeSet(self, el_type, EL_TYPES)
		return element

	@staticmethod
	def _static_select_element(el_type):
		dct = {
			'type': el_type,
			'placeholder': {
				'type': 'plain_text',
				'text': 'Please Choose A Response',
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
		option = self._single_select(str(label), str(value))
		return option

	def construct_markdown_option(self, markdown_text):
		return self._markdown(markdown_text)

	def construct_header_option(self, header_text):
		return self._header(header_text)

	@staticmethod
	def _single_select(label, value):
		dct = {
			"text": {
				"type": "plain_text",
				"text": label,
				"emoji": True
			},
			"value": value
		}
		return dct

	@staticmethod
	def _markdown(markdown_text):
		dct = {
			"text": {
				"type": "mrkdwn",
				"text": markdown_text
			}
		}
		return dct

	@staticmethod
	def _header(header_text):
		return {
			'text': {
				"type": "plain_text",
				"text": header_text,
				"emoji": True
			}
		}


blocks = BlockBuilder()
elements = ElementBuilder()
options = OptionsBuilder()

import datetime
import json
from pprint import pprint as p

import data
from . import helper, config
from application import mon_config


def _convert_monday_time_to_string(monday_date_column):
	if monday_date_column.date:
		try:
			date = datetime.datetime.strptime(monday_date_column.value, '%Y-%m-%d %H:%M')
		except ValueError:
			try:
				date = datetime.datetime.strptime(monday_date_column.value, '%Y-%m-%d')
			except ValueError:
				return "Not Provided (This REALLY Shouldn't Happen (col has date but does match strptime options))"
		return date.strftime('%a %-d %b %H:%M')

	else:
		return "Not Provided (This Shouldn't Happen)"


def _get_repairs_string(main_item):
	if main_item.repairs.labels:
		return ", ".join(main_item.repairs.labels)
	else:
		return 'No Repairs Requested, please diagnose the device'


def _construct_markdown_option(title, description='', chosen_value=''):
	dct = {
		"text": {
			"type": "mrkdwn",
			"text": title
		},
		"description": {
			"type": "mrkdwn",
			"text": description
		},
		"value": chosen_value
	}

	if description:
		dct['description'] = {"type": "mrkdwn", "text": description}

	if chosen_value:
		dct['value'] = chosen_value
	else:
		dct['value'] = f"{title.replace(' ', '-')}-not-given-value"

	return dct


def loading(footnotes=''):
	"""returns the view for the modal screen showing that the application has received a request and is processing it
	adds in a footnote to the loading screen for more specific information"""
	view = {
		"type": "modal",
		"title": {
			"type": "plain_text",
			"text": "Beginning Repairs",
			"emoji": True
		},
		"close": {
			"type": "plain_text",
			"text": "Cancel",
			"emoji": True
		},
		"blocks": [
			{
				"type": "header",
				"text": {
					"type": "plain_text",
					"text": "Please wait... Eric is thinking big thoughts",
					"emoji": True
				}
			}
		]
	}

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
		view['blocks'].append(context)

	return view


def bookings_search_input(body, invalid_search=False):
	metadata = helper.get_metadata(body)

	search = {
		'type': "modal",
		"private_metadata": json.dumps(metadata),
		"title": {
			"type": "plain_text",
			"text": "Bookings Search",
			"emoji": True
		},
		"close": {
			"type": "plain_text",
			"text": "Cancel",
			"emoji": True
		},
		'blocks': [{
			"dispatch_action": True,
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "bookings_search"
			},
			"label": {
				"type": "plain_text",
				"text": "Enter booking name (or Monday ID :nerd_face:):",
				"emoji": True
			}
		}]
	}

	if invalid_search:
		to_add = [{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": ":confused: Sorry, I couldn't find anyone by that name",
				"emoji": True
			}
		},
			{
				"type": "context",
				"elements": [
					{
						"type": "plain_text",
						"text": "Check Today's Repairs to see why :nerd_face:",
						"emoji": True
					}
				]
			}]

		search['blocks'] = to_add + search['blocks']

	return search


def bookings_search_results(body):
	search_block_id = body['actions'][0]['block_id']

	basic = {}


def todays_repairs(bookings):

	def generate_results_blocks(monday_bookings):
		def generate_results_block(client_name, main_id):
			dct = {
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": client_name
				},
				"accessory": {
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Accept",
						"emoji": True
					},
					"value": main_id,
					"action_id": "select_booking"
				}
			}
			return dct

		blocks = [{"type": "divider"}]
		for item in monday_bookings:
			blocks.append(generate_results_block(item.name, str(item.id)))
			blocks.append({"type": "divider"})

		return blocks

	view = {
		"type": "modal",
		"title": {
			"type": "plain_text",
			"text": "My App",
			"emoji": True
		},
		"submit": {
			"type": "plain_text",
			"text": "Submit",
			"emoji": True
		},
		"close": {
			"type": "plain_text",
			"text": "Cancel",
			"emoji": True
		},
		"blocks": generate_results_blocks(bookings)
	}
	return view


def pre_repair_info(main_item, resp_body):
	item_id = main_item.mon_id
	client_name = main_item.name
	repair_type = main_item.repair_type.label
	device_label = main_item.device.labels[0]
	repairs_string = ", ".join(main_item.repairs.labels)
	received_date = _convert_monday_time_to_string(main_item.received_date)
	deadline = _convert_monday_time_to_string(main_item.deadline_date)

	metadata = helper.get_metadata(resp_body)
	metadata['main'] = main_item.mon_id
	metadata["extra"]["repair_type"] = repair_type
	helper.add_device_type_metadata(main_item, metadata)

	basic = {
		"type": "modal",
		"callback_id": "pre_repair_info",
		"title": {
			"type": "plain_text",
			"text": f"Repair: {item_id}",
			"emoji": True
		},
		"submit": {
			"type": "plain_text",
			"text": "Begin Repair",
			"emoji": True
		},
		"close": {
			"type": "plain_text",
			"text": "Cancel",
			"emoji": True
		},
		"private_metadata": json.dumps(metadata),
		"blocks": [
			{
				"type": "header",
				"text": {
					"type": "plain_text",
					"text": f"{client_name} | {repair_type}",
					"emoji": True
				}
			},
			{
				"type": "context",
				"elements": [
					{
						"type": "plain_text",
						"text": f"Device: {device_label}",
						"emoji": True
					}
				]
			},
			{
				"type": "context",
				"elements": [
					{
						"type": "plain_text",
						"text": f"Requested Repairs: {_get_repairs_string(main_item)}",
						"emoji": True
					}
				]
			},
			{
				"type": "context",
				"elements": [
					{
						"type": "plain_text",
						"text": f"Received: {received_date}",
						"emoji": True
					}
				]
			},
			{
				"type": "context",
				"elements": [
					{
						"type": "plain_text",
						"text": f"Deadline: {deadline}",
						"emoji": True
					}
				]
			},
		]
	}

	return basic


def repair_phase_view(main_item, body):
	item_id = main_item.mon_id
	device = main_item.device.labels[0]
	repair_type = main_item.repair_type.label
	repairs_string = ", ".join(main_item.repairs.labels)
	start_time = datetime.datetime.now().strftime("%X")

	metadata = helper.get_metadata(body)

	basic = {
		"type": "modal",
		"callback_id": "repair_phase",
		"private_metadata": json.dumps(metadata),
		"title": {
			"type": "plain_text",
			"text": "Repairing",
			"emoji": True
		},
		"submit": {
			"type": "plain_text",
			"text": "Submit",
			"emoji": True
		},
		"close": {
			"type": "plain_text",
			"text": "Cancel",
			"emoji": True
		},
		"blocks": [
			{
				"type": "header",
				"text": {
					"type": "plain_text",
					"text": f"Repair: {item_id} | {device} | {repair_type}",
					"emoji": True
				}
			},
			{
				"type": "context",
				"elements": [
					{
						"type": "plain_text",
						"text": f"Repair Run Started: {start_time}",
						"emoji": True
					}
				]
			},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "The client has requested the following repairs:"
				}
			},
			{
				"type": "context",
				"elements": [
					{
						"type": "plain_text",
						"text": f"{_get_repairs_string(main_item)}",
						"emoji": True
					}
				]
			},
			{
				"type": "divider"
			},
			{
				"type": "input",
				"optional": True,
				"element": {
					"type": "plain_text_input",
					"multiline": True,
					"action_id": "repair_notes"
				},
				"label": {
					"type": "plain_text",
					"text": "Repair Notes",
					"emoji": True
				}
			},
			{
				"type": "input",
				"dispatch_action": True,
				"label": {
					"type": "plain_text",
					"text": "Are you moving on from this repair?",
					"emoji": True
				},
				"element": {
					"type": "static_select",
					"placeholder": {
						"type": "plain_text",
						"text": "Let us know what happened",
						"emoji": True
					},
					"options": [
						{
							"text": {
								"type": "plain_text",
								"text": "The device has been repaired!",
								"emoji": True
							},
							"value": "repaired"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "I need more information",
								"emoji": True
							},
							"value": "client"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "I don't have the parts to complete the repair",
								"emoji": True
							},
							"value": "parts"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "A more urgent repair has been given to me",
								"emoji": True
							},
							"value": "urgent"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "I need help",
								"emoji": True
							},
							"value": "other"
						}
					],
					"action_id": "end_repair_phase"
				}
			},
		]
	}
	return basic


def initial_parts_search_box(body):
	metadata = helper.get_metadata(body)

	search = {
		'type': "modal",
		"private_metadata": json.dumps(metadata),
		"title": {
			"type": "plain_text",
			"text": "Parts Search",
			"emoji": True
		},
		"close": {
			"type": "plain_text",
			"text": "Go Back",
			"emoji": True
		},
		'blocks': [{
			"dispatch_action": True,
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "repair_search"
			},
			"label": {
				"type": "plain_text",
				"text": "Enter search term:",
				"emoji": True
			}
		}]
	}
	return search


def parts_search_results(resp_body):
	def generate_results_block(repair_name):

		dct = {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": repair_name
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "Add Part",
					"emoji": True
				},
				"value": repair_name,
				"action_id": "select_part"
			}
		}
		return dct

	selected_repair = resp_body['actions'][0]['value']

	metadata = helper.get_metadata(resp_body)

	available_repairs = config.PART_SELECTION_OPTIONS[metadata['extra']['device_type']] + config.PART_SELECTION_OPTIONS[
		'General']

	results = []
	for item in available_repairs:
		if selected_repair.upper() in item.upper():
			results.append(item)

	if not results:
		print("============================ NO RESULTS FOUND =======================================================")
		basic = {
			"type": "modal",
			"private_metadata": json.dumps(metadata),
			"title": {
				"type": "plain_text",
				"text": "No results found!",
				"emoji": True
			},
			"close": {
				"type": "plain_text",
				"text": "Go Back",
				"emoji": True
			},
			"blocks": [
				{
					'type': 'section',
					'text': {
						"type": "mrkdwn",
						"text": "Click 'Go Back' to try again"
					}
				}
			]
		}

		return basic

	else:
		blocks = []
		for repair in results:
			blocks.append(generate_results_block(repair))

		basic = {
			"type": "modal",
			"private_metadata": json.dumps(metadata),
			"title": {
				"type": "plain_text",
				"text": "Please select part:",
				"emoji": True
			},
			"close": {
				"type": "plain_text",
				"text": "Go Back",
				"emoji": True
			},
			"blocks": blocks
		}
		return basic


def continue_parts_search(resp_body):
	def generate_selected_parts_line(part_name):
		parts_used_line = {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": part_name
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "Remove Part",
					"emoji": True
				},
				"value": f"{part_name}",
				"action_id": "remove_part"
			}
		}
		return parts_used_line

	def generate_search_block():
		search = {
			"dispatch_action": True,
			"optional": True,
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "repair_search"
			},
			"label": {
				"type": "plain_text",
				"text": "Add More Parts to Repair:",
				"emoji": True
			}
		}
		return search

	new_part = resp_body['actions'][0]['value']

	metadata = helper.get_metadata(resp_body)
	metadata['extra']['selected_repairs'].append(new_part)

	selected_repair_blocks = []
	for repair in metadata['extra']['selected_repairs']:
		selected_repair_blocks.append(generate_selected_parts_line(repair))

	basic = {
		"type": "modal",
		"title": {
			"type": "plain_text",
			"text": "My App",
			"emoji": True
		},
		"submit": {
			"type": "plain_text",
			"text": "Validate Repairs",
			"emoji": True
		},
		"close": {
			"type": "plain_text",
			"text": "Go Back",
			"emoji": True
		},
		"blocks": [
			{
				"type": "header",
				"text": {
					"type": "plain_text",
					"text": "Used Parts:",
					"emoji": True
				}
			}
		]
	}

	if selected_repair_blocks:
		basic['blocks'] += selected_repair_blocks

	# noinspection PyTypeChecker
	basic['blocks'].append(generate_search_block())

	basic["private_metadata"] = json.dumps(metadata)

	return basic


def user_search_request():
	basic = {
		"title": {
			"type": "plain_text",
			"text": "User Search",
			"emoji": True
		},
		"type": "modal",
		"callback_id": "user_search_request",
		"close": {
			"type": "plain_text",
			"text": "Cancel",
			"emoji": True
		},
		"blocks": [
			{
				"dispatch_action": True,
				"type": "input",
				"element": {
					"type": "plain_text_input",
					"action_id": "user_search"
				},
				"label": {
					"type": "plain_text",
					"text": "User Search",
					"emoji": True
				}
			}
		]
	}
	return basic


def user_search_results(zenpy_search_object):
	def _generate_results_blocks():
		def _get_name(username, zendesk_id):

			def _get_username():
				if not username:
					return "looks like we're missing this data"
				else:
					return username

			def _get_id():
				if not zendesk_id:
					return "looks like we're missing this data"
				else:
					return str(zendesk_id)

			dct = {
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": _get_username()
				},
				"accessory": {
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Select User",
						"emoji": True
					},
					"value": _get_id(),
					"action_id": "user_select"
				}
			}
			return dct

		def _get_email(email):

			def _email():
				if not email:
					return "looks like we're missing this data"
				else:
					return email

			dct = {
				"type": "context",
				"elements": [
					{
						"type": "mrkdwn",
						"text": f"*Email*: {_email()}"
					}
				]
			}
			return dct

		def _get_phone(phone):

			def _phone():
				if not phone:
					return "looks like we're missing this data"
				else:
					return phone

			dct = {
				"type": "context",
				"elements": [
					{
						"type": "mrkdwn",
						"text": f"*Phone*: {_phone()}"
					}
				]
			}
			return dct

		blocks = []

		for user in zenpy_search_object:
			blocks.append(_get_name(user.name, user.id))
			blocks.append(_get_email(user.email))
			blocks.append(_get_phone(user.phone))
			blocks.append({"type": "divider"})

		from pprint import pprint as p

		p(len(blocks))

		p(blocks)

		return blocks

	basic = {
		"title": {
			"type": "plain_text",
			"text": "User Search",
			"emoji": True
		},
		"type": "modal",
		"callback_id": "user_search_results",
		"close": {
			"type": "plain_text",
			"text": "Search Again",
			"emoji": True
		},
		"blocks": _generate_results_blocks()
	}

	return basic


class OptionBuilder:

	def __init__(self):
		pass

	@staticmethod
	def checkbox_option(title, description='', value=''):

		res = {
			"text": {
				"type": "mrkdwn",
				"text": title
			},
		}

		if description:
			res['description'] = {
				"type": "mrkdwn",
				"text": "*this is mrkdwn text*"
			}

		if value:
			res['value'] = value
		else:
			res['value'] = f"{title}-no-value"

		return res

	@staticmethod
	def text_field_option(text):

		dct = {
			"type": "plain_text",
			"text": text,
			"emoji": True
		}
		return dct

	@staticmethod
	def static_select_option(text, value):
		dct = {
			"text": {
				"type": "plain_text",
				"text": text,
				"emoji": True
			},
			"value": value
		}

		return dct


build = OptionBuilder()

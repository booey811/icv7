import datetime
import json

from . import helper
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


def pre_repair_info(main_item):
	item_id = main_item.mon_id
	client_name = main_item.name
	repair_type = main_item.repair_type.label
	device_label = main_item.device.labels[0]
	repairs_string = ", ".join(main_item.repairs.labels)
	received_date = _convert_monday_time_to_string(main_item.received_date)
	deadline = _convert_monday_time_to_string(main_item.deadline_date)

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
		"private_metadata": helper.encode_metadata(main_item),
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


def specific_repair_view(main_item):
	item_id = main_item.mon_id
	device = main_item.device.labels[0]
	repair_type = main_item.repair_type.label
	repairs_string = ", ".join(main_item.repairs.labels)
	start_time = datetime.datetime.now().strftime("%X")

	basic = {
		"type": "modal",
		"callback_id": "repair_submission",
		"private_metadata": helper.encode_metadata(main_item),
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
								"text": "Repair Completed",
								"emoji": True
							},
							"value": "complete"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "I am unable to complete the repair right now",
								"emoji": True
							},
							"value": "failed"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "A more urgent repair has come in",
								"emoji": True
							},
							"value": "urgent"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "I've got a different issue",
								"emoji": True
							},
							"value": "other"
						}
					],
					"action_id": "repair_complete"
				}
			},
		]
	}
	return basic


def repair_submission(main_item):
	def _generate_parts_options_list():
		if 'iPhone' in main_item.device.labels[0]:
			id_s = mon_config.STANDARD_REPAIR_OPTIONS['iPhone']
		elif 'iPad' in main_item.device.labels[0]:
			id_s = mon_config.STANDARD_REPAIR_OPTIONS['iPad']
		elif 'Watch' in main_item.device.labels[0]:
			id_s = mon_config.STANDARD_REPAIR_OPTIONS['Apple Watch']
		else:
			id_s = mon_config.STANDARD_REPAIR_OPTIONS['MacBook']

		options = []
		for repair_id in id_s:
			title = main_item.repairs.settings[str(repair_id)]
			value = f"r_id:{main_item.device.ids[0]}-{repair_id}"
			options.append(build.checkbox_option(title, value=value))

		return options

	def _generate_faults_list():
		if 'iPhone' in main_item.device.labels[0]:
			id_s = mon_config.STANDARD_REPAIR_OPTIONS['iPhone']
		elif 'iPad' in main_item.device.labels[0]:
			id_s = mon_config.STANDARD_REPAIR_OPTIONS['iPad']
		elif 'Watch' in main_item.device.labels[0]:
			id_s = mon_config.STANDARD_REPAIR_OPTIONS['Apple Watch']
		else:
			id_s = mon_config.STANDARD_REPAIR_OPTIONS['MacBook']

		options = []
		for repair in main_item.repairs.labels:
			options.append(build.text_field_option(repair))

		if options:
			return options
		else:
			return [build.text_field_option("No Repairs Requested By Client")]

	basic = {
		"type": "modal",
		"callback_id": "parts_submit",
		"title": {
			"type": "plain_text",
			"text": "Repair Details",
			"emoji": True
		},
		"submit": {
			"type": "plain_text",
			"text": "Submit",
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
					"text": "You're All Done!",
					"emoji": True
				}
			},
			{
				"type": "context",
				"elements": [
					{
						"type": "mrkdwn",
						"text": "*Congrats* :partying_face: on completing the repair, just a few things:"
					}
				]
			},
			{
				"type": "header",
				"text": {
					"type": "plain_text",
					"text": "The client reported these faults:",
					"emoji": True
				}
			},
			{
				"type": "section",
				"fields": _generate_faults_list()
			},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "Please select the parts you used to resolve these faults:"
				},
				"accessory": {
					"type": "checkboxes",
					"options": _generate_parts_options_list(),
					"action_id": "checkboxes-action"
				}
			},
			{
				"type": "input",
				"dispatch_action": True,
				"label": {
					"type": "plain_text",
					"text": "Did you damage any parts during the repair?",
					"emoji": True
				},
				"element": {
					"type": "static_select",
					"placeholder": {
						"type": "plain_text",
						"text": "Don't lie...",
						"emoji": True
					},
					"options": [
						{
							"text": {
								"type": "plain_text",
								"text": "Nope, a perfect repair 😏",
								"emoji": True
							},
							"value": "no"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "...I had a little accident 😳",
								"emoji": True
							},
							"value": "yes"
						}
					],
					"action_id": "waste_opt_in"
				}
			}
		]
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

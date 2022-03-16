import datetime
import json


def _convert_monday_time_to_string(monday_date_column):
	if monday_date_column.date:
		date_s = monday_date_column.date.split("-")
		time_s = monday_date_column.time

		date = datetime.datetime(year=date_s[0], month=date_s[1], day=date_s[2]).strftime("%a %d %b %Y")
		if time_s:
			date = date + ": " + time_s
		return date
	else:
		return "Not Provided (This Shouldn't Happen)"


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
		"external_id": "pre_repair_info",
		"title": {
			"type": "plain_text",
			"text": f"Repair: {item_id}",
			"emoji": True
		},
		"private_metadata": json.dumps({
			'main_id': item_id
		}),
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
						"text": f"Requested Repairs: {repairs_string}",
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
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "Click here to begin the repair   -->"
				},
				"accessory": {
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Begin",
						"emoji": True
					},
					"style": "primary",
					"value": item_id,
					"action_id": "begin-repair-button-confirm"
				}
			}
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
						"text": f"{repairs_string}",
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
					"action_id": "plain_text_input-action"
				},
				"label": {
					"type": "plain_text",
					"text": "Repair Notes",
					"emoji": True
				}
			},
			{
				"type": "input",
				'optional': False,
				"element": {
					"type": "static_select",
					"placeholder": {
						"type": "plain_text",
						"text": "What's happening with the repair?",
						"emoji": True
					},
					"options": [
						{
							"text": {
								"type": "plain_text",
								"text": "Repair Completed! Next!",
								"emoji": True
							},
							"value": "value-0"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "Cannot Complete - Need More Information",
								"emoji": True
							},
							"value": "value-1"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "Urgent Repair Request Received (Pause current repair)",
								"emoji": True
							},
							"value": "value-2"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "I've Got a Different Issue",
								"emoji": True
							},
							"value": "value-2"
						}
					],
					"action_id": "static_select-action"
				},
				"label": {
					"type": "plain_text",
					"text": "Repair Result",
					"emoji": True
				}
			}
		]
	}
	return basic

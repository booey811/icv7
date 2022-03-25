import datetime
import json
from pprint import pprint as p

import data
from . import helper, config
from application import mon_config, BaseItem, EricTicket


def add_divider_block(blocks):
	blocks.append({"type": "divider"})
	return blocks


def add_header_block(blocks, text):
	blocks.append({
		"type": "header",
		"text": {
			"type": "plain_text",
			"text": text,
			"emoji": True
		}
	})
	return blocks


def add_dropdown_ui(title, placeholder, options, blocks, block_id, selection_action_id):
	def get_option(text):
		option = {
			"text": {
				"type": "plain_text",
				"text": text,
				"emoji": True
			},
			"value": text
		}
		return option

	slack_options = []
	for option in options:
		slack_options.append(get_option(option))

	basic = {
		"type": "section",
		"block_id": block_id,
		"text": {
			"type": "mrkdwn",
			"text": title
		},
		"accessory": {
			"type": "static_select",
			"placeholder": {
				"type": "plain_text",
				"text": placeholder,
				"emoji": True
			},
			"options": slack_options,
			"action_id": selection_action_id
		}
	}
	blocks.append(basic)
	return blocks


def add_multiline_text_input(title, placeholder, block_id, action_id, blocks):
	basic = {
		"type": "input",
		"block_id": block_id,
		"element": {
			"type": "plain_text_input",
			"multiline": True,
			"action_id": action_id,
			"placeholder": {
				"type": "plain_text",
				"text": placeholder
			},
		},
		"label": {
			"type": "plain_text",
			"text": title,
			"emoji": True
		}
	}

	blocks.append(basic)
	return blocks


def add_radio_buttons_ui(title, block_id, action_id, options, blocks):
	def get_option(text):
		return {
			"text": {
				"type": "plain_text",
				"text": text,
				"emoji": True
			},
			"value": text
		}

	options = [get_option(item) for item in options]

	basic = {
		"type": "section",
		"block_id": block_id,
		"text": {
			"type": "mrkdwn",
			"text": f"*{title}*"
		},
		"accessory": {
			"type": "radio_buttons",
			"options": options,
			"action_id": action_id
		}
	}

	blocks.append(basic)
	return blocks


def add_book_new_repair_button(blocks):
	blocks.append({
		"type": "section",
		"text": {
			"type": "mrkdwn",
			"text": "Want to add a new repair? Click here  :point_right:"
		},
		"accessory": {
			"type": "button",
			"text": {
				"type": "plain_text",
				"text": ":iphone: New Repair",
				"emoji": True
			},
			"value": "no_value_needed",
			"action_id": "new_repair"
		}
	})
	return blocks


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


def loading(footnotes='', external_id=False):
	"""returns the view for the modal screen showing that the application has received a request and is processing it
	adds in a footnote to the loading screen for more specific information"""
	view = {
		"type": "modal",
		"title": {
			"type": "plain_text",
			"text": "Processing",
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

	if external_id:
		view["external_id"] = external_id

	return view


def stock_check_flow_maker(body, initial=False, get_level=None, fetching_stock_levels=False, repair_not_found=False):
	if get_level is None:
		get_level = []

	def get_base_modal_view():
		return {
			"type": "modal",
			"private_metadata": json.dumps(metadata),
			"title": {
				"type": "plain_text",
				"text": "Stock Checker",
				"emoji": True
			},
			"submit": {
				"type": "plain_text",
				"text": "Cancel",
				"emoji": True
			},
			"blocks": []
		}

	def add_device_type_options(blocks):
		blocks.append({
			"type": "input",
			"block_id": "stock_device_type",
			"dispatch_action": True,
			"element": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select a type",
					"emoji": True
				},
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "iPhone",
							"emoji": True
						},
						"value": "iPhone"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "iPad",
							"emoji": True
						},
						"value": "iPad"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "MacBook",
							"emoji": True
						},
						"value": "MacBook"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Apple Watch",
							"emoji": True
						},
						"value": "Apple Watch"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Other",
							"emoji": True
						},
						"value": "Other"
					}
				],
				"action_id": "stock_device_type"
			},
			"label": {
				"type": "plain_text",
				"text": "Device Type",
				"emoji": True
			}
		})

	def add_device_options(blocks):

		def get_device_options():

			selection = metadata["extra"]['device_type']

			options = []

			for item in data.MAIN_DEVICE:
				if selection in item:
					options.append({
						"text": {
							"type": "plain_text",
							"text": item,
							"emoji": True
						},
						"value": item
					})
			return options

		blocks.append({
			"type": "input",
			"dispatch_action": True,
			"block_id": "stock_device",
			"element": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select a device",
					"emoji": True
				},
				"options": get_device_options(),
				"action_id": "select_stock_device"
			},
			"label": {
				"type": "plain_text",
				"text": "Device",
				"emoji": True
			}
		})

		return blocks

	def add_repair_options(blocks):

		def get_repair_options():
			options = []

			for repair in config.PART_SELECTION_OPTIONS[metadata['extra']['device_type']]:
				options.append({
					"text": {
						"type": "plain_text",
						"text": repair,
						"emoji": True
					},
					"value": repair
				})
			return options

		blocks.append({
			"type": "input",
			"dispatch_action": True,
			"block_id": "stock_repair",
			"element": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select a repair",
					"emoji": True
				},
				"options": get_repair_options(),
				"action_id": "select_stock_repair"
			},
			"label": {
				"type": "plain_text",
				"text": "Repair",
				"emoji": True
			}
		})

		return blocks

	def add_stock_level_block(blocks, repair_info: list):

		try:
			stock_level = int(float(repair_info[1]))
		except ValueError:
			stock_level = 0

		if stock_level < 1:
			text = f"{repair_info[0]}: {stock_level} | :no_entry_sign: NO STOCK"
		else:
			text = f"{repair_info[0]}: {stock_level} | :tada: STOCK AVAILABLE"

		blocks.append({
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": text
			}
		})
		return blocks

	def add_micro_loader(blocks):

		text = "Fetching Stock Level Info - This Can Take A While"

		blocks.append({
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": text
			}
		})
		return blocks

	def add_no_results_block(blocks):
		blocks.append({
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f":cry: I couldn't find the stock level for this repair"
			}
		})
		return blocks

	metadata = helper.get_metadata(body)

	# check if this was initiated by a command, meaning its the entry point
	if initial:
		view = get_base_modal_view()
		add_device_type_options(view['blocks'])
		return view

	elif get_level:
		chosen = body['actions'][0]['selected_option']['value']
		view = get_base_modal_view()
		add_device_type_options(view['blocks'])
		add_device_options(view['blocks'])
		add_repair_options(view['blocks'])
		add_divider_block(view["blocks"])
		add_stock_level_block(view['blocks'], get_level)

	elif fetching_stock_levels:
		view = get_base_modal_view()
		add_device_type_options(view['blocks'])
		add_device_options(view['blocks'])
		add_repair_options(view['blocks'])
		add_divider_block(view["blocks"])
		add_micro_loader(view['blocks'])

	elif repair_not_found:
		view = get_base_modal_view()
		add_device_type_options(view['blocks'])
		add_device_options(view['blocks'])
		add_repair_options(view['blocks'])
		add_divider_block(view["blocks"])
		add_no_results_block(view['blocks'])

	else:
		phase = body['actions'][0]['action_id']
		chosen = body['actions'][0]['selected_option']['value']
		# check the body for the action id to work out point in flow
		if phase == 'stock_device_type':
			metadata['extra']['device_type'] = chosen.strip()
			view = get_base_modal_view()
			add_device_type_options(view['blocks'])
			add_device_options(view['blocks'])
		elif phase == "select_stock_device":
			metadata['extra']['device'] = chosen.strip()
			view = get_base_modal_view()
			add_device_type_options(view['blocks'])
			add_device_options(view['blocks'])
			add_repair_options(view['blocks'])
		elif phase == 'select_stock_repair':
			metadata['extra']['repair'] = chosen.strip()
			view = get_base_modal_view()
			add_device_type_options(view['blocks'])
			add_device_options(view['blocks'])
			add_repair_options(view['blocks'])
		else:
			raise Exception(f"encountered weird choice for phase in stock checker: {phase}")

	return view


def bookings_search_input(body, invalid_search=False):
	def add_book_new_repair_button(blocks):
		blocks.append({
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Want to add a new repair? Click here  :point_right:"
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": ":iphone: New Repair",
					"emoji": True
				},
				"value": "no_value_needed",
				"action_id": "new_repair"
			}
		})

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

	add_book_new_repair_button(search['blocks'])

	return search


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
			"text": "Todays Repairs",
			"emoji": True
		},
		"close": {
			"type": "plain_text",
			"text": "Cancel",
			"emoji": True
		},
		"blocks": generate_results_blocks(bookings)
	}

	add_divider_block(view['blocks'])
	add_divider_block(view['blocks'])

	add_book_new_repair_button(view["blocks"])

	return view


def walkin_booking_info(body, zen_user=None, phase="init", monday_item: BaseItem = None, ticket: EricTicket = None):
	class UpdateComplete(Exception):
		pass

	def get_base_modal():
		external_id = helper.create_external_view_id(body, "walk_in_info")
		metadata['external_id'] = external_id
		return {
			"title": {
				"type": "plain_text",
				"text": "Repair Information",
				"emoji": True
			},
			"submit": {
				"type": "plain_text",
				"text": "Accept Walk-In",
				"emoji": True
			},
			"type": "modal",
			"callback_id": "walkin_acceptance_submission",
			"external_id": external_id,
			"close": {
				"type": "plain_text",
				"text": "Cancel",
				"emoji": True
			},
			"blocks": []
		}

	def add_header(title, blocks):
		blocks.append({
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": title,
				"emoji": True
			}
		})
		return blocks

	def add_plain_line(text, blocks, block_id=''):
		block = {
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": text,
				"emoji": True
			}
		}
		if block_id:
			block["block_id"] = block
		blocks.append(block)
		return blocks

	def add_combined_line(title, value, blocks):
		blocks += [
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": f"*{title}*"
				}
			},
			{
				"type": "context",
				"elements": [
					{
						"type": "mrkdwn",
						"text": f"{value}"
					}
				]
			}
		]
		return blocks

	def add_client_info(blocks):

		if zen_user:
			name = zen_user.name
			email = zen_user.email
			phone = zen_user.phone
		else:
			name = metadata["zendesk"]["user"]["name"]
			email = metadata["zendesk"]["user"]["email"]
			phone = metadata["zendesk"]["user"]["phone"]

		if not name:
			name = "Somehow, we don't have a name for this client's account"
		if not email:
			email = "Somehow, we don't have an email address associated with this account"
		if not phone:
			phone = "No Phone Number Know, please acquire one"

		to_add = []
		add_plain_line(f"{name}", to_add)
		add_plain_line(email, to_add)
		add_plain_line(phone, to_add)
		add_divider_block(to_add)
		blocks += to_add
		return blocks

	def add_client_repair_data(blocks):
		# report client provided data back to the view
		if monday_item:
			device_str = monday_item.device.labels[0]
			repairs_str = ", ".join(monday_item.repairs.labels)
		else:
			device_str = metadata["device"]["model"]
			repairs_str = ", ".join(metadata["repairs"]["labels"])

		if not repairs_str:
			repairs_str = "Unconfirmed - Please confirm"

		if not device_str:
			device_str = "Unconfirmed - Please confirm with the client"

		to_add = []
		add_combined_line("Device", device_str, to_add)
		add_combined_line("Requested Repairs", repairs_str, to_add)
		blocks += to_add
		return blocks

	metadata = helper.get_metadata(body)
	view = get_base_modal()

	try:

		if phase == "init":
			if ticket:
				metadata = helper.get_metadata(body, update=metadata, new_data_item=ticket)

			if zen_user:
				metadata = helper.get_metadata(body, update=metadata, new_data_item=zen_user)

			if monday_item:
				metadata = helper.get_metadata(body, update=metadata, new_data_item=monday_item)

		add_client_info(view['blocks'])
		add_client_repair_data(view["blocks"])

		add_header("Confirmations", view['blocks'])

		add_dropdown_ui(
			title="Device Type",
			placeholder="Select a device type",
			options=['iPhone', 'iPad', 'MacBook', 'Apple Watch', 'Other'],
			blocks=view['blocks'],
			block_id="select_device_type",
			selection_action_id='select_accept_device_type'
		)

		if phase == "init":
			raise UpdateComplete

		p(body)

		device_type = \
		body['view']['state']['values']['select_device_type']['select_accept_device_type']['selected_option']['value']

		add_dropdown_ui(
			title="Device",
			placeholder="Select device",
			options=[item for item in data.MAIN_DEVICE if device_type in item],
			blocks=view['blocks'],
			block_id="select_device",
			selection_action_id="select_accept_device"
		)

		if phase == "device_type":
			raise UpdateComplete

		device = body['view']['state']['values']['select_device']['select_accept_device']['selected_option']['value']

		add_radio_buttons_ui(
			title="Repair Type",
			block_id="select_repair_type",
			action_id="radio_accept_device",
			options=config.REPAIR_TYPES,
			blocks=view['blocks']
		)

		if phase == "device":
			raise UpdateComplete

		repair_type = body['view']['state']['values']['select_repair_type']['radio_accept_device']['selected_option'][
			'value']

		add_multiline_text_input(
			title="Repair Notes",
			placeholder='Got Catch Em All!..... The infos I mean',
			block_id="text_notes",
			action_id="text_accept_notes",
			blocks=view["blocks"]
		)

		if phase == "repair_type":
			raise UpdateComplete

	except UpdateComplete as e:
		view["private_metadata"] = json.dumps(metadata)
		p(view)
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


def user_search_request(body, zenpy_results=None, research=False):
	if not zenpy_results:
		zenpy_results = []

	def add_base_modal():

		external_id = helper.create_external_view_id(body, "user_search")
		metadata['external_id'] = external_id

		return {
			"type": "modal",
			"private_metadata": json.dumps(metadata),
			"external_id": external_id,
			"title": {
				"type": "plain_text",
				"text": "User Search",
				"emoji": True
			},
			"submit": {
				"type": "plain_text",
				"text": "Cancel",
				"emoji": True
			},
			"blocks": []
		}

	def add_search_input(blocks):
		blocks.append({
			"dispatch_action": True,
			"type": "input",
			"block_id": "text_input_user_search",
			"element": {
				"type": "plain_text_input",
				"action_id": "user_search"
			},
			"label": {
				"type": "plain_text",
				"text": "User Search",
				"emoji": True
			}
		})
		return blocks

	def add_results_blocks(blocks, zenpy_search_object):

		add_divider_block(blocks)

		def add_name_and_button(username, zendesk_id, blocks):
			blocks.append({
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": str(username),
				},
				"accessory": {
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Select User",
						"emoji": True
					},
					"value": str(zendesk_id),
					"action_id": "new_walkin_repair"
				}
			})
			return blocks

		def add_context_lines(email, phone, blocks):

			if not email:
				email = "looks like we're missing this data"

			if not phone:
				phone = "looks like we're missing this data"

			blocks.append({
				"type": "context",
				"elements": [
					{
						"type": "mrkdwn",
						"text": f"*Email*: {str(email)}"
					},
					{
						"type": "mrkdwn",
						"text": f"*Phone*: {str(phone)}"
					}
				]
			})

			return blocks

		for user in zenpy_search_object:
			add_name_and_button(user.name, user.id, blocks)
			add_context_lines(user.email, user.phone, blocks)
			add_divider_block(blocks)

		return blocks

	def add_failed_user_addition(blocks):
		add_header_block(blocks, f"Sorry, we found {len(zenpy_results)} users with this search:")

	def add_new_user_button(blocks, no_users_found=False):

		if no_users_found:
			text = "No users Found with this search term - create one?"
		else:
			text = "Can't find the person you're looking for?  :point_right:"

		blocks.append({
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": text
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": ":new:   New User",
					"emoji": True
				},
				"value": "no_value_needed",
				"action_id": "button_new_user"
			}
		})
		return blocks

	def add_failed_search_block(blocks):

		blocks += [
			{
				"type": "header",
				"text": {
					"type": "plain_text",
					"text": "We found too many results there",
					"emoji": True
				}
			},
			{
				"type": "context",
				"elements": [
					{
						"type": "plain_text",
						"text": "Please try to be a little more specific (email addresses work brilliantly!)",
						"emoji": True
					}
				]
			}
		]
		return blocks

	metadata = helper.get_metadata(body)

	view = add_base_modal()
	add_search_input(view['blocks'])

	no_user_found = False
	if len(zenpy_results) == 0:
		no_user_found = True
	elif len(zenpy_results) < 25:
		add_results_blocks(view['blocks'], zenpy_search_object=zenpy_results)
		add_divider_block(view['blocks'])
	elif len(zenpy_results) > 24:
		add_failed_search_block(view['blocks'])
	else:
		raise Exception(f"Mathematically Impossible Number of Zendesk Search Results {len(zenpy_results)}")

	add_divider_block(view['blocks'])
	add_new_user_button(view["blocks"], no_users_found=no_user_found)

	# metadata = helper.get_metadata(body)
	# if not metadata["views"]["user_search"]:
	# 	try:
	# 		metadata["views"]["user_search"] = body["view"]["id"]
	# 	except KeyError:
	# 		print("Cannot Gt View ID from Response Body")
	#
	# view = add_base_modal()
	# add_search_input(view['blocks'])
	#
	# if initial:
	# 	pass
	# else:
	# 	if failed_addition:
	# 		add_failed_user_addition(view['blocks'])
	# 	add_results_block(view['blocks'], zenpy_search_object=zenpy_results)
	# 	add_divider_block(view['blocks'])

	return view


def new_user_form(body):
	def get_base_modal():
		external_id = helper.create_external_view_id(body, "new_user_input")
		metadata['external_id'] = external_id

		return {
			"type": "modal",
			"callback_id": "new_user_input",
			"private_metadata": json.dumps(metadata),
			"external_id": external_id,
			"title": {
				"type": "plain_text",
				"text": "Add New User",
				"emoji": True
			},
			"submit": {
				"type": "plain_text",
				"text": "Add User",
				"emoji": True
			},
			"close": {
				"type": "plain_text",
				"text": "Cancel",
				"emoji": True
			},
			"blocks": []}

	def add_input_blocks(blocks):
		blocks += [
			{
				"type": "input",
				"block_id": "new_user_name",
				"optional": False,
				"element": {
					"type": "plain_text_input",
					"action_id": "plain_text_input-action"
				},
				"label": {
					"type": "plain_text",
					"text": "First Name",
					"emoji": True
				}
			},
			{
				"type": "input",
				"block_id": "new_user_surname",
				"optional": False,
				"element": {
					"type": "plain_text_input",
					"action_id": "plain_text_input-action"
				},
				"label": {
					"type": "plain_text",
					"text": "Surname",
					"emoji": True
				}
			},
			{
				"type": "input",
				"block_id": "new_user_email",
				"optional": False,
				"element": {
					"type": "plain_text_input",
					"action_id": "plain_text_input-action"
				},
				"label": {
					"type": "plain_text",
					"text": "Email Address",
					"emoji": True
				}
			},
			{
				"type": "input",
				"block_id": "new_user_phone",
				"element": {
					"type": "plain_text_input",
					"action_id": "plain_text_input-action"
				},
				"label": {
					"type": "plain_text",
					"text": "Phone Number",
					"emoji": True
				}
			}
		]

	metadata = helper.get_metadata(body)

	view = get_base_modal()
	add_input_blocks(view['blocks'])

	return view


def new_user_result_view(body, zendesk_user):
	def get_base_modal():
		return {
			"type": "modal",
			"private_metadata": json.dumps(metadata),
			"callback_id": "new_user_walkin_submission",
			"title": {
				"type": "plain_text",
				"text": "Create New User",
				"emoji": True
			},
			"submit": {
				"type": "plain_text",
				"text": "Create New Repair",
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
						"text": "User Created",
						"emoji": True
					}
				}
			]
		}

	def add_attribute_block(blocks):

		def get_blocks(attribute, val):
			return [{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": f"*{attribute}*"
				}
			},
				{
					"type": "context",
					"elements": [
						{
							"type": "mrkdwn",
							"text": str(val)
						}
					]
				}]

		info = {
			"name": zendesk_user.name,
			"email": zendesk_user.email,
			"phone": zendesk_user.phone
		}

		for att in info:
			if info[att]:
				blocks += get_blocks(att, info[att])

		return blocks

	metadata = helper.get_metadata(body)
	metadata = helper.get_metadata(body, update=metadata, new_data_item=zendesk_user)

	view = get_base_modal()
	add_attribute_block(view["blocks"])

	return view


def failed_new_user_creation_view(email, no_of_results, failed_to_create=False):
	def get_base_modal():

		if failed_to_create:
			base = {
				"type": "modal",
				"callback_id": "user_creation_failed",
				"title": {
					"type": "plain_text",
					"text": "Create New User",
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
							"text": "Could Not Create User",
							"emoji": True
						}
					},
					{
						"type": "section",
						"text": {
							"type": "mrkdwn",
							"text": f"An error occurred while adding this user to Zendesk: {str(failed_to_create)}"
						}
					},
					{
						"type": "context",
						"elements": [
							{
								"type": "mrkdwn",
								"text": "Please return to search and use this email address to find the user"
							}
						]
					}
				]
			}

		else:

			base = {
				"type": "modal",
				"callback_id": "user_already_exists",
				"title": {
					"type": "plain_text",
					"text": "Create New User",
					"emoji": True
				},
				"close": {
					"type": "plain_text",
					"text": "Return to Search",
					"emoji": True
				},
				"blocks": [
					{
						"type": "header",
						"text": {
							"type": "plain_text",
							"text": "Too Many Results Found",
							"emoji": True
						}
					},
					{
						"type": "section",
						"text": {
							"type": "mrkdwn",
							"text": f"We found {no_of_results} users with email address {email}"
						}
					},
					{
						"type": "context",
						"elements": [
							{
								"type": "mrkdwn",
								"text": "Please return to search and use this email address to find the user"
							}
						]
					}
				]
			}

		return base

	view = get_base_modal()
	return view


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

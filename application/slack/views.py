import datetime
import json
from pprint import pprint as p

import data
from . import helper, config, exceptions
from application import mon_config, BaseItem, EricTicket, clients


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


def add_context_block(blocks, text):
	basic = {
		"type": "context",
		"elements": [
			{
				"type": "mrkdwn",
				"text": text
			}
		]
	}

	blocks.append(basic)
	return blocks


def add_dropdown_ui_section(title, placeholder, options, blocks, block_id, selection_action_id):
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


def add_dropdown_ui_input(title, placeholder, options, blocks, block_id, optional=False, action_id=None,
                          dispatch_action=False):
	def get_options():
		results = []
		for text_and_value in options:
			results.append({
				"text": {
					"type": "plain_text",
					"text": text_and_value[0],
					"emoji": True
				},
				"value": text_and_value[1]
			})
		return results

	basic = {
		"type": "input",
		"block_id": block_id,
		"element": {
			"type": "static_select",
			"placeholder": {
				"type": "plain_text",
				"text": placeholder,
				"emoji": True
			},
			"options": get_options(),
			"action_id": action_id
		},
		"label": {
			"type": "plain_text",
			"text": title,
			"emoji": True
		}
	}

	if optional:
		basic["optional"] = True

	if action_id:
		basic["element"]["action_id"] = action_id

	if dispatch_action:
		basic["dispatch_action"] = True

	blocks.append(basic)
	return blocks


def add_multiline_text_input(title, placeholder, block_id, blocks, action_id='', optional=False):
	basic = {
		"type": "input",
		"optional": optional,
		"block_id": block_id,
		"element": {
			"type": "plain_text_input",
			"multiline": True,
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

	if action_id:
		basic["element"]["action_id"] = action_id

	blocks.append(basic)
	return blocks


def add_single_text_input(title, placeholder, block_id, action_id, blocks, optional=True):
	basic = {
		"type": "input",
		"block_id": block_id,
		"optional": optional,
		"element": {
			"type": "plain_text_input",
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


def add_radio_buttons_input_version(title, block_id, options, blocks, optional=True, action_id=None):
	def get_options():

		result = []

		for option in options:
			option_title = option[0]
			option_value = option[1]

			result.append({
				"text": {
					"type": "plain_text",
					"text": option_title,
					"emoji": True
				},
				"value": option_value
			})

		return result

	basic = {
		"type": "input",
		"block_id": block_id,
		"optional": optional,
		"element": {
			"type": "radio_buttons",
			"options": get_options(),
		},
		"label": {
			"type": "plain_text",
			"text": title,
			"emoji": True
		}
	}

	if action_id:
		basic["element"]["action_id"] = action_id

	blocks.append(basic)

	return blocks


def add_button_section(title, button_text, button_value, block_id, action_id, blocks):
	view = {
		"type": "section",
		"block_id": block_id,
		"text": {
			"type": "mrkdwn",
			"text": title
		},
		"accessory": {
			"type": "button",
			"text": {
				"type": "plain_text",
				"text": button_text,
				"emoji": True
			},
			"value": button_value,
			"action_id": action_id
		}
	}

	blocks.append(view)
	return blocks


def add_checkbox_section(title, options: list, block_id, action_id, blocks, optional=True):
	def get_options():
		results = []

		for text_and_value in options:
			results.append(
				{
					"text": {
						"type": "plain_text",
						"text": text_and_value[0],
						"emoji": True
					},
					"value": text_and_value[1]
				}
			)

		return results

	basic = {
		"type": "input",
		"block_id": block_id,
		"optional": optional,
		"element": {
			"type": "checkboxes",
			"options": get_options(),
			"action_id": action_id
		},
		"label": {
			"type": "plain_text",
			"text": title,
			"emoji": True
		}
	}

	blocks.append(basic)
	return blocks


def add_markdown_block(blocks, text):
	blocks.append(		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": text
			}
		})


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


def loading(footnotes='', external_id=False, metadata=None):
	"""returns the view for the modal screen showing that the application has received a request and is processing it
	adds in a footnote to the loading screen for more specific information"""
	if metadata is None:
		metadata = {}
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
		# noinspection PyTypeChecker
		view['blocks'].append(context)

	if external_id:
		view["external_id"] = external_id
		if metadata:
			metadata["external_id"] = external_id
			view["private_metadata"] = json.dumps(metadata)

	return view


def error(footnotes=''):
	view = {
		"type": "modal",
		"callback_id": "error_report",
		"title": {
			"type": "plain_text",
			"text": "Error Reporting",
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
					"text": "Uh Oh, We Ran Into A Problem",
					"emoji": True
				}
			}
		]
	}

	if footnotes:
		secondary = {
			"type": "context",
			"elements": [
				{
					"type": "mrkdwn",
					"text": footnotes
				}
			]
		}
		# noinspection PyTypeChecker
		view['blocks'].append(secondary)

	return view


def success(footnotes=''):
	view = {
		"type": "modal",
		"callback_id": "success_screen",
		"title": {
			"type": "plain_text",
			"text": "Success!",
			"emoji": True
		},
		"close": {
			"type": "plain_text",
			"text": "Close",
			"emoji": True
		},
		"blocks": [
			{
				"type": "header",
				"text": {
					"type": "plain_text",
					"text": "Operation Complete! Yay!",
					"emoji": True
				}
			}
		]
	}

	if footnotes:
		secondary = {
			"type": "context",
			"elements": [
				{
					"type": "mrkdwn",
					"text": footnotes
				}
			]
		}
		# noinspection PyTypeChecker
		view['blocks'].append(secondary)

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
			# "submit": {
			# 	"type": "plain_text",
			# 	"text": "Cancel",
			# 	"emoji": True
			# },
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
							"text": "Other Device",
							"emoji": True
						},
						"value": "Other Device"
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

	def add_device_options(blocks, devices_list):

		def get_device_options():
			options = []

			for device in devices_list:
				options.append({
					"text": {
						"type": "plain_text",
						"text": device.info["display_name"],
						"emoji": True
					},
					"value": device.info["eric_id"]
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

	def add_repair_options(device_object: data.DeviceRepairsObject, blocks):

		def query_monday_for_products(device_name: str):

			try:
				group_id = str(data.PRODUCT_GROUPS[device_name])
			except KeyError:
				raise exceptions.ProductGroupNameError(device_name)

			options = clients.monday.system.get_boards(
				"id",
				"groups.items.[id, name]",
				ids=[2477699024],
				groups={"ids": [group_id]}
			)[0].groups[0].items
			return options

		def get_repair_options():
			repairs_info = device_object.get_slack_repair_options_data()
			options = []
			for repair in repairs_info:
				options.append({
					"text": {
						"type": "plain_text",
						"text": repair["name"],
						"emoji": True
					},
					"value": repair["repair_obj_id"]
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

	def add_stock_level_block(blocks, parts_list: list):
		for repair_info in parts_list:
			# try:
			level = repair_info[1]
			if not level:
				level = 0
			stock_level = int(float(level))
			# except (ValueError, AttributeError):
			# 	stock_level = 0

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
		add_device_options(view['blocks'], data.DEVICE_TYPES[metadata["extra"]["device_type"]])
		add_repair_options(getattr(data.repairs, metadata["device"]["eric_id"]), view['blocks'])
		add_divider_block(view["blocks"])
		add_stock_level_block(view['blocks'], get_level)

	elif fetching_stock_levels:
		view = get_base_modal_view()
		add_device_type_options(view['blocks'])
		add_device_options(view['blocks'], data.DEVICE_TYPES[metadata["extra"]["device_type"]])
		add_repair_options(getattr(data.repairs, metadata["device"]["eric_id"]), view['blocks'])
		add_divider_block(view["blocks"])
		add_micro_loader(view['blocks'])

	elif repair_not_found:
		view = get_base_modal_view()
		add_device_type_options(view['blocks'])
		add_device_options(view['blocks'], data.DEVICE_TYPES[metadata["extra"]["device_type"]])
		add_repair_options(getattr(data.repairs, metadata["device"]["eric_id"]), view['blocks'])
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
			add_device_options(view['blocks'], data.DEVICE_TYPES[chosen])
		elif phase == "select_stock_device":
			device = getattr(data.repairs, chosen)
			metadata["device"]["model"] = device.info["device_type"]
			metadata["device"]["eric_id"] = device.info["eric_id"]
			view = get_base_modal_view()
			add_device_type_options(view['blocks'])
			add_device_options(view['blocks'], data.DEVICE_TYPES[metadata['extra']['device_type']])
			add_repair_options(device, view['blocks'])
		elif phase == 'select_stock_repair':
			metadata['repairs']['eric_ids'].append(chosen.strip())
			view = get_base_modal_view()
			add_device_type_options(view['blocks'])
			add_device_options(view['blocks'], data.DEVICE_TYPES[chosen])
			add_repair_options(device_object=getattr(data.repairs, metadata["device"]["eric_id"]),
			                   blocks=view['blocks'])
		else:
			raise Exception(f"encountered weird choice for phase in stock checker: {phase}")

	view["private_metadata"] = json.dumps(metadata)
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

	# add_book_new_repair_button(search['blocks'])

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
			try:
				device_str = monday_item.device.labels[0]
			except IndexError:
				device_str = "Unconfirmed"
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
			if monday_item:
				metadata = helper.get_metadata(body, update=metadata, new_data_item=monday_item)
			if zen_user:
				metadata = helper.get_metadata(body, update=metadata, new_data_item=zen_user)

		add_client_info(view['blocks'])
		add_client_repair_data(view["blocks"])

		add_header("Confirmations", view['blocks'])

		add_dropdown_ui_section(
			title="Device Type",
			placeholder="Select a device type",
			options=['iPhone', 'iPad', 'MacBook', 'Apple Watch', 'Other'],
			blocks=view['blocks'],
			block_id="select_device_type",
			selection_action_id='select_accept_device_type'
		)

		if phase == "init":
			raise UpdateComplete

		device_type = \
			body['view']['state']['values']['select_device_type']['select_accept_device_type']['selected_option'][
				'value']

		add_dropdown_ui_section(
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
			options=[item for item in config.REPAIR_TYPES],
			blocks=view['blocks']
		)

		if phase == "device":
			raise UpdateComplete

		repair_type = body['view']['state']['values']['select_repair_type']['radio_accept_device']['selected_option'][
			'value']

		add_multiline_text_input(
			title="Repair Notes",
			placeholder='Gotta Catch Em All!..... The infos I mean',
			block_id="text_notes",
			action_id="text_accept_notes",
			blocks=view["blocks"]
		)

		if repair_type == "Diagnostic":
			pc_optional = False
		else:
			pc_optional = True

		add_single_text_input(
			title="Passcode",
			placeholder="Passcode is required for ALL diagnostics",
			block_id='text_pc',
			action_id="text_accept_pc",
			blocks=view["blocks"],
			optional=pc_optional
		)

		if phase == "repair_type":
			raise UpdateComplete

	except UpdateComplete as e:
		view["private_metadata"] = json.dumps(metadata)
		return view


def pre_repair_info(main_item, resp_body):

	def get_base_modal(title):
		if len(title) > 20:
			title = title[:20]
		basic = {
			"type": "modal",
			"callback_id": "pre_repair_info",
			"title": {
				"type": "plain_text",
				"text": title,
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
			"blocks": []
		}
		return basic

	repair_type = main_item.repair_type.label
	try:
		device_label = main_item.device.labels[0]
	except IndexError:
		device_label = "Unconfirmed"
	repairs_string = ", ".join(main_item.repairs.labels)
	if not repairs_string:
		repairs_string = 'No Repairs Requested'

	metadata = helper.get_metadata(resp_body)
	metadata['main'] = main_item.mon_id
	metadata["general"]["repair_type"] = repair_type
	metadata["extra"]["client_repairs"] = repairs_string
	helper.add_device_type_metadata(main_item, metadata)

	view = get_base_modal(main_item.name)
	add_header_block(view['blocks'], f"{device_label}  |  {repair_type}")

	if repair_type == "Repair":
		add_markdown_block(view["blocks"], "Repairs Requested:")
		add_context_block(view["blocks"], repairs_string)
		add_divider_block(view["blocks"])
		add_markdown_block(view["blocks"], ":thumbsup:  Please complete the requested repairs")
	elif repair_type == "Diagnostic":
		add_markdown_block(view["blocks"], ":nerd_face:  Please diagnose the device, paying attention to the following parts:")
		add_context_block(view["blocks"], repairs_string)
	else:
		view = error(f"A Repair Has Been Submitted with an Unknown Repair Type: {repair_type}\nPlease let Gabe know")

	view["private_metadata"] = json.dumps(metadata)
	return view


def repair_phase_view(main_item, body, external_id):

	def get_base_modal(title):
		if len(title) > 20:
			title = title[:20]
		basic = {
			"type": "modal",
			"callback_id": "repair_phase_ended",
			"external_id": external_id,
			"notify_on_close": True,
			"title": {
				"type": "plain_text",
				"text": title,
				"emoji": True
			},
			"submit": {
				"type": "plain_text",
				"text": "Finalise Repair",
				"emoji": True
			},
			"close": {
				"type": "plain_text",
				"text": "Cancel",
				"emoji": True
			},
			"blocks": []
		}
		return basic

	item_id = main_item.mon_id

	try:
		device = main_item.device.labels[0]
	except IndexError:
		device = "Unconfirmed Device (this is bad)"
	repair_type = main_item.repair_type.label
	start_time = datetime.datetime.now().strftime("%X")
	pc = main_item.passcode.value
	if not pc:
		pc = "No Access Granted :white_frowning_face:"
	intake_notes = main_item.intake_notes.value
	if not intake_notes:
		intake_notes = ":sob:  None Taken"

	metadata = helper.get_metadata(body)
	metadata["device"]["model"] = device
	metadata["general"]["repair_type"] = repair_type
	view = get_base_modal(f"{main_item.name}")

	add_header_block(view['blocks'], f"{device}  |  {repair_type}")
	add_divider_block(view["blocks"])
	add_markdown_block(view["blocks"], _get_repairs_string(main_item))
	add_context_block(view["blocks"], pc)
	add_divider_block(view["blocks"])
	add_header_block(view["blocks"], "Client Notes:")
	add_markdown_block(view['blocks'], intake_notes)
	add_divider_block(view["blocks"])

	dropdown_options = []
	if repair_type == "Repair":
		dropdown_options = [[":ok_hand:  The repair has been completed", "repaired"]]
	elif repair_type == "Diagnostic":
		dropdown_options = [[":gear:  I've finished the diagnostic", "diagnosed"]]
	else:
		raise Exception(f"Unrecognised Repair Type: {repair_type}")

	dropdown_options += [
			[":eyes:  I've received a more urgent repair request", "urgent"],
			[":warning:  I can't complete this repair", "client"],
		]

	add_multiline_text_input(
		title="Repair Notes",
		placeholder="Anything to add?",
		block_id="repair_notes",
		blocks=view["blocks"],
		optional=True,
		action_id="repair_notes"
	)

	add_dropdown_ui_input(
		title="Have you finished?",
		placeholder="Let us know what happened",
		options=dropdown_options,
		block_id="repair_result_select",
		blocks=view["blocks"],
		optional=False,
		action_id="repair_result_select"
	)

	view["private_metadata"] = json.dumps(metadata)
	return view


def repair_issue_form(body, more_info=False):

	def get_base_modal():
		basic = {
			"type": "modal",
			"callback_id": "repair_issue_submit",
			"notify_on_close": True,
			"title": {
				"type": "plain_text",
				"text": "Repair Issue Logger",
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
			"blocks": []
		}
		return basic

	metadata = helper.get_metadata(body)

	view = get_base_modal()

	options = [
		["Device Needs To Be Charged", 'charge'],
		["I Do Not Have The Required Parts", "parts"],
		["I Do Not Have The Correct Passcode", "passcode"],
		["Other", "other"]
	]

	add_dropdown_ui_input(
		title="Please Select An Option That Best Describes the Issue",
		placeholder="Your Choice!",
		options=options,
		blocks=view["blocks"],
		block_id="dropdown_repair_issue_selector",
		optional=False,
		action_id="dropdown_repair_issue_selector_action",
		dispatch_action=True
	)

	if more_info:
		add_multiline_text_input(
			title="Please explain your issue",
			placeholder="Does the client need a further repair? Is the passcode wrong?!",
			block_id="text_issue",
			action_id='text_issue_action',
			blocks=view["blocks"]
		)

	view["private_metadata"] = json.dumps(metadata)
	return view


def initial_parts_search_box(body, external_id, initial: bool, remove=False, diag=False):
	def get_base_modal():
		search = {
			'type': "modal",
			"callback_id": "repairs_parts_submission",
			"external_id": external_id,
			"notify_on_close": True,
			"title": {
				"type": "plain_text",
				"text": "Parts Selection",
				"emoji": True
			},
			"submit": {
				"type": "plain_text",
				"text": "Proceed",
				"emoji": True
			},
			"close": {
				"type": "plain_text",
				"text": "Go Back",
				"emoji": True
			},
			'blocks': []
		}
		return search

	def add_selected_parts_block(repair_data, blocks):

		add_button_section(
			title=repair_data["name"],
			button_text="Remove Part",
			button_value=repair_data["mon_id"],
			block_id=f"repairs_parts_remove_{repair_data['mon_id']}",
			action_id="repairs_parts_remove",
			blocks=blocks
		)

	def add_parts_list(repairs_data, blocks):
		for repair in repairs_data:
			if repair["mon_id"] in metadata["extra"]["selected_repairs"]:
				continue
			part_name = repair["name"].replace(metadata["device"]["model"], "")
			add_button_section(
				title=part_name,
				button_text="Add Part",
				button_value=repair["mon_id"],
				block_id=f"repairs_parts_select_{repair['mon_id']}",
				action_id='repairs_parts_select',
				blocks=blocks
			)

		return blocks

	metadata = helper.get_metadata(body)
	metadata["external_id"] = external_id

	try:
		data_repairs_id = data.PRODUCT_GROUPS[metadata["device"]["model"]]
	except KeyError:
		raise exceptions.DeviceProductNotFound(metadata["device"]["model"])
	metadata['device']['eric_id'] = data_repairs_id

	device_repairs = getattr(data.repairs, data_repairs_id)

	if not initial:
		selected_repair_id = body['actions'][0]["value"]
		if remove:
			metadata["extra"]["selected_repairs"].remove(selected_repair_id)
		else:
			metadata["extra"]["selected_repairs"].append(selected_repair_id)
	else:
		notes = body["view"]["state"]["values"]["repair_notes"]["repair_notes"]["value"]
		if notes:
			metadata["notes"] = notes + "\n\n"

	view = get_base_modal()
	if metadata["extra"]["selected_repairs"]:
		add_header_block(view["blocks"], "Selected Parts")
		for repair_id in metadata["extra"]["selected_repairs"]:
			for repair_info in device_repairs.get_slack_repair_options_data():
				if str(repair_id) == repair_info["mon_id"]:
					name = repair_info["name"].replace(metadata["device"]["model"], "")
					add_selected_parts_block(repair_info, view["blocks"])
		add_divider_block(view["blocks"])

	if diag:
		header = "Add Required Repairs"
	else:
		header = "Add Parts to Repair"

	add_header_block(view["blocks"], header)
	add_parts_list(device_repairs.get_slack_repair_options_data(), view["blocks"])

	view["private_metadata"] = json.dumps(metadata)

	return view


def sub_parts_confirmation(body):
	metadata = helper.get_metadata(body)

	requires_confirmation = []
	product_items = []
	if metadata["extra"]["selected_repairs"]:
		product_items = clients.monday.system.get_items(ids=metadata["extra"]["selected_repairs"])

	for product in product_items:
		part_ids = product.get_column_value("connect_boards8")
		if len(part_ids) == 1:
			metadata["parts"].append(part_ids[0])
			metadata["extra"]["selected_repairs"].remove(part_ids[0])
		elif len(part_ids) > 1:
			# requires clarification (push a selection view)
			requires_confirmation.append([product, part_ids])
		elif len(part_ids) == 0:
			# no parts connected to this product
			raise Exception(f"No Parts attached to {product.name} Product")
		else:
			raise Exception("Mathematically Impossible Thing Happened")

	if requires_confirmation:
		view = {
			"type": "modal",
			"title": {
				"type": "plain_text",
				"text": "Parts Confirmation",
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
			"blocks": []
		}

		add_header_block(view["blocks"], "Please confirm variations:")

		for product_data in requires_confirmation:
			options = []
			product = product_data[0]
			part_ids = product_data[1]
			parts = clients.monday.system.get_items('id', 'name', ids=part_ids)
			for part in parts:
				name = part.name
				value = part.id
				options.append([name, value])

			add_radio_buttons_input_version(
				title=product.name,
				block_id="repairs_sub_parts_select",
				options=options,
				blocks=view["blocks"],
				optional=False
			)

	else:
		pass


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


def display_variant_options(body, variant_dict, meta):
	def get_base_modal():
		basic = {
			"type": "modal",
			"callback_id": "variant_selection_submission",
			"private_metadata": json.dumps(metadata),
			"notify_on_close": True,
			"title": {
				"type": "plain_text",
				"text": "Variation Selection",
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
			"blocks": []
		}

		return basic

	metadata = meta
	view = get_base_modal()
	for repair in variant_dict:
		add_header_block(view["blocks"], repair)

		add_radio_buttons_input_version(
			title="Please select a part",
			block_id=f"variant_selection_{variant_dict[repair]['id']}",
			options=variant_dict[repair]['info'],
			optional=False,
			blocks=view['blocks'],
			action_id=f"radio_variant_selection_{variant_dict[repair]['id']}"
		)

	return view


def repair_completion_confirmation_view(body, from_variants, external_id='', meta=None):
	def get_base_modal():
		basic = {
			"type": "modal",
			"notify_on_close": True,
			"callback_id": "repair_completion_confirmation",
			"title": {
				"type": "plain_text",
				"text": "Confirming Your Work",
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
			"blocks": []
		}

		return basic

	metadata = meta

	if from_variants:
		for repair_id in metadata["extra"]["selected_repairs"]:
			part_id = \
				body["view"]["state"]["values"][f"variant_selection_{repair_id}"][
					f"radio_variant_selection_{repair_id}"][
					"selected_option"]["value"]
			metadata["parts"].append(part_id)
		metadata["extra"]["selected_repairs"] = []

	view = get_base_modal()

	text_and_values = [
		[item.name, item.name] for item in clients.monday.system.get_items('name', ids=metadata['parts'])
	]

	if metadata["general"]["repair_type"] == "Repair":

		add_header_block(view["blocks"], "The Client Requested the Following Repairs:")
		if not metadata["extra"]["client_repairs"]:
			add_context_block(view["blocks"], "No repairs explicitly requested")
		else:
			add_context_block(view["blocks"], metadata["extra"]["client_repairs"])
		add_divider_block(view['blocks'])
		add_header_block(view["blocks"], "To resolve these faults, you have used:")

		add_checkbox_section(
			title="Please confirm",
			options=text_and_values,
			block_id="checkbox_parts_confirmation",
			action_id="checkbox_parts_confirmation",
			blocks=view['blocks'],
			optional=False
		)

	elif metadata["general"]["repair_type"] == "Diagnostic":
		add_header_block(view["blocks"], "The Client Requires The Following:")
		for part in text_and_values:
			add_markdown_block(view["blocks"], part[0])

	add_divider_block(view["blocks"])
	add_divider_block(view["blocks"])

	add_multiline_text_input(
		title="Final Notes",
		optional=True,
		placeholder="If you have any final notes, put them here",
		block_id='text_final_repair_notes',
		action_id='text_final_repair_notes',
		blocks=view['blocks']
	)
	view["private_metadata"] = json.dumps(metadata)
	return view


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

	return view


def capture_waste_request(body, external_id):
	def get_base_modal():
		basic = {
			"type": "modal",
			"callback_id": "waste_opt_in",
			"external_id": external_id,
			"notify_on_close": True,
			"private_metadata": json.dumps(helper.get_metadata(body)),
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
			"blocks": []
		}
		return basic

	view = get_base_modal()
	options = [["No Parts To Waste", "no_waste"], ["I've Damaged Stock", "waste"]]
	add_dropdown_ui_input(
		title="Do You Need to Record Waste?",
		placeholder="It's OK if you do!",
		options=options,
		blocks=view["blocks"],
		block_id="waste_opt_in",
		optional=False,
		action_id="waste_opt_in_action"
	)
	return view


def register_wasted_parts(body, initial, remove, external_id):
	def add_base_modal():
		basic = {
			"type": "modal",
			"external_id": external_id,
			"callback_id": "waste_parts_submission",
			"notify_on_close": True,
			"title": {
				"type": "plain_text",
				"text": "Record Waste",
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
			"blocks": []
		}
		return basic

	metadata = helper.get_metadata(body)
	metadata["external_id"] = external_id

	device_repairs_obj = getattr(data.repairs, metadata["device"]["eric_id"])
	repairs_info = device_repairs_obj.get_slack_repair_options_data()

	if not initial:
		selected_id = body["actions"][0]["value"]
		selected_name = device_repairs_obj.get_product_repair_by_id(selected_id).display_name
		if remove:
			del metadata['extra']['products_to_waste'][selected_id]
		else:
			metadata["extra"]["products_to_waste"][selected_id] = selected_name

	view = add_base_modal()

	if metadata["extra"]["products_to_waste"]:
		add_header_block(view["blocks"], "To Be Wasted")
		for repair in metadata["extra"]["products_to_waste"]:
			add_button_section(
				title=metadata["extra"]["products_to_waste"][repair],
				button_text="Remove from Waste",
				button_value=repair,
				block_id=f"button_waste_remove_{repair}",
				action_id="button_waste_remove",
				blocks=view["blocks"]
			)

	add_header_block(view["blocks"], "Add Parts To Waste Record")

	for repair in repairs_info:
		if repair['mon_id'] not in metadata["extra"]["products_to_waste"]:
			add_button_section(
				title=repair["name"],
				button_text="Add to Waste",
				button_value=repair["mon_id"],
				block_id=f"button_waste_select_{repair['mon_id']}",
				action_id="button_waste_selection",
				blocks=view["blocks"]
			)

	view["private_metadata"] = json.dumps(metadata)
	return view


def select_waste_variants(body):
	def get_base_modal():
		basic = {
			"type": "modal",
			"callback_id": "waste_validation_submission",
			"notify_on_close": True,
			"title": {
				"type": "plain_text",
				"text": "Confirming Wasted Items",
				"emoji": True
			},
			"submit": {
				"type": "plain_text",
				"text": "Proceed",
				"emoji": True
			},
			"close": {
				"type": "plain_text",
				"text": "Cancel",
				"emoji": True
			},
			"blocks": []
		}
		return basic

	metadata = helper.get_metadata(body)

	view = get_base_modal()
	add_header_block(view["blocks"], "Parts Ready to Waste (if any):")

	products_device = getattr(data.repairs, metadata['device']['eric_id'])

	product_repairs_to_waste = []
	for waste_id in metadata['extra']['products_to_waste']:
		product_repairs_to_waste.append(
			products_device.get_product_repair_by_id(waste_id)
		)

	validations = []

	for product in product_repairs_to_waste:
		if len(product.part_ids) > 1:
			validations.append(product)
		elif len(product.part_ids) == 1:
			add_context_block(view["blocks"], product.display_name)
			metadata['extra']['parts_to_waste'][str(product.part_ids[0])] = \
				clients.monday.system.get_items('name', ids=product.part_ids)[0].name
		else:
			raise Exception(f"{product.info['display_name']} does not have any Parts associated with it")

	add_divider_block(view["blocks"])
	add_header_block(view["blocks"], "Please Confirm Variants of the Following:")

	for to_validate in validations:
		options = []
		for part_id in to_validate.part_ids:
			part_item = clients.monday.system.get_items(ids=[part_id])[0]
			options.append([part_item.name, part_item.id])
		add_radio_buttons_input_version(
			title=to_validate.display_name,
			block_id=f'waste_validation_{to_validate.mon_id}',
			options=options,
			blocks=view["blocks"],
			action_id=f'waste_validation_radio',
			optional=False
		)

	view["private_metadata"] = json.dumps(metadata)

	return view


def waste_parts_quantity_input(body, external_id):
	def get_base_modal():
		basic = {
			"type": "modal",
			"external_id": external_id,
			"callback_id": "waste_quantity_submission",
			"clear_on_close": True,
			"notify_on_close": True,
			"title": {
				"type": "plain_text",
				"text": "Waste Quantities",
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
			"blocks": []
		}
		return basic

	metadata = helper.get_metadata(body)

	radio_selections = body['view']['state']['values']

	for selected in radio_selections:
		name = radio_selections[selected]['waste_validation_radio']['selected_option']['text']['text']
		mon_id = radio_selections[selected]['waste_validation_radio']['selected_option']['value']
		metadata['extra']['parts_to_waste'][mon_id] = name

	view = get_base_modal()

	for part in metadata['extra']['parts_to_waste']:
		add_single_text_input(
			title=metadata['extra']['parts_to_waste'][part],
			placeholder='How Many Parts Should Be Wasted?',
			block_id=f'waste_quantity_{part}',
			action_id=f'waste_quantity_text',
			blocks=view["blocks"],
			optional=False
		)

	view["private_metadata"] = json.dumps(metadata)

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


def failed_new_user_creation_view(email, no_of_results, failed_to_create=False, phone_issue=False):
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

		if phone_issue:
			add_header_block(base['blocks'], "The phone number you entered is not possible")

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

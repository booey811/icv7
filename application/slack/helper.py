from datetime import datetime, timedelta
import json
from pprint import pprint as p

from zenpy.lib.api_objects import User

from application import BaseItem, EricTicket


def add_device_type_metadata(main_item, custom_metadata):
	if not main_item.device.labels:
		raise Exception(f"No Device Assigned on Monday Item: {main_item.mon_id}")

	else:
		if 'iPhone' in main_item.device.labels[0]:
			custom_metadata['extra']['device_type'] = "iphone"
		elif 'iPad' in main_item.device.labels[0]:
			custom_metadata['extra']['device_type'] = "ipad"
		elif 'Watch' in main_item.device.labels[0]:
			custom_metadata['extra']['device_type'] = "watch"
		elif "MacBook" in main_item.device.labels[0]:
			custom_metadata['extra']['device_type'] = "macbook"
		else:
			custom_metadata['extra']['device_type'] = "other"


def get_refurb_request_markdown(main_item, repairs):
	def format_dates(booking_date):
		if booking_date:
			dt_ob = datetime.strptime(booking_date, '%Y-%m-%d %H:%M')
			change = timedelta(hours=2)
			dead_date = dt_ob - change
			dead_date = dead_date.strftime("%d %b %y %H:%M")
		else:
			booking_date = 'Not Provided'
			dead_date = 'No Booking Date - Cannot Provide Refurb Deadline'

		return [booking_date, dead_date]

	def format_stock_string():
		data = []
		for repair in repairs:
			stock_level = repair.stock_level.value
			if not stock_level:
				stock_level = 0
			data.append([repair.name, stock_level])
		return "\n".join(f"{item[0]}: {item[1]}" for item in data)

	parts_formatted = format_stock_string()

	b_date, d_date = format_dates(main_item.booking_date.value)

	return f"*Low Stock Notification*\nWe have received a repair for " \
	       f"<https://icorrect.monday.com/boards/349212843/pulses/{main_item.mon_id}|{main_item.name}> that we do " \
	       f"not have the stock for.\n\n*Refurbishment Deadline*:\n{d_date}\n*Booking Date/Time*:\n{b_date}\n\n" \
	       f"*Required Parts*:\n{parts_formatted}"


def _init_metadata():
	dct = {
		"main": "",
		"device": {
			"model": "",
			"id": '',
			"eric_id": ''
		},
		"repairs": {
			"labels": [],
			"ids": [],
			"eric_ids": []
		},
		"general": {
			"repair_type": "",
			"service": ""
		},
		"parts": [],
		"financial": [],
		"views": {
			"user_search": ""
		},
		"extra": {
			"selected_repairs": [],
			"notes": '',
			"client_repairs": "",
			"parts_to_waste": {},
			"products_to_waste": {},
			"device_type": ''
		},
		"external_id": "",
		"zendesk": {
			"user": {
				"id": '',
				"name": '',
				'email': '',
				'phone': ''
			},
			"ticket": {
				'id': ''
			}
		},
		"notes": ''
	}

	return dct


def get_metadata(resp_body, update=False, new_data_item=None):
	def handle_data_item(data_item):

		if type(data_item) is BaseItem:
			meta["main"] = data_item.mon_id
			meta["repairs"]["labels"] = data_item.repairs.labels
			meta['general']['service'] = data_item.service.label
			meta["general"]['repair_type'] = data_item.repair_type.label
			try:
				meta["device"]["model"] = data_item.device.labels[0]
			except IndexError:
				meta['device']["model"] = "Unconfirmed"

		elif type(data_item) is EricTicket:
			meta["zendesk"]["ticket"]['id'] = data_item.id
			meta["zendesk"]["user"]['id'] = data_item.user["id"]
			meta["zendesk"]["user"]['name'] = data_item.user['name']
			meta["zendesk"]["user"]['email'] = data_item.user['email']
			meta["zendesk"]["user"]['phone'] = data_item.user['phone']

		elif type(data_item) is User:
			meta["zendesk"]["user"]['id'] = data_item.id
			meta["zendesk"]["user"]['name'] = data_item.name
			meta["zendesk"]["user"]['email'] = data_item.email
			meta["zendesk"]["user"]['phone'] = data_item.phone

		else:
			raise Exception(f"Cannot Update Metadata with {type(data_item)}")

	if not update:
		try:
			meta = resp_body['view']['private_metadata']
			try:
				meta = json.loads(resp_body['view']['private_metadata'])
			except json.JSONDecodeError:
				meta = _init_metadata()

		except KeyError as e:
			meta = _init_metadata()

	else:
		meta = update

	if new_data_item:
		handle_data_item(new_data_item)

	return meta


def create_external_view_id(body, view_name):
	try:
		user_id = body['user_id']
	except KeyError:
		user_id = body['user']['id']
	now = str(datetime.now())
	return f"{view_name}-{user_id}-{now}".replace(":", "").replace(" ", "").replace("-", "").replace(".", "")


def convert_walkin_submission_to_dict(body):
	"""takes in the response body from slack repair intake and returns a dictionary of values and attributes for a main
	board item"""

	# get input data
	state = body["view"]["state"]["values"]

	data_dict = {
		"device_str": state["select_device"]["select_accept_device"]['selected_option']['value'],
		'device_type_str': state["select_device_type"]["select_accept_device_type"]["selected_option"]["value"],
		'repair_type_str': state["select_repair_type"]["radio_accept_device"]["selected_option"]["value"],
		'notes': state["text_notes"]["text_accept_notes"]["value"],
		'pc': state['text_pc']["text_accept_pc"]["value"]
	}

	meta = get_metadata(body)
	data_dict["main_id"] = meta["main"]
	data_dict["zen_user_id"] = meta["zendesk"]["user"]["id"]
	data_dict["zendesk_id"] = meta["zendesk"]["ticket"]["id"]

	return data_dict


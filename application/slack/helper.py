from datetime import datetime, timedelta
import json
from pprint import pprint as p

from application import BaseItem, EricTicket


def add_device_type_metadata(main_item, custom_metadata):
	if not main_item.device.labels:
		raise Exception(f"No Device Assigned on Monday Item: {main_item.mon_id}")

	else:
		if 'iPhone' in main_item.device.labels[0]:
			custom_metadata['extra']['device_type'] = "iPhone"
		elif 'iPad' in main_item.device.labels[0]:
			custom_metadata['extra']['device_type'] = "iPad"
		elif 'Watch' in main_item.device.labels[0]:
			custom_metadata['extra']['device_type'] = "Apple Watch"
		else:
			custom_metadata['extra']['device_type'] = "MacBook"


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
			"id": ''
		},
		"repairs": {
			"labels": [],
			"ids": []
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
			"selected_repairs": []
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
		}
	}

	return dct


def get_metadata(resp_body, update=False, new_data_item=None):
	def handle_data_item(data_item):

		if type(data_item) is BaseItem:
			meta["main"] = data_item.mon_id
			meta["repairs"]["labels"] = data_item.repairs.labels
			meta['general']['service'] = data_item.service.label
			meta["general"]['repair_type'] = data_item.repair_type.label
			meta["device"]["model"] = data_item.device.labels[0]

		elif type(data_item) is EricTicket:
			meta["zendesk"]["ticket"]['id'] = data_item.id
			meta["zendesk"]["user"]['id'] = data_item.user["id"]
			meta["zendesk"]["user"]['name'] = data_item.user['name']
			meta["zendesk"]["user"]['email'] = data_item.user['email']
			meta["zendesk"]["user"]['phone'] = data_item.user['phone']

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
	p(body)
	try:
		user_id = body['user_id']
	except KeyError:
		user_id = body['user']['id']
	now = str(datetime.now())
	return f"{view_name}-{user_id}-{now}"

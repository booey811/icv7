import os

from rq import Queue

from application import BaseItem, zen_help, inventory, HardLog, CustomLogger, clients
from application.monday.config import STANDARD_REPAIR_OPTIONS, REPAIR_COLOURS
from worker import conn
from eric import log_catcher_decor

q_stock = Queue("stock", connection=conn)


def sync_zendesk_fields():
	keys = {  # contains Zendesk Ticket Field IDs to adjust
		'repairs': 360008842297,
		'device': 4413411999249,
		'client': 360010408778,
		'service': 360010444117,
		'repair_type': 360010444077,
		'repair_status': 360005728837
	}

	fields = [item for item in keys]

	# get Eric item for column info
	mon_item = BaseItem(CustomLogger(), item_id_or_mon_item=1290815635)

	for attribute in fields:

		url = f"https://icorrect.zendesk.com/api/v2/ticket_fields/{keys[attribute]}"

		ids_with_names = []
		col = getattr(mon_item, attribute)
		for setting in col.settings:
			try:
				ids_with_names.append([str(int(setting)), str(col.settings[setting])])
			except ValueError:
				pass

		list_of_zen_values = []
		for id_name in ids_with_names:
			list_of_zen_values.append({'name': id_name[1], 'value': f"{attribute}-{id_name[0]}"})

		data = {
			"ticket_field": {
				"custom_field_options": list_of_zen_values
			}
		}

		response = zen_help.send_direct_request(data=data, url=url, method="PUT")

		if response.status_code == 200:
			print(f"{attribute} field updated")
		else:
			raise Exception(f"Could Not Update {attribute} field: {response.text}")


def generate_repair_set(forced_repair_ids=()):
	"""Go to The PRODUCT GENERATOR on the Main Board and use this function to generate the specified repairs and
    parts (in all colours) """

	# Get generator Item
	gennie = BaseItem(CustomLogger(), 1093049167)  # Product Creator Item ID
	gennie.log(f"Generating Repair Set: {gennie.device.labels[0]}")

	repairs_board = clients.monday.system.get_boards('id', ids=[984924063])[0]

	# Check a device has been supplied to the generator item
	if not gennie.device.ids:
		gennie.log(f"Device Column Not Supplied on the Product Generator: "
		           f"https://icorrect.monday.com/boards/349212843/pulses/1093049167")
		gennie.logger.hard_log()

	# Acquire necessary repair IDS from REPAIR OPTIONS, exception if this cannot be found
	repair_ids = []
	device_type = "Device"
	if forced_repair_ids:
		repair_ids = forced_repair_ids
		gennie.log(f"Forcing Repair IDs: {repair_ids}")
	elif gennie.repairs.ids:
		repair_ids = gennie.repairs.ids
	else:
		for option in STANDARD_REPAIR_OPTIONS:
			if option in gennie.device.labels[0]:
				repair_ids = STANDARD_REPAIR_OPTIONS[option]
				device_type = option
				gennie.log(f"Requested Generation: {gennie.device.labels[0]}")
				gennie.log(f"Generating Repais for IDs: {repair_ids}")
				break

	if not repair_ids:
		gennie.log("Cannot Generate Repairs - Please Ensure the Device is present in REPAIR_OPTIONS or supply "
		           "forced_repair_ids")
		gennie.log(f"Device Column: {gennie.device.labels[0]} | OPTIONS: {STANDARD_REPAIR_OPTIONS.keys()}")
		gennie.logger.hard_log()

	for device in gennie.device.ids:
		# Construct Repair Item Construction Terms (Device)
		device_id = device
		device_label = gennie.device.settings[str(device_id)]

		# Iterate through Repair IDs to construct items
		search_terms = inventory.construct_search_terms_for_parts(gennie, force_device=device_id)

		for term in search_terms:

			repair_id = term.split("-")[1]

			base_col = repairs_board.get_column_value(id="combined_id")

			base_col.value = str(term)

			results = repairs_board.get_items_by_column_values(base_col, 'name')  # Repairs board ID

			if results:
				print("Repair Found - Ignoring")
				continue

			if os.getenv("ENV") == "devlocal":
				repair_item_constructor([device_id, repair_id], device_label, device_type, repair_id)
			else:
				q_stock.enqueue(
					f=repair_item_constructor,
					args=([device_id, repair_id], device_label, device_type, repair_id)
				)

			gennie.logger.commit("success")


# noinspection PyTypeChecker
def repair_item_constructor(id_info: list, label_info: str, device_type_string: str, repair_id):
	"""sub function that actually creates the repair item, as this job must be queued to avoid timeout"""

	def determine_available_colours(device_string):
		"""returns the correct colour set from monday.config"""
		try:
			colours = REPAIR_COLOURS[device_string]
		except KeyError:
			colours = REPAIR_COLOURS["STANDARD_REPAIR_COLOURS"]

		return colours

	coloured = False
	gennie_item = BaseItem(CustomLogger(), 1093049167)  # Product Creator ID (Main Board)
	repair_searcher_item = BaseItem(gennie_item.logger, board_id=984924063)  # Repairs Board ID
	repair_label = gennie_item.repairs.settings[str(repair_id)]

	repair_colours = determine_available_colours(device_string=device_type_string)

	# Check if part is coloured
	if repair_label in inventory.COLOURED_PARTS:
		for colour in repair_colours:
			colour = colour
			colour_id = gennie_item.device_colour.settings[colour]
			try:
				if not check_if_repair_exists(repair_searcher_item,
				                              "-".join([str(id_info[0]), str(id_info[1]), str(colour_id)])):
					new_repair = inventory.create_repair_item(
						gennie_item.logger,
						dropdown_ids=[id_info[0], id_info[1], colour_id],
						dropdown_names=[label_info, repair_label, colour],
						device_type=device_type_string
					)
				else:
					gennie_item.logger.log("Repair Already Exists - Not Creating")
			except HardLog:
				pass
	else:
		try:
			if not check_if_repair_exists(repair_searcher_item, "-".join([str(id_info[0]), str(id_info[1])])):
				new_repair = inventory.create_repair_item(
					gennie_item.logger,
					dropdown_ids=[id_info[0], id_info[1]],
					dropdown_names=[label_info, repair_label],
					device_type=device_type_string
				)
		except HardLog:
			pass


def check_if_repair_exists(repair_searcher, combined_id):
	"""checks to see if the supplied combined ID can be found on the repairs board, and therefore doesn't need to
    be created. Returns False if the repair can be found

    Returns:
        bool: False if repair exists, True if repair does not exist"""
	search_results = repair_searcher.combined_id.search(combined_id)
	if search_results:
		return True
	return False

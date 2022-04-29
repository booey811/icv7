import os
import datetime
import time
from functools import wraps
from pprint import pprint as p
import json
import logging

import rq
import zenpy.lib.api_objects as zen_obj
from zenpy.lib.exception import APIException as zen_ex

from moncli.api_v2.exceptions import MondayApiError

import data
import utils.tools
from application import BaseItem, clients, phonecheck, inventory, CannotFindReportThroughIMEI, accounting, \
	EricTicket, financial, CustomLogger, xero_ex, mon_ex, views, slack_config, s_help, add_repair_event, get_timestamp, \
	slack_ex
import tasks
from utils.tools import refurbs
from application.monday import config as mon_config
from worker import q_hi, q_lo, q_def

from application.slack import exceptions as slack_ex

logger = logging.getLogger()


def log_catcher_decor(eric_function):
	@wraps(eric_function)
	def wrapper(webhook, test=None):
		logger = CustomLogger()
		# Attempt to execute the Eric function
		try:
			logger.func = str(eric_function.__name__)
			eric_function(webhook, logger, test)
			logger.commit("success")
		except MondayApiError as e:
			for item in e.messages:
				logger.log(item)
			logger.summary = 'Monday Spazzed Out During Submission'
			logger.commit("raised")
			raise e
		except UserError as e:
			logger.log("User Error Encountered")
			logger.summary = e.summary
			logger.commit("user")
			raise e
		except AwaitingResponse as e:
			logger.log("Awaiting Response From User")
			logger.summary = e.summary
			logger.commit('waiting')
			raise e
		except BaseException as e:
			logger.log(str(e))
			logger.summary = str(e)
			logger.commit("error")
			raise e

	return wrapper


@log_catcher_decor
def handle_repair_events(webhook, logger, test=None):
	if test:
		event_id = test
	else:
		event_id = webhook["pulseId"]
	eric_event = BaseItem(logger, event_id)

	columns = [["chain_trigger", "Connected"]]

	if eric_event.actions_status.label == "No Actions Required":
		# Adjust Chain Trigger to add to Brick Chain
		q_lo.enqueue(
			tasks.add_to_brick_chain,
			eric_event.mon_id
		)
		return True

	event_type = eric_event.event_type.label
	actions = json.loads(eric_event.json_actions.value)

	if event_type == "Parts Consumption":
		job = q_hi.enqueue(
			inventory.adjust_stock_level,
			kwargs={
				"logger": None,
				"part_reference": actions['inventory.adjust_stock_level'],
				"quantity": 1,
				"source_object": eric_event.mon_id
			},
			retry=rq.Retry(max=5, interval=20)
		)
		while not job.result:
			time.sleep(0.5)

		columns += [
			["actions_status", "Complete"],
			["related_items", [job.result, actions['inventory.adjust_stock_level']]]
		]

		job_2 = q_lo.enqueue(
			tasks.rq_item_adjustment,
			kwargs={
				"item_id": str(eric_event.mon_id),
				"columns": columns
			},
			depends_on=job,
			retry=rq.Retry(max=5, interval=20)
		)

	elif event_type == "Waste Record":
		job = q_hi.enqueue(
			inventory.adjust_stock_level,
			kwargs={
				"logger": None,
				"part_reference": actions['inventory.adjust_stock_level'][0],
				"quantity": actions['inventory.adjust_stock_level'][1],
				"source_object": eric_event.mon_id
			},
			retry=rq.Retry(max=5, interval=20)
		)
		while not job.result:
			time.sleep(0.5)

		columns += [
			["actions_status", "Complete"],
			["related_items", [job.result, actions['inventory.adjust_stock_level'][0]]]
		]

		job_2 = q_lo.enqueue(
			tasks.rq_item_adjustment,
			kwargs={
				"item_id": str(eric_event.mon_id),
				"columns": [
					["actions_status", "Complete"],
					["related_items", [job.result, actions['inventory.adjust_stock_level'][0]]]
				]
			},
			depends_on=job,
			retry=rq.Retry(max=5, interval=20)
		)

	else:
		eric_event.actions_status.value = "Error"
		eric_event.commit()
		return False

	eric_event.actions_status.value = 'Processing'
	eric_event.commit()
	return True


@log_catcher_decor
def process_stock_count(webhook, logger, test=None):
	logger.log('Process Stock Count Requested')

	# Get Stock Count Board (Needed for creating New Group and getting New Count Group)
	logger.log('Getting Count Board')
	count_board = clients.monday.system.get_boards('id', ids=[1008986497])[0]
	# Create Group for Processed Count
	logger.log('Creating Group')
	processed_group = count_board.add_group(f'Count | {datetime.datetime.today().strftime("%A %d %m %y")}')

	new_count_group_id = "new_group26476"

	# Get Current Count Group
	logger.log('Getting Items')
	new_count_group = count_board.get_groups('id', ids=[new_count_group_id])[0]
	logger.log('Got Items')

	# Iterate Through Counted Items & Consolidate Results into dict of {Part ID: Total Quantities}
	count_totals = {}  # dict of Part ID against Eric Part Item, Expected Quantity and Counted Quantity

	# Consolidate results
	for item in new_count_group.items:

		count_item = BaseItem(logger, item.id)

		part_id = count_item.part_id.value
		count_num = count_item.count_num.value
		if count_num is None:
			count_num = 0

		if part_id not in count_totals:
			part_item = BaseItem(logger, part_id)
			count_totals[part_id] = {
				'count': count_item,
				'part': part_item,
				'expected': part_item.stock_level.value,
				'actual': count_num
			}
		else:
			count_totals[part_id]['actual'] += count_num
			count_item.moncli_obj.archive()

	# Adjust Part stock levels and Count Item Status & Group
	for result in count_totals:
		inventory.adjust_stock_level(
			logger=logger,
			part_reference=count_totals[result]['part'],
			quantity=count_totals[result]['actual'],
			source_object=count_totals[result]["count"],
			absolute=True
		)

		count_totals[result]['count'].count_status.label = 'Confirmed'
		count_totals[result]['count'].count_num.value = count_totals[result]['actual']
		count_totals[result]['count'].expected_num.value = count_totals[result]['expected']
		count_totals[result]['count'].moncli_obj.move_to_group(processed_group.id)
		count_totals[result]['count'].commit()

	logger.clear()
	return True


@log_catcher_decor
def fetch_pc_report(webhook, logger, test=None):
	if test:
		repair_item = BaseItem(logger, test)
	else:
		repair_item = BaseItem(logger, webhook['pulseId'])

	try:
		# Get Device info via IMEI
		logger.log(f'Fetching Phonecheck Report for IMEI: {repair_item.imeisn.value}')
		report_info = phonecheck.get_info(repair_item.imeisn.value)
	except CannotFindReportThroughIMEI:
		logger.log(f'No Phonecheck Report Found')
		repair_item.pc_reports_status.label = 'No Report Found'
		repair_item.commit()
		logger.hard_log()
		return ''

	#  Fetch the HTML Report for the check instance via report ID
	logger.log(f'Fetching HTML Report {report_info["A4Reports"]}')
	html_report = phonecheck.get_certificate(report_info['A4Reports'])

	# Converting to PDF
	path_to_pdf_report = phonecheck.new_convert_to_pdf(html_report, report_info['A4Reports'])

	# Add PDF File to Repair Item
	repair_item.pc_reports.files = f'tmp/pc_reports/report-{report_info["A4Reports"]}.pdf'

	# Delete the report file - helps clean local development dir clean
	os.remove(f'tmp/pc_reports/report-{report_info["A4Reports"]}.pdf')

	return True


@log_catcher_decor
def print_stock_info_for_mainboard(webhook, logger, test=None):
	logger.log("Checking Stock For MainBoard Item")

	if test:
		main_item = BaseItem(logger, test)
	else:
		main_item = BaseItem(logger, webhook["pulseId"])

	stock_info = inventory.get_stock_info(main_item)

	# Create Monday Friendly Update from Stock Info
	stock_list = []
	for item in stock_info:
		stock_list.append(f"{item}: {stock_info[item]['stock_level']}")
	stock_string = "\n".join(stock_list)
	update = f"""STOCK LEVELS\n\n{stock_string}"""

	try:
		update_info = main_item.moncli_obj.add_update(body=update)
		logger.log(f"Update Added: {update_info['body']}")
	except MondayApiError as e:
		logger.log("Monday API Error Occurred")
		logger.log(e.messages)
		logger.hard_log()

	logger.soft_log()

	return True


# noinspection PyTypeChecker
@log_catcher_decor
def create_enquiry_ticket(webhook, logger, test=None):
	def extract_enquiry_data(enquiry_item):

		# params to extract
		name = enquiry_item.name
		device_type = "Not Provided"
		model = "Not Provided"
		message = "Not Provided"

		try:
			value = enquiry_item.device_type.value
			if value:
				device_type = value
		except AttributeError:
			pass

		try:
			value = enquiry_item.model.value
			if value:
				model = value
		except AttributeError:
			pass

		try:
			value = enquiry_item.message.value
			if value:
				message = value
		except AttributeError:
			pass

		return [name, device_type, model, message]

	logger.log("Creating Panrix Enquiry Ticket")

	if test:
		item = BaseItem(logger, test)
	else:
		item = BaseItem(logger, webhook["pulseId"])

	# create eric ticket for panrix brand
	uncommitted_ticket = EricTicket(logger, None, new=item)
	uncommitted_ticket.zenpy_ticket.brand_id = 360004939497  # panrix brand ID

	enq_type = item.moncli_board_obj.name

	enq_data = extract_enquiry_data(item)

	# add enquiry message
	comment = \
		f"""Enquiry Type: {enq_type}
Client Name: {enq_data[0]}
Device: {enq_data[1]}
Model: {enq_data[2]}

Message: {enq_data[3]}
"""
	if enq_type == "Diagnostic Requests":
		turn_on_value = "Not Provided"
		exposed_to_liquid = "Not Provided"
		try:
			turn_on_value = item.turn_on_status.value
		except AttributeError:
			pass

		try:
			exposed_to_liquid = item.exposed_to_liquid.value
		except AttributeError:
			pass

		comment += f"\n\nDoes the device turn on?\n{turn_on_value}\n\nHas the device been exposed to liquid?\n{exposed_to_liquid}"

	uncommitted_ticket.add_comment(comment)
	new_zen_ticket = uncommitted_ticket.commit()

	# add other data & intro macro
	new_eric_ticket = EricTicket(logger, new_zen_ticket)
	macro_effect = clients.zendesk.tickets.show_macro_effect(new_eric_ticket.zenpy_ticket,
	                                                         360128472418)  # New Panrix Enquiry Macro
	clients.zendesk.tickets.update(macro_effect.ticket)

	logger.soft_log()

	return True


@log_catcher_decor
def refurb_phones_initial_pc_report(webhook, logger, test=None):
	logger.log("Fetching Phonecheck Data for Refurb iPhones")

	if test:
		item = BaseItem(logger, test)
	else:
		item = BaseItem(logger, webhook["pulseId"])

	# Get info from phonecheck
	try:
		logger.log(f"Searching for IMEI[{item.imeisn.value}]")
		report_info = phonecheck.get_info(item.imeisn.value)
	except CannotFindReportThroughIMEI as e:
		# Cannot find report - IMEI entered incorrectly or device not checked
		item.pc_report_status_pre.label = "No Report Found"
		item.add_update(f"Cannot Find A Report for IMEI: {item.imeisn.value}. Check the IMEI number or make sure you "
		                f"have completed a phonecheck test run for this device.")
		logger.log("No report found")
		logger.hard_log()
		raise e

	# Sync Actual Condition Values (set by user when receiving) with Init and Working Values
	refurbs.sync_i_a_and_w_values(item)

	# Use Phonecheck Data to set required repairs
	summary = f"PHONECHECK REPORT DATA\nDate of Check: {report_info['DeviceUpdatedDate']}\n" \
	          f"Target Grade: {item.target_grade.label}\n\n\fFace ID Condition: {item.a_face_id.label}\n\n===== FAILED =====\n"

	phonecheck.generate_and_store_pc_report(item.imeisn.value, item.pre_report)

	refurbs.sync_pc_to_status_values(item, report_info, summary)

	batt_health = report_info["BatteryHealthPercentage"]
	batt_cycles = report_info["BatteryCycle"]

	refurbs.process_battery_data(item, batt_health, initial=True)

	summary += f"\n===== BATTERY STATS =====\nHealth: {batt_health}\nCycles: {batt_cycles}"

	item.pc_report_status_pre.label = "Captured"
	item.report_summary.value = summary
	item.pc_report_id.value = report_info["A4Reports"]
	item.add_update(summary)
	item.commit()

	logger.soft_log()


@log_catcher_decor
def create_repairs_profile(webhook, logger, test=None):
	def add_financial_subitem(financial_item, repair_item):

		if isinstance(financial_item, (str, int)):
			financial_item = BaseItem(CustomLogger(), financial_item)
		if isinstance(repair_item, (str, int)):
			repair_item = BaseItem(CustomLogger(), repair_item)

		blank_subitem = BaseItem(financial_item.logger, board_id=989906488)

		blank_subitem.parts_id.value = repair_item.parts_id.value
		blank_subitem.quantity_used.value = 1
		if str(repair_item.parts_id.value) == '1112258883':  # No Parts Used Part ID TODO: Setup monday parts[Function] Column to control this automatically
			blank_subitem.eod_status.value = "Admin"

		financial_item.logger.log(f"Adding Subitem - {financial_item.name} | {repair_item.name}")

		financial_item.moncli_obj.create_subitem(
			item_name=repair_item.name,
			column_values=blank_subitem.staged_changes
		)

	logger.log("Creating Repairs Financial Profile")

	if test:
		finance = BaseItem(logger, test)
	else:
		finance = BaseItem(logger, webhook["pulseId"])

	# void processed subitems (if present)
	inventory.void_repairs_profile(finance)

	# Get Main Item
	main = BaseItem(logger, finance.main_id.value)

	# Check colour has been selected
	if main.device_colour.label in ["Not Selected", "PLEASE SELECT"] or not main.device_colour.label:
		main.add_update("No Colour Provided for this Device, please correct this -"
		                " Colourless devices would be incredibly difficult for people to use!")
		main.user_errors.label = "No Colour Given"
		raise UserError("No Colour Provided for this Device, please correct this -"
		                " Colourless devices would be incredibly difficult for people to use!")

	# Fetch Repairs and make sure there are some
	repairs = inventory.get_repairs(main, create_if_not=True)
	if len(repairs) == 0:
		finance.repairs_profile.label = "Failed"
		finance.add_update("Cannot Create Repairs Profile - No Repairs Supplied")
		main.user_errors.label = "No Repair Given"
		main.add_update("Cannot Checkout this repair as no repairs have been provided")
		main.commit()
		finance.commit()
		raise UserError("Cannot Create Repairs Profile - No Repairs Supplied")

	# Check Repairs Exist
	try:
		inventory.check_repairs_are_valid(logger, repairs)
	except mon_ex.RepairDoesNotExist as e:
		main.add_update("This Repair has been submitted but is impossible - please select the correct repair"
		                "It is likely that you have selected a Screen Manufacturer that is not compatible with your "
		                "device\n\n "
		                f"{e.error_message}")
		main.user_errors.label = "Does Not Exist"
		main.commit()
		finance.repair_profile.label = "Failed"
		finance.commit()
		finance.add_update(e.error_message)
		raise UserError(f"Impossible Repair Encounter: {e.repair.name}")

	# import external board data (if needed)
	if finance.external_board_id.value:
		external = BaseItem(logger, finance.external_board_id.value)
		try:
			financial.import_account_specific_data(finance, external)
		except mon_ex.ExternalDataImportError as e:
			finance.repair_profile.label = "Failed"
			finance.add_update(e.error_message)
			finance.commit()
			raise UserError(f"Data missing from External Board item: "
			                f"{external.moncli_board_obj.name}: {external.name} ({external.mon_id})")

	repair_profile = "Complete"
	stock_adjust = "Do Now!"

	for repair in repairs:
		if isinstance(repair, BaseItem):
			if repair.parts_id.value == "1112258883":  # No Parts Used Item ID
				logger.log("No Parts Used Detected - Switching to Manual Stock Checkout")
				stock_adjust = "Manual"
			# noinspection PyTypeChecker
			add_financial_subitem(finance, repair)
		elif isinstance(repair, str):
			logger.log("Repair Not Found - Beginning Creation Process and Setting Stock Checkout to Manual")
			stock_adjust = "Manual"
			repair_profile = "Failed - Creation"
			device_type = "Device"
			for option in mon_config.STANDARD_REPAIR_OPTIONS:
				if option in main.device.labels[0]:
					device_type = option
			dropdown_ids = repair.split("-")
			if len(dropdown_ids) == 3:
				dropdown_labels = [
					main.device.settings[str(dropdown_ids[0])],
					main.repairs.settings[str(dropdown_ids[1])],
					main.device_colour.settings[str(dropdown_ids[2])]
				]
			else:
				dropdown_labels = [main.device.settings[str(dropdown_ids[0])],
				                   main.repairs.settings[str(dropdown_ids[1])]]

			if os.environ["ENV"] == 'devlocal':
				inventory.create_repair_item(
					logger=logger,
					dropdown_ids=dropdown_ids,
					dropdown_names=dropdown_labels,
					device_type=device_type
				)
			else:
				q_hi.enqueue(f=inventory.create_repair_item, args=("new", dropdown_ids, dropdown_labels, device_type))

	finance.repair_profile.label = repair_profile
	finance.stock_adjust.label = stock_adjust
	logger.log("Financial Profile Creation Complete")
	finance.commit()


@log_catcher_decor
def checkout_stock_profile(webhook, logger, test=None):
	if test:
		finance = BaseItem(logger, test)
	else:
		finance = BaseItem(logger, webhook["pulseId"])

	logger.log(f"Checking Out Stock: {finance.name}")

	if finance.repair_profile.label != "Complete":
		logger.log("Repair Profile Not Complete - Cancelling")
		raise UserError("Cannot Checkout Stock - No Repair Profile Created")
	if finance.be_generator.value:
		return True
	try:
		for subitem in finance.moncli_obj.subitems:
			financial.checkout_stock_for_line_item(subitem.id, finance.main_id.value)
		financial.mark_entry_as_complete(finance)
	except mon_ex.TagsOnPartsNotAvailableOnMovements as e:
		logger.log(e.error_message)
		finance.repair_profile.label = 'Failed'
		finance.add_update("Please get Gabe to check Eric's Logs & Update the Tag Transfer from Parts to Movements")
		finance.commit()
		raise DataError(f"Tag Discrepancy Between Parts and Inventory Movements:\n{e.tags}")


@log_catcher_decor
def void_financial_profile(webhook, logger, test=None):
	if test:
		finance = BaseItem(logger, test)
	else:
		finance = BaseItem(logger, webhook["pulseId"])

	inventory.void_repairs_profile(finance)


@log_catcher_decor
def create_or_update_invoice(webhook, logger, test=None):
	if test:
		finance = BaseItem(logger, test)
	else:
		finance = BaseItem(logger, webhook["pulseId"])

	logger.log(f"Creating/Updating Invoice from Financial: {finance.name}")

	# Assemble Items
	subitems = [BaseItem(finance.logger, item.id) for item in finance.moncli_obj.subitems]
	main = BaseItem(logger, finance.main_id.value)
	ticket = None
	if main.zendesk_id.value:
		ticket = EricTicket(logger, main.zendesk_id.value)

	corp_search_item = BaseItem(logger, board_id=1973442389)  # Corporate Board ID
	if finance.shortcode.value:
		corp_items = corp_search_item.shortcode.search(finance.shortcode.value)
		if not corp_items:
			logger.log(f"CANNOT CREATE INVOICE: No Corporate Account Setup for {finance.name}")
			finance.invoice_generation.label = "Validation Error"
			finance.commit()
			raise UserError(f"CANNOT CREATE INVOICE: No Corporate Account Setup for {finance.name}")
	elif ticket and ticket.organisation:
		corp_items = corp_search_item.zendesk_org_id.search(ticket.organisation['id'])
	elif ticket and not ticket.organisation:
		logger.log(f"CANNOT CREATE INVOICE: Ticket[{ticket.id}] used to process invoice, "
		           f"but User[{ticket.user['name']}] is not part of an organisation")
		finance.invoice_generation.label = "Validation Error"
		finance.commit()
		raise UserError(f"CANNOT CREATE INVOICE: Ticket[{ticket.id}] used to process invoice, "
		                f"but User[{ticket.user['name']}] is not part of an organisation")
	else:
		logger.log("CANNOT CREATE INVOICE: No Ticket Associated with Financial Item, and no Shortcode Provided")
		finance.invoice_generation.label = "Validation Error"
		finance.commit()
		raise UserError("CANNOT CREATE INVOICE: No Ticket Associated with Financial Item, and no Shortcode Provided")

	if len(corp_items) > 1:
		accs = '\n'.join([f"{item.name}:{item.id}" for item in corp_items])
		logger.log(f"CANNOT CREATE INVOICE: Too Many Corporate Accounts Found\n\n{accs}")
		finance.invoice_generation.label = "Validation Error"
		finance.commit()
		raise UserError(f"CANNOT CREATE INVOICE: Too Many Corporate Accounts Found\n\n{accs}")
	elif not corp_items:
		logger.log(f"CANNOT CREATE INVOICE: No Corporate Account Setup for {finance.name}")
		finance.invoice_generation.label = "Validation Error"
		finance.commit()
		raise UserError(f"CANNOT CREATE INVOICE: No Corporate Account Setup for {finance.name}")
	else:
		corporate = BaseItem(logger, corp_items[0].id)

	# Check financial Item validity against corporate item
	try:
		results = accounting.check_financial_against_requirements(corporate, finance)
	except xero_ex.FinancialAndCorporateItemIncompatible as e:
		finance.add_update(e.corp_requirements)
		finance.invoice_generation.label = "Validation Error"
		finance.add_update(
			f"Financial Item[{finance.name}] Does not Match Requirements from Corp Item[{corporate.name}]")
		finance.commit()
		raise UserError(f"Financial Item[{finance.name}] Does not Match Requirements from Corp Item[{corporate.name}]")

	# Construct Line Data from Items
	repair_line_data = accounting.construct_repair_line_item(finance, subitems, main, ticket, corporate)
	courier_line_data = accounting.construct_courier_line_item(main, corporate, finance)
	line_items = [item for item in [repair_line_data, courier_line_data] if item]

	# Calculate Courier Service Type & Level
	if corporate.payment_method.label == "Business (Xero) Invoice":
		if corporate.payment_terms.label == "Monthly Payments":
			# Get invoice and update
			invoice_search = accounting.get_invoice(corporate.invoice_id.value)["Invoices"]
			if len(invoice_search) == 1:
				inv = invoice_search[0]
				assert inv["Status"] == "DRAFT"
				inv["LineItems"] += line_items
				inv = accounting.update_invoice(inv)
				finance.invoice_generation.label = "Complete"
				finance.invoice_number.value = inv["InvoiceNumber"]
			else:
				finance.invoice_generation.label = "Get Invoice Error"
				finance.add_update(
					f"Too Many Invoices Found When Searching: {corporate.invoice_id.value} | {corporate.name}")
				finance.commit()
				raise DataError(
					f"Too Many Invoices Found When Searching: {corporate.invoice_id.value} | {corporate.name}")

		elif corporate.payment_terms.label == "Pay Per Repair":
			# Create one-off invoice
			inv = accounting.create_invoice(corporate, finance, line_items)
			finance.invoice_generation.label = "Complete"
			finance.invoice_number.value = inv["InvoiceNumber"]
		else:
			finance.invoice_generation.label = "Failed"
			finance.add_update(
				f"Corporate Item Has Unacceptable Label for 'Payment Terms': {corporate.payment_terms.label} | {corporate.name}")
			finance.commit()
			raise UserError(
				f"Corporate Item Has Unacceptable Label for 'Payment Terms': {corporate.payment_terms.label} | {corporate.name}")

	elif corporate.payment_method.label == "Card Payment (In Person)":
		finance.add_update(
			f"Corporate Item Has Unacceptable Label for 'Payment Terms': {corporate.payment_terms.label} | {corporate.name}")
		finance.invoice_generation.label = "Failed"
		finance.commit()
		raise UserError(
			f"Corporate Item Has Unacceptable Label for 'Payment Terms': {corporate.payment_terms.label} | {corporate.name}")

	elif corporate.payment_method.label == "Consumer (Sumup) Invoice":
		finance.add_update(
			f"Corporate Item Expects a Sumup Invoice: {corporate.payment_terms.label} | {corporate.name}")
		finance.invoice_generation.label = "Failed"
		finance.commit()
		raise UserError(f"Corporate Item Expects a Sumup Invoice: {corporate.payment_terms.label} | {corporate.name}")

	else:
		finance.add_update(
			f"Corporate Item Has Unacceptable Label for 'Payment Method': {corporate.payment_terms.label} | {corporate.name}")
		finance.invoice_generation.label = "Failed"
		finance.commit()
		raise UserError(
			f"Corporate Item Has Unacceptable Label for 'Payment Method': {corporate.payment_terms.label} | {corporate.name}")

	finance.commit()


@log_catcher_decor
def create_monthly_invoice(webhook, logger, test=None):
	if test:
		corporate = BaseItem(logger, test)
	else:
		corporate = BaseItem(logger, webhook["pulseId"])

	logger.log(f"Creating Invoice (Monthly) From Corporates: {corporate.name}")

	inv = accounting.create_invoice(corporate, None, monthly=True)

	corporate.invoice_id.value = inv["InvoiceID"]
	corporate.create_invoice.label = "Complete"
	corporate.invoice_link.value = [
		f"https://invoicing.xero.com/edit/{inv['InvoiceID']}",
		inv["InvoiceNumber"]
	]

	corporate.commit()


def search_todays_repairs(body, client):
	# not in use
	# triggered by SOMETHING command
	# send loading view
	resp = client.views_open(
		trigger_id=body['trigger_id'],
		view=views.loading("Getting available bookings")
	)
	# get todays repair group from main board, query for name and id
	bookings = data.MAIN_BOARD.groups[0].items
	# get user search input
	resp = client.views_update(
		view_id=resp["view"]["id"],
		hash=resp["view"]["hash"],
		view=views.bookings_search_input(body)
	)
	# search through names for user input
	query = resp['actions'][0]['value']
	result = None
	for item in bookings:
		if str(query) in item.name or str(query) in item.id:
			result = item

	# If no results, return search screen
	if not result:
		resp = client.views_update(
			view_id=resp["view"]["id"],
			hash=resp["view"]["hash"],
			view=views.bookings_search_input(body, invalid_search=True)
		)


def show_todays_repairs_group(body, client, dev=False):
	# triggers on /bookings command
	# send loading view
	resp = client.views_open(
		trigger_id=body['trigger_id'],
		view=views.loading("Getting available bookings")
	)
	# get todays or devs repair group from main board, query for name and id
	if dev:
		group_id = 'new_group49546'
	else:
		group_id = 'new_group70029'

	bookings = data.MAIN_BOARD.groups[0].get_items()
	# present name alongside 'select repair' button
	resp = client.views_update(
		view_id=resp["view"]["id"],
		hash=resp["view"]["hash"],
		view=views.todays_repairs(bookings)
	)


def slack_user_search_init(body, client):
	resp = client.views_open(
		trigger_id=body["trigger_id"],
		view=views.user_search_request(body)
	)


def slack_user_search_results(body, client):
	meta = s_help.get_metadata(body)
	external_id = meta['external_id']

	resp = client.views_update(
		# trigger_id=body['trigger_id'],
		external_id=external_id,
		view=views.loading(f"Searching Database")
	)

	search_term = body['actions'][0]['value']
	results = clients.zendesk.search(search_term, type='user')

	resp = client.views_update(
		view_id=resp["view"]["id"],
		hash=resp["view"]["hash"],
		view=views.user_search_request(body, zenpy_results=results)
	)


def show_new_user_form(body, client):
	resp = client.views_push(
		trigger_id=body['trigger_id'],
		view=views.loading("Generating New User Form")
	)

	resp = client.views_update(
		view_id=resp['view']['id'],
		hash=resp["view"]["hash"],
		view=views.new_user_form(body)
	)


def check_and_create_new_user(body, client, ack):
	external_id = s_help.create_external_view_id(body, "creating_user")

	ack({
		"response_action": "update",
		"view": views.loading("Attempting to Create User", external_id)
	})

	meta = s_help.get_metadata(body)

	email = body['view']['state']['values']['new_user_email']['plain_text_input-action']['value']
	phone = body['view']['state']['values']['new_user_phone']['plain_text_input-action']['value']
	name = body['view']['state']['values']['new_user_name']['plain_text_input-action']['value']
	surname = body['view']['state']['values']['new_user_surname']['plain_text_input-action']['value']

	# check the user is not dense: does the email already exist in Zendesk?
	results = clients.zendesk.search(email, type='user')

	if len(results) == 0:
		# create user
		user = zen_obj.User(
			name=f"{name} {surname}",
			email=email
		)
		try:
			user = clients.zendesk.users.create(user)
			user.phone = phone
			user = clients.zendesk.users.update(user)
			# generate view
			view = views.new_user_result_view(body, user)
		except zen_ex as e:
			view = views.failed_new_user_creation_view(email, len(results), e)

	else:
		# user found with that email, please go back to search and enter this email
		view = views.failed_new_user_creation_view(email, len(results))

	resp = client.views_update(
		external_id=external_id,
		view=view
	)


def check_stock(body, client, initial=False, get_level=False):
	meta = s_help.get_metadata(body)
	if initial:
		# send loading view
		resp = client.views_open(
			trigger_id=body['trigger_id'],
			view=views.loading("Beginning Stock Check")
		)

		view_id = resp["view"]["id"]
		hash_val = resp['view']['hash']

	elif get_level:
		resp = client.views_update(
			view_id=body['view']['id'],
			hash=body['view']['hash'],
			view=views.stock_check_flow_maker(body, fetching_stock_levels=True)
		)
		device = getattr(data.repairs, meta["device"]["eric_id"])
		repair = getattr(device, body['actions'][0]['selected_option']['value'])
		if not repair.part_ids:
			try:
				raise slack_ex.SlackUserError(
					client,
					f"This Product {repair.display_name} Has No Parts Linked To It, So We Cannot Provide A Stock Level",
					data_points=[
						"Issue: Product Not Linked to a Part on Products Board",
						f"https://icorrect.monday.com/boards/2477699024/pulses/{repair.mon_id}"
					]
				)
			except slack_ex.SlackUserError as e:
				client.views_update(
					view_id=body['view']['id'],
					view=e.view
				)
				return

		parts = clients.monday.system.get_items('id', ids=repair.part_ids)

		info = []
		for part in parts:
			stock_level = part.get_column_value(id="quantity").value
			info.append([part.name, stock_level])

		get_level = info

		view_id = resp['view']['id']
		hash_val = resp['view']['hash']

	else:
		view_id = body['view']['id']
		hash_val = body['view']['hash']

	resp = client.views_update(
		view_id=view_id,
		hash=hash_val,
		view=views.stock_check_flow_maker(body, initial=initial, get_level=get_level)
	)


def show_walk_in_info(body, client, from_search=False, from_booking=False, from_create=None):
	# send loading view

	ext_id = s_help.create_external_view_id(body, "walkin_info_view")
	view = views.loading("Getting Walk-In Acceptance Data", external_id=ext_id)

	if from_create:
		from_create(
			{
				"response_action": "push",
				"view": view
			}
		)
	else:

		resp = client.views_push(
			trigger_id=body['trigger_id'],
			view=view
		)

	meta = s_help.get_metadata(body)
	item = None
	ticket = None

	if from_booking:
		item = BaseItem(CustomLogger(), body['actions'][0]['value'])
		if not item.zendesk_id.value:
			try:
				raise slack_ex.SlackUserError(
					client,
					f"{item.name}[{item.mon_id}] has no Zendesk ticket linked to it, meaning we are "
					f"unable to contact the client (and the booking was taken incorrectly). In future, "
					f"we'll create the ticket here, but for now you'll need to go back and use the "
					f"'/users' command to book this repair in"
				)
			except slack_ex.SlackUserError as e:
				client.views_update(
					external_id=ext_id,
					view=e.view
				)
				return
		else:
			ticket = EricTicket(item.logger, item.zendesk_id.value)
			user = ticket.zenpy_ticket.requester
	elif from_search:
		user = clients.zendesk.users(id=body['actions'][0]['value'])
	elif from_create:
		user = clients.zendesk.users(id=meta["zendesk"]["user"]["id"])
	else:
		raise Exception("show_walk_in_info received a call without coming from a booking, search result or user create")

	view = views.walkin_booking_info(body=body, zen_user=user, monday_item=item, ticket=ticket)

	resp = client.views_update(
		external_id=ext_id,
		view=view
	)


def handle_walk_in_updates(body, client, phase):
	metadata = s_help.get_metadata(body)

	resp = client.views_update(
		external_id=metadata["external_id"],
		view=views.walkin_booking_info(body=body, phase=phase)
	)


def process_walkin_submission(body, client, ack):
	ext = s_help.create_external_view_id(body, "walkin_submission")  # generate external ID
	view = views.loading("Processing Walk-In Data", external_id=ext)  # generate view with specified external ID

	# port to Monday
	data_dict = s_help.convert_walkin_submission_to_dict(body)
	intake_notes = data_dict['notes']

	meta = s_help.get_metadata(body)
	meta["device"]["eric_id"] = \
		body["view"]["state"]["values"]['select_device']["select_accept_device"]["selected_option"]['value']

	ticket = None

	cuslog = CustomLogger()
	columns = [["intake_notes", intake_notes]]

	if not data_dict["zendesk_id"]:
		# create ticket & add to monday
		if data_dict["main_id"]:
			raise Exception("Slack Repair Acceptance Has a Main ID But No Zendesk Ticket (Shouldn't happen)")

		if not data_dict["zen_user_id"]:
			raise Exception("Slack Repair Acceptance Submission Commissioned without Zendesk References")

		eric_ticket = EricTicket(cuslog, None, new=data_dict["zen_user_id"])

		eric_ticket.zenpy_ticket.subject = f"Your {data_dict['device_str']} {data_dict['repair_type_str']}"

		eric_ticket.add_comment(
			intake_notes,
			public=False
		)

		zenp_ticket = eric_ticket.commit()

		eric_ticket = EricTicket(cuslog, zenp_ticket)

		tags = [
			# f"device-{data.MAIN_DEVICE[data_dict['device_str']]}",
			f"service-1",  # Walk-In Service (Has to be as this flow is only to be used upstairs)
			f"repair_type-{data.MAIN_REPAIR_TYPE[data_dict['repair_type_str']]}",
		]

		eric_ticket.add_tags(tags)

		data_dict["zendesk_id"] = eric_ticket.zenpy_ticket.id

		if not data_dict["main_id"]:
			name = f"{eric_ticket.user['name']}"
			client_label = 'End User'
			blank = BaseItem(cuslog, board_id=349212843)  # Mainboard ID

			blank.repair_type.label = data_dict["repair_type_str"]
			blank.repair_status.label = "Received"
			blank.service.label = "Walk-In"
			blank.zendesk_id.value = data_dict["zendesk_id"]
			blank.ticket_url.value = [
				f"https://icorrect.zendesk.com/agent/tickets/{data_dict['zendesk_id']}",
				str(data_dict['zendesk_id'])
			]
			blank.phone.value = eric_ticket.user["phone"]
			blank.email.value = eric_ticket.user["email"]
			blank.device_eric_id.value = meta["device"]["eric_id"]
			blank.device_eric_name.value = getattr(data.repairs, meta["device"]["eric_id"]).info["display_name"]
			blank.notifications_status.label = "ON"
			if data_dict["pc"]:
				blank.passcode.value = data_dict["pc"]

			if eric_ticket.organisation:
				name += f' ({eric_ticket.organisation["name"]})'
				blank.company_name.value = eric_ticket.organisation["name"]
				client_label = "Corporate"

			blank.client.label = client_label

			blank.new_item(
				name=name,
				convert_eric=True
			)
			main = blank

			data_dict["main_id"] = blank.moncli_obj.id

			eric_ticket.fields.main_id.adjust(str(blank.moncli_obj.id))
			eric_ticket.add_tags(["mondayactive"])
			eric_ticket.commit()

		else:
			main = BaseItem(cuslog, data_dict["main_id"])
			main.repair_status.label = "Received"

	elif data_dict["zendesk_id"]:
		ticket = EricTicket(cuslog, data_dict["zendesk_id"])
		ticket.add_comment(
			intake_notes,
			public=False
		)

		main = BaseItem(cuslog, data_dict["main_id"])
		# main.device.replace(data_dict["device_str"])
		main.repair_type.label = data_dict["repair_type_str"]
		main.repair_status.label = "Received"
		main.device_eric_id.value = meta["device"]["eric_id"]
		main.device_eric_name.value = getattr(data.repairs, meta["device"]["eric_id"]).info["display_name"]
		if data_dict["pc"]:
			main.passcode.value = data_dict["pc"]
		main.commit()

	else:
		raise Exception("Unexpected Exception in Walk-In Processing Route")

	q_def.enqueue(
		tasks.rq_item_adjustment,
		kwargs={
			"item_id": main.mon_id,
			"update": f"INTAKE NOTES\n\n{intake_notes}",
			"columns": columns
		}

	)
	q_def.enqueue(
		add_repair_event,
		kwargs={
			'main_item_or_id': main.moncli_obj.id,
			'timestamp': get_timestamp(),
			'event_name': "Received Device",
			'event_type': "Device Received",
			'summary': f"Device Received\n\n{intake_notes}",
			"username": slack_config.get_username(body["user"]["id"])
		}
	)


def begin_slack_repair_process(body, client, ack, dev=False):
	ack()
	# Get active user IDs
	# DURING DEVELOPMENT WE WILL USE THE DEV GROUP AS THE SAMPLE USER
	if dev:
		username = 'dev'
	else:
		user_id = body['user_id']
		username = slack_config.USER_IDS[user_id]

	external_id = s_help.create_external_view_id(body, "begin_repairs")

	client.views_open(
		trigger_id=body['trigger_id'],
		view=views.loading(f"Getting {username.capitalize()}'s next repair", external_id=external_id)
	)

	# Convert from Slack User to Monday User IDs, and get the relevant group
	main_group_id = mon_config.MAINBOARD_GROUP_IDS[username]

	# try for items in group, report if none
	try:
		next_repair = BaseItem(
			CustomLogger(),
			clients.monday.system.get_boards(ids=[349212843])[0].get_groups(
				'items.[id, name]',
				ids=[main_group_id]
			)[0].items[0])
	except IndexError:
		try:
			raise slack_ex.SlackUserError(
				client,
				"There are no Repairs in Your Group, Please Ask Your Manager to Assign Some Repairs",
				[username]
			)
		except slack_ex.SlackUserError as e:
			client.views_update(
				external_id=external_id,
				view=e.view
			)
			raise Exception(f"Cannot Begin Repairs: No Repairs Assigned to Technician's Group: {username}")

	# check item has device assigned
	if not next_repair.device.ids:
		try:
			raise slack_ex.SlackUserError(
				client,
				f"{next_repair.name}[{next_repair.mon_id}] Has No Device Assigned To It - Please let Gabe Know and Try Again",
				[f"username: {username}"]
			)
		except slack_ex.SlackUserError as e:
			view = e.view

	else:
		try:
			if not next_repair.device_eric_id.value:

				client.views_update(
					external_id=external_id,
					view=views.loading(
						"Converting OLD REPAIRS/PARTS data into NEW PRODUCTS data (can take a while)",
						external_id=external_id
					)
				)
				try:
					product = utils.tools.convert_device_id_to_product(next_repair.device.ids[0])
				except utils.tools.ProductConversionError as convert_error:
					try:
						raise slack_ex.SlackUserError(
							client=client,
							footnotes=convert_error.message,
							data_points=[
								f"Parts: {convert_error.tried_parts}"
							]
						)
					except slack_ex.SlackUserError as slack_error:
						client.views_update(
							external_id=external_id,
							view=slack_error.view
						)
						raise Exception

				device_eric_id = data.get_device_eric_id(product.moncli_obj.get_group())

				next_repair.device_eric_id.value = device_eric_id
				next_repair.device_eric_name.value = getattr(data.repairs, device_eric_id).info["display_name"]
				next_repair.commit()
				client.views_update(
					external_id=external_id,
					view=views.loading(
						"Update Successful. Getting Repair Data",
						external_id=external_id
					)
				)

			view = views.pre_repair_info(next_repair, body)

		except slack_ex.SlackUserError as e:
			try:
				raise slack_ex.SlackUserError(
					client,
					footnotes=e.footnotes,
					data_points=[
						f"username: {username}",
					]
				)
			except slack_ex.SlackUserError as e:
				view = e.view

	client.views_update(
		external_id=external_id,
		view=view
	)


def begin_specific_slack_repair(body, client, ack):
	metadata = s_help.get_metadata(body)
	external_id = s_help.create_external_view_id(body, "repair_phase_view")

	ack(
		response_action="update",
		view=views.loading(
			f"Getting Repair Data: {metadata['main']}",
			external_id=external_id,
			metadata=metadata
		)
	)

	main_item = BaseItem(CustomLogger(), metadata['main'])

	resp = client.views_update(
		external_id=external_id,
		view=views.repair_phase_view(main_item, body, external_id)
	)

	try:
		repair_phase = int(main_item.repair_phase.value)
	except TypeError:
		repair_phase = 0
	repair_phase += 1

	q_hi.enqueue(
		tasks.rq_item_adjustment,
		kwargs={
			"item_id": main_item.mon_id,
			"columns": [
				["repair_status", "Under Repair"]
			]
		}
	)

	q_lo.enqueue(
		f=add_repair_event,
		kwargs={
			"main_item_or_id": main_item.mon_id,
			"timestamp": get_timestamp(),
			"event_name": f"Repair Phase {repair_phase}: Beginning",
			"event_type": "Repair Phase Start",
			"summary": f"Begin Repair Phase {repair_phase}",
			"actions_dict": f"repair_phase_{repair_phase}",
			"actions_status": "No Actions Required",
			"username": slack_config.get_username(body["user"]["id"])
		}
	)


def abort_repair_phase(body, client):
	meta = s_help.get_metadata(body)
	q_def.enqueue(
		add_repair_event,
		kwargs={
			"main_item_or_id": meta["main"],
			"timestamp": get_timestamp(),
			"event_name": "Repair Phase Aborted",
			"event_type": "Aborted Process",
			"summary": "User Exited the Repair Process",
			"actions_status": "No Actions Required",
			"username": slack_config.get_username(body["user"]["id"])
		}
	)
	q_def.enqueue(
		tasks.process_repair_phase_completion,
		args=([], meta["main"], meta, get_timestamp(), slack_config.get_username(body["user"]["id"]), 'pause')
	)
	try:
		raise slack_ex.SlackUserError(
			client,
			f"User closed a Repair Phase View: {slack_config.get_username(body['user']['id'])}",
			["app metadata", str(meta), f"https://icorrect.monday.com/boards/349212843/pulses/{meta['main']}"]
		)
	except slack_ex.SlackUserError as e:
		return True


def add_parts_to_repair(body, client, initial, ack, remove=False, diag=False):
	metadata = s_help.get_metadata(body)

	# push loading view (first boot for this process is slow)

	if initial:
		if metadata["general"]["repair_type"] == "Diagnostic":
			if not body['view']['state']['values']['repair_notes']['repair_notes']['value']:
				p("erroring")
				ack({
					"response_action": "errors",
					"errors": {'repair_notes': "Please provide repair notes for a Diagnostic!"}
				})
				return
		external_id = s_help.create_external_view_id(body, "add_parts_to_repair")
		temp_load = views.loading(f"Getting Parts Data (This can take 30-40 seconds after an update is released!",
		                          external_id=external_id, metadata=metadata)
		ack({
			"response_action": "push",
			"view": temp_load
		})
	else:
		external_id = body["view"]["external_id"]

	try:
		view = views.initial_parts_search_box(body, external_id, initial, remove, diag=diag)
	except slack_ex.DeviceProductNotFound as e:
		try:
			if body['view']['state']['values']['repair_notes']['repair_notes']['value']:
				notes = body['view']['state']['values']['repair_notes']['repair_notes']['value']
				metadata["notes"] = notes
				message = \
					f"***** CANNOT USE SLACK TO COMPLETE THIS REPAIR\nPlease add the device to the Prices and " \
					f"Products Board ASAP *****\n\nTECHNICIAN NOTES:\n{notes} "
				q_lo.enqueue(
					tasks.rq_item_adjustment,
					kwarg={
						"item_id": metadata["main"],
						"update": message
					}
				)
			q_lo.enqueue(
				tasks.process_repair_phase_completion,
				args=(
					[], metadata["main"], metadata, get_timestamp(), slack_config.get_username(body["user"]["id"]),
					"pause")
			)
			raise slack_ex.SlackUserError(
				client,
				f"The {e.device} is not supported by Slack UI Repairs, as it has not bee programmed on the 'Parts and "
				f"Products' Board\n\nPlease Let Seb & Gabe know.",
				[f"https://icorrect.monday.com/boards/349212843/pulses/{metadata['main']}"]
			)
		except slack_ex.SlackUserError as e:
			view = e.view
	resp = client.views_update(
		external_id=external_id,
		view=view
	)


def show_variant_selections(body, client, ack):
	external_id = body["view"]["external_id"]
	ack({
		"response_action": "update",
		"view": views.loading("Checking Parts Validity", external_id=external_id, metadata=s_help.get_metadata(body))
	})

	meta = s_help.get_metadata(body)
	repair_ids = [item for item in meta["extra"]["selected_repairs"] if item != "no_parts"]
	if repair_ids:
		selected_repairs = clients.monday.system.get_items('id', ids=repair_ids)
	else:
		selected_repairs = []

	variants = {}
	unprocessed_repair_ids = []
	if "no_parts" in meta["extra"]["selected_repairs"]:
		unprocessed_repair_ids.append("no_parts")

	for repair in selected_repairs:
		part_ids = repair.get_column_value(id="connect_boards8").value
		if len(part_ids) == 1:
			meta['parts'].append(part_ids[0])
		elif len(part_ids) > 1:
			names_and_ids = []
			parts = clients.monday.system.get_items(ids=part_ids)
			for item in parts:
				names_and_ids.append([item.name, item.id])
			variants[repair.name] = {
				"id": repair.id,
				'info': names_and_ids
			}
			unprocessed_repair_ids.append(repair.id)
		else:
			raise Exception(f"No Part IDS Attached to Product {repair.name}[{repair.id}]")

		meta["extra"]["selected_repairs"] = unprocessed_repair_ids

	if variants:
		view = views.display_variant_options(body, variants, meta)
	else:
		view = views.repair_completion_confirmation_view(body=body, from_variants=False, meta=meta,
		                                                 external_id=external_id)

	resp = client.views_update(
		external_id=external_id,
		view=view
	)


def show_repair_and_parts_confirmation(body, client, ack, from_variants=False):
	external_id = body["view"]["external_id"]

	view = views.repair_completion_confirmation_view(body=body, from_variants=from_variants, external_id=external_id,
	                                                 meta=s_help.get_metadata(body))
	ack({
		"response_action": "update",
		"view": view
	})


def show_waste_validations(body, client, ack):
	external_id = body["view"]["external_id"]
	loading_view = views.loading(
		"Searching for Variant Options",
		external_id=external_id
	)
	ack({
		"response_action": "update",
		"view": loading_view
	})

	view = views.select_waste_variants(body)

	client.views_update(
		external_id=external_id,
		view=view
	)


def confirm_waste_quantities(body, client, ack):
	external_id = body["view"]["external_id"]
	ack({
		"response_action": "update",
		"view": views.waste_parts_quantity_input(body, external_id)
	})


def finalise_repair_data_and_request_waste(body, client, ack):
	metadata = s_help.get_metadata(body)
	external_id = s_help.create_external_view_id(body, "waste_data_capture")

	view = views.capture_waste_request(body, external_id)

	notes = body["view"]["state"]["values"]["text_final_repair_notes"]["text_final_repair_notes"]["value"]
	if notes:
		metadata["notes"] += notes + "\n\n"

	ack({"response_action": "update", "view": view})

	if metadata["general"]["repair_type"] == "Repair":
		args = (
			metadata["parts"], metadata["main"], metadata, get_timestamp(),
			slack_config.get_username(body["user"]["id"]),
			"complete")
	elif metadata["general"]["repair_type"] == "Diagnostic":
		args = (
			metadata["parts"], metadata["main"], metadata, get_timestamp(),
			slack_config.get_username(body["user"]["id"]),
			"diagnostic")
	else:
		raise Exception(f"Unrecognised Repair Type {metadata['general']['repair_type']}")

	q_hi.enqueue(
		tasks.process_repair_phase_completion,
		args=args
	)


def begin_parts_search(body, client):
	"""
	presents the clients requested repairs and confirms the parts used in repair
	leads to screen manufacturer selection if required
	presents option to submit wastage
	should eventually trigger a check that the parts usage makes sense (e.g. used a battery during battery
		requested repair)

	"""

	resp = client.views_push(
		trigger_id=body['trigger_id'],
		view=views.loading(f"Isn't Gabe like, the coolest guy ever?")
	)

	resp = client.views_update(
		view_id=resp["view"]["id"],
		hash=resp["view"]["hash"],
		view=views.initial_parts_search_box(body)
	)


def display_repairs_search_results(body, client):
	resp = client.views_update(
		view_id=body['view']['id'],
		hash=body['view']['hash'],
		view=views.loading(f"Isn't Gabe like, the coolest guy ever?")
	)

	resp = client.views_update(
		view_id=resp["view"]["id"],
		hash=resp["view"]["hash"],
		view=views.parts_search_results(body)
	)


def continue_parts_search(body, client):
	resp = client.views_update(
		view_id=body["view"]["id"],
		hash=body["view"]["hash"],
		view=views.loading(f"Isn't Gabe like, the coolest guy ever?")
	)

	client.views_update(
		view_id=resp["view"]["id"],
		hash=resp["view"]["hash"],
		view=views.continue_parts_search(resp_body=body)
	)


def handle_urgent_repair(body, client, ack):
	meta = s_help.get_metadata(body)

	# close modal
	ack({"response_action": "clear"})

	# adjust status
	# move to client services

	abort = q_def.enqueue(
		add_repair_event,
		kwargs={
			"main_item_or_id": meta["main"],
			"event_name": "More Urgent Repair Request Received",
			"event_type": "Aborted Process",
			"timestamp": get_timestamp(),
			"summary": "Moving Item to Client Services to Be Re-queued",
			"actions_dict": [],
			"actions_status": "No Actions Required",
			"username": slack_config.get_username(body["user"]["id"])
		}
	)

	q_def.enqueue(
		tasks.process_repair_phase_completion,
		kwargs={
			"part_ids": [],
			"main_id": meta["main"],
			"timestamp": get_timestamp(),
			"status": "urgent",
			"username": slack_config.get_username(body["user"]["id"]),
			"metadata": meta
		},
		depends_on=abort
	)


def handle_other_repair_issue(body, client, ack, initial=False, more_info=False):
	meta = s_help.get_metadata(body)
	if initial:
		notes = body["view"]["state"]["values"]["repair_notes"]["repair_notes"]['value']
		if notes:
			meta["notes"] = notes
		external_id = s_help.create_external_view_id(body, "handle_other_repair_issue")
		loading_view = views.loading(
			"This Screen Is Just For Improving Stability :)",
			external_id=external_id,
			metadata=meta
		)
		ack({
			"response_action": "push",
			"view": loading_view
		})

	else:
		ack()
		external_id = body["view"]["external_id"]

	view = views.repair_issue_form(body, more_info=more_info)
	view["external_id"] = external_id
	view["private_metadata"] = json.dumps(meta)

	resp = client.views_update(
		external_id=external_id,
		view=view
	)


def process_repair_issue(body, client, ack):
	meta = s_help.get_metadata(body)

	selected = \
		body["view"]["state"]["values"]["dropdown_repair_issue_selector"]["dropdown_repair_issue_selector_action"][
			"selected_option"]["text"]["text"]

	if selected == "Other":
		message = body['view']['state']['values']["text_issue"]["text_issue_action"]["value"]
	else:
		message = selected

	ack({
		"response_action": "clear"
	})

	q_hi.enqueue(
		tasks.log_repair_issue,
		args=(meta["main"], message, slack_config.get_username(body["user"]["id"]), meta)
	)


def cannot_complete_repair_no_parts(body, client):
	resp = client.views_push(
		trigger_id=body['trigger_id'],
		view=views.loading("We haven't developed this yet....... Nothing is loading")
	)


def process_waste_entry(ack, body, client, initial=False, remove=False):
	meta = s_help.get_metadata(body)
	ext_id = body['view']['external_id']
	if initial:
		resp = ack({
			"response_action": "update",
			"view": views.loading("Fetching Wastable Options", metadata=meta, external_id=ext_id)
		})

	client.views_update(
		external_id=ext_id,
		view=views.register_wasted_parts(body, initial, remove, ext_id)
	)


def emit_waste_events(body, client, ack):
	class BreakCycle(Exception):
		def __init__(self, input_id):
			self.input_id = input_id

	meta = s_help.get_metadata(body)
	info = meta["extra"]["parts_to_waste"]

	vals = {}
	for quantity_input in body["view"]["state"]["values"]:
		vals[quantity_input] = body["view"]["state"]["values"][quantity_input]["waste_quantity_text"]["value"]

	try:
		for in_val in vals:
			value = vals[in_val]
			try:
				quan = int(value)
				if quan < 1:
					raise BreakCycle(in_val)
			except ValueError:
				raise BreakCycle(in_val)

	except BreakCycle as e:
		error = {e.input_id: "Must Be A Number Larger Than 0"}
		ack({"response_action": "errors", "errors": error})

	else:
		for quantity_input in body["view"]["state"]["values"]:
			input_part_id = str(quantity_input).replace("waste_quantity_", "")
			for part_id in info:
				if input_part_id == part_id:
					quantity = int(body["view"]["state"]["values"][quantity_input]["waste_quantity_text"]["value"])
					q_lo.enqueue(
						f=add_repair_event,
						kwargs={
							"main_item_or_id": meta["main"],
							"timestamp": get_timestamp(),
							"event_name": f"Waste: {info[part_id]}",
							"event_type": "Waste Record",
							"summary": f"Wasting {quantity}  x  {info[part_id]}",
							"actions_dict": {
								"inventory.adjust_stock_level": [part_id, quantity]
							},
							"username": slack_config.get_username(body["user"]["id"])
						}
					)
		ack({"response_action": "clear"})
	ack({"response_action": "clear"})


def begin_repair_logging(body, client):

	def get_base_modal():
		basic = {
			"type": "modal",
			"title": {
				"type": "plain_text",
				"text": "Device Logging",
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

	external_id = s_help.create_external_view_id(body, "device_logging")
	loading = views.loading(
		"Searching for Repairs Marked as 'Received'",
		external_id=external_id
	)

	client.views_open(
		trigger_id=body["trigger_id"],
		view=loading
	)

	view = get_base_modal()
	blocks = view["blocks"]

	main_board = data.MAIN_BOARD
	val = main_board.get_column_value('status4')
	val.label = "Received"
	items = main_board.get_items_by_column_values(column_value=val)

	for item in items:
		views.add_button_section(
			item.name,
			"Add Info",
			item.id,
			block_id=f"button_section_{item.id}",
			action_id="button_section_logging_repair",
			blocks=blocks
		)

	views.add_header_block(blocks, "Can't Find Your Repair?")
	views.add_context_block(blocks, "Make Sure The Repair has it's 'Status' set to 'Received'")

	client.views_update(
		external_id=external_id,
		view=view
	)


def show_device_logging_form(ack, body, client):

	try:
		external_id = body["view"]["external_id"]
	except KeyError as e:
		external_id = s_help.create_external_view_id(body, "device_logging_form")
		print("ASSIGNING EXTERNAL ID")
		p(str(e))

	loading = views.loading(
		"Collecting Data for Logging",
		external_id
	)
	client.views_push(
		trigger_id=body["trigger_id"],
		view=loading
	)

	meta = s_help.get_metadata(body)

	selected = body["actions"][0]["value"]

	cuslog = CustomLogger()
	main_item = BaseItem(cuslog, selected)




def test_user_init(body, client):
	"""loads loading screen for user and returns slack response for manipulation in console"""
	resp = client.views_open(
		trigger_id=body['trigger_id'],
		view={
			"type": "modal",
			"title": {
				"type": "plain_text",
				"text": "views_open",
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
						"text": "This is a header block",
						"emoji": True
					}
				},
				{
					"type": "section",
					"fields": [
						{
							"type": "plain_text",
							"text": "*this is plain_text text*",
							"emoji": True
						},
						{
							"type": "plain_text",
							"text": "*this is plain_text text*",
							"emoji": True
						},
						{
							"type": "plain_text",
							"text": "*this is plain_text text*",
							"emoji": True
						},
						{
							"type": "plain_text",
							"text": "*this is plain_text text*",
							"emoji": True
						},
						{
							"type": "plain_text",
							"text": "*this is plain_text text*",
							"emoji": True
						}
					]
				}
			]
		})
	return resp


class EricLevelException(Exception):

	def __init__(self):
		pass


class UserError(Exception):

	def __init__(self, summary="User Error: Not Supplied"):
		self.summary = summary


class DataError(Exception):

	def __init__(self, summary="Data Error: Not supplied"):
		self.summary = summary


class AwaitingResponse(Exception):

	def __init__(self, summary="Awaiting User Response"):
		self.summary = summary

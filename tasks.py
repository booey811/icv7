from pprint import pprint as p

from application import BaseItem, CustomLogger, add_repair_event, clients, get_timestamp
import data


def log_repair_issue(main_item_id, message, username, metadata: dict = None):
	if metadata is None:
		metadata = {}
	item = BaseItem(CustomLogger(), main_item_id)
	message_fr = f"******* REPAIR ISSUE RAISED *******\n\nIssue:\n{message}"
	if metadata:
		if metadata["notes"]:
			message_fr += f"\n\nTechnician Notes:\n{metadata['notes']}"
	item.add_update(message_fr)
	add_repair_event(
		item.mon_id,
		"Repair Issue Data",
		"Repair Issue",
		get_timestamp(),
		summary=message,
		actions_dict={
			"move_item": "client_services",
			"notify": "client_services"
		},
		username=username
	)
	item.moncli_obj.move_to_group("new_group6580")
	process_repair_phase_completion([], item.mon_id, metadata, get_timestamp(), username, status="client")


def process_repair_phase_completion(part_ids, main_id, metadata, timestamp, username, status="pause"):

	def generate_diagnostic_report(parts_list, notes):
		basic = "***** DIAGNOSTIC REPORT *****\n\nRepairs Required:\n"
		for part_item in parts_list:
			line = f"-  {part_item.name}\n"
			basic += line
		basic += f"\n TECHNICIAN NOTES\n{notes}"
		return basic

	if part_ids:
		parts_ids = [item for item in part_ids if item != "no_parts"]
		parts = clients.monday.system.get_items('name', ids=parts_ids)
	else:
		parts = []
	main = BaseItem(CustomLogger(), main_id)

	try:
		repair_phase = int(main.repair_phase.value)
	except TypeError:
		repair_phase = 0

	repair_phase += 1

	if metadata:
		if metadata["notes"]:
			add_repair_event(
				main_item_or_id=main,
				event_name=f"Technician Notes",
				event_type="Tech Note",
				timestamp=timestamp,
				summary=metadata["notes"],
				actions_dict=f"repair_phase_{repair_phase}",
				actions_status="No Actions Required",
				username=username
			)

	add_repair_event(
		main_item_or_id=main,
		event_name=f"Repair Phase {repair_phase}: Ending",
		event_type="Repair Phase End",
		timestamp=timestamp,
		summary=f"Ending Repair Phase {repair_phase}",
		actions_dict=f"repair_phase_{repair_phase}",
		actions_status="No Actions Required",
		username=username
	)

	main.repair_phase.value = repair_phase
	if status == "complete":
		for part in parts:
			try:
				current_quantity = int(part.get_column_value('quantity').value)
			except TypeError:
				current_quantity = 0
			if not current_quantity:
				current_quantity = 0
			add_repair_event(
				main_item_or_id=main,
				event_name=f"Consume: {part.name}",
				event_type='Parts Consumption',
				timestamp=timestamp,
				summary=f"Adjusting Stock Level for {part.name} | {current_quantity} -> {current_quantity - 1}",
				actions_dict={'inventory.adjust_stock_level': part.id},
				username=username
			)
		main.repairs.value = []
		main.repair_status.label = "Repaired"
	elif status == "pause":
		main.repair_status.label = "Repair Paused"
	elif status == "client":
		main.repair_status.label = "Client Contact"
	elif status == "urgent":
		main.repair_status.label = "To Be Queued"
	elif status == "diagnostic":
		main.repair_status.label = "Diagnostic Complete"
		report = generate_diagnostic_report(parts, metadata["notes"])
		main.add_update(report)
		add_repair_event(
			main,
			"Diagnostic Complete",
			"Diagnostic Complete",
			get_timestamp(),
			report,
			actions_dict="No Actions Required",
			username=username
		)
	else:
		raise Exception(f"Invalid Status for Repair Phase Completion: {status}")

	main.commit()


def task_repair_event(main_id, event_name, event_type, timestamp, summary, actions_dict=None, actions_status='Not Done'):
	if actions_dict is None:
		actions_dict = {}
	add_repair_event(
		main_id,
		event_name,
		event_type,
		timestamp,
		summary,
		actions_dict,
		actions_status
	)


def rq_item_adjustment(item_id, columns=(), move_item='', update=''):

	item = BaseItem(CustomLogger(), item_id)

	for adjustment in columns:
		attri = getattr(item, adjustment[0])
		attri.value = adjustment[1]

	if move_item:
		if move_item == "cs":
			move_item = "new_group6580"
		item.moncli_obj.move_to_group(group_id=move_item)

	if update:
		item.add_update(message_body=update)

	item.commit()


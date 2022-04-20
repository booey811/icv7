from application import BaseItem, CustomLogger, add_repair_event, clients


def log_repair_issue(main_item_id, message):
	item = BaseItem(CustomLogger(), main_item_id)
	message_fr = f"******* REPAIR ISSUE RAISED *******\n\nTechnician Notes:\n{message}"
	item.add_update(message_fr)
	item.moncli_obj.move_to_group("new_group6580")
	item.repair_status.label = "Client Contact"
	item.commit()
	add_repair_event(
		item.mon_id,
		"Repair Issue Data",
		"Repair Issue Raised",
		summary=message,
		actions_status="No Actions Required"
	)
	add_repair_event(
		item.mon_id,
		f"Repair Phase {item.repair_phase.value}: Ending",
		"Repair Phase End",
		f"Ending Repair Phase {item.repair_phase.value}",
		actions_status="No Actions Required"
	)


def process_repair_phase_completion(part_ids, main_id):
	parts = clients.monday.system.get_items('name', ids=part_ids)
	main = clients.monday.system.get_items(ids=[main_id])[0]
	repair_phase_col = main.get_column_value('numbers5')

	try:
		repair_phase = int(repair_phase_col.value)
	except TypeError:
		repair_phase = 0

	repair_phase += 1

	add_repair_event(
		main_item_or_id=main,
		event_name=f"Repair Phase {repair_phase}: Ending",
		event_type="Repair Phase End",
		summary=f"Ending Repair Phase {repair_phase}",
		actions_dict=f"repair_phase_{repair_phase}",
		actions_status="No Actions Required"
	)

	repair_phase_col.value = repair_phase
	main.change_column_value(column_value=repair_phase_col)

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
			summary=f"Adjusting Stock Level for {part.name} | {current_quantity} -> {current_quantity - 1}",
			actions_dict={'inventory.adjust_stock_level': part.id}
		)


def task_repair_event(main_id, event_name, event_type, summary, actions_dict=None, actions_status='Not Done'):
	if actions_dict is None:
		actions_dict = {}
	add_repair_event(
		main_id,
		event_name,
		event_type,
		summary,
		actions_dict,
		actions_status
	)

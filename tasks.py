from application import BaseItem, CustomLogger, add_repair_event, clients, get_timestamp


def log_repair_issue(main_item_id, message):
	item = BaseItem(CustomLogger(), main_item_id)
	message_fr = f"******* REPAIR ISSUE RAISED *******\n\nTechnician Notes:\n{message}"
	item.add_update(message_fr)
	item.repair_phase.value = int(item.repair_phase.value) + 1
	item.commit()
	add_repair_event(
		item.mon_id,
		"Repair Issue Data",
		"Repair Issue",
		get_timestamp(),
		summary=message,
		actions_dict={
			"move_item": "client_services",
			"notify": "client_services"
		}
	)
	add_repair_event(
		item.mon_id,
		f"Repair Phase {int(item.repair_phase.value)}: Ending",
		"Repair Phase End",
		get_timestamp(),
		f"Ending Repair Phase {int(item.repair_phase.value)}",
		actions_status="No Actions Required"
	)


def process_repair_phase_completion(part_ids, main_id, timestamp):
	if part_ids:
		parts = clients.monday.system.get_items('name', ids=part_ids)
	else:
		parts = []
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
		timestamp=timestamp,
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
			timestamp=timestamp,
			summary=f"Adjusting Stock Level for {part.name} | {current_quantity} -> {current_quantity - 1}",
			actions_dict={'inventory.adjust_stock_level': part.id}
		)


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


def rq_item_adjustment(item_id, columns=(), move_item=''):

	item = BaseItem(CustomLogger(), item_id)

	for adjustment in columns:
		attri = getattr(item, adjustment[0])
		attri.value = adjustment[1]

	if move_item:
		item.moncli_obj.move_to_group(group_id=move_item)

	item.commit()

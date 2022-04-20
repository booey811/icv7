from application import BaseItem, CustomLogger, add_repair_event


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

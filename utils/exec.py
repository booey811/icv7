import application
from application import BaseItem, CustomLogger, zen_help, inventory, HardLog


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

    REPAIR_OPTIONS = {
        "iPhone": [133, 74, 71, 54, 70, 7, 65, 73, 99, 76, 66, 88, 75, 83, 84],
        "Apple Watch": [133, 69, 138],
        "iPad": [133, 30, 69, 54, 99],
        "MacBook": [133, 71, 54, 119, 32, 38]
    }

    COLOURS = [
        "Black", "White", "Space Grey"
    ]

    # Get generator Item
    gennie = BaseItem(CustomLogger(), 1093049167)  # Product Creator Item ID
    gennie.log(f"Generating Repair Set: {gennie.device.labels[0]}")

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
    else:
        for option in REPAIR_OPTIONS:
            if option in gennie.device.labels[0]:
                repair_ids = REPAIR_OPTIONS[option]
                device_type = option
                gennie.log(f"Requested Generation: {gennie.device.labels[0]}")
                gennie.log(f"Generating Repais for IDs: {repair_ids}")
                break

    if not repair_ids:
        gennie.log("Cannot Generate Repairs - Please Ensure the Device is present in REPAIR_OPTIONS or supply "
                   "forced_repair_ids")
        gennie.log(f"Device Column: {gennie.device.labels[0]} | OPTIONS: {REPAIR_OPTIONS.keys()}")
        gennie.logger.hard_log()

    # Construct Repair Item Construction Terms (Device)
    device_id = gennie.device.ids[0]
    device_label = gennie.device.labels[0]

    # Iterate through Repair IDs to construct items
    for repair_id in repair_ids:
        coloured = False
        repair_label = gennie.repairs.settings[str(repair_id)]

        # Check if part is coloured
        if repair_label in inventory.COLOURED_PARTS:
            for colour in COLOURS:
                colour = colour
                colour_id = gennie.device_colour.settings[colour]
                try:
                    new_repair = inventory.create_repair_item(
                        gennie.logger,
                        dropdown_ids=[device_id, repair_id, colour_id],
                        dropdown_names=[device_label, repair_label, colour],
                        device_type=device_type
                    )
                except HardLog:
                    continue
        else:
            try:
                new_repair = inventory.create_repair_item(
                    gennie.logger,
                    dropdown_ids=[device_id, repair_id],
                    dropdown_names=[device_label, repair_label],
                    device_type=device_type
                )
            except HardLog:
                continue

    gennie.logger.soft_log(for_records=True)

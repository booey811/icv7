from pprint import pprint as p

from application import BaseItem, EricTicket, clients, phonecheck, CustomLogger


def sync_fields_from_monday_new(main_board_item: BaseItem = None, eric_ticket=None):
    """This function will accept a Main Board Monday Item and/or an EricTicket and sync IMEI, passcode, device,
    repairs, clients, service, type

    Args:
        eric_ticket (EricTicket): the eric ticket to sync with
        main_board_item (BaseItem): the main board item to sync"""

    # validate and format input
    if not main_board_item and not eric_ticket:  # no inputs
        raise Exception('Zendesk Sync Function not provided with any objects')
    elif main_board_item and eric_ticket:  # items already instantiated
        main = main_board_item
        zen = eric_ticket
        main.log(f"Syncing Fields Main[{main.mon_id}] | Zen[{zen.id}]")
    elif main_board_item:  # monday item supplied only
        main = main_board_item
        main.log(f"Syncing Zen Fields Main[{main.mon_id}]: Acquiring Zendesk Ticket")
        if not main.zendesk_id.value:  # check for zendesk ID
            main.log(f"Unable to Sync to Zendesk: No ID on Mon[{main.mon_id}]")
            main.logger.soft_log()
            raise SyncErrorNoZendeskID()
        else:
            zen = EricTicket(main.logger, main.zendesk_id.value)
    elif eric_ticket:
        eric_ticket.logger.log(f"Syncing Fields Zen[{eric_ticket.id}]")
        eric_ticket.logger.log("Zendesk Sync From an EricTicket has not yet been developed")
        eric_ticket.logger.hard_log()
        raise Exception("Zendesk Sync From an EricTicket has not yet been developed")
    else:
        # Should not be logically possible
        raise Exception("sync_fields_from_monday else route")

    # list and get syncable attributes - text values
    text_atts = ['imeisn', 'passcode']
    tag_atts_dropdown = ['device', 'repairs']
    tag_atts_status = ['repair_status', 'client', 'service', 'repair_type']

    atts = ['repair_status', 'client', 'service', 'repair_type', 'device', 'repairs', 'imeisn', 'passcode']

    for attribute in text_atts:
        mon_col = getattr(main, attribute)
        field = getattr(zen.fields, attribute)
        field.adjust(mon_col.value)

    # list and get syncable attributes - tag values
    tag_atts_dropdown = ['device', 'repairs']
    tag_atts_status = ['repair_status', 'client', 'service', 'repair_type']
    current_tags = [item for item in zen.zenpy_ticket.tags]
    new_tags = [item for item in current_tags]

    # generate new tags from monday dropdown columns
    for attribute in tag_atts_dropdown:
        mon_col = getattr(main, attribute)
        zen_field = getattr(zen.fields, attribute)
        zen_field.adjust(mon_col.ids)

    # generate new tags from monday status columns
    for attribute in tag_atts_status:
        mon_col = getattr(main, attribute)
        zen_field = getattr(zen.fields, attribute)
        zen_field.adjust(mon_col.index)

    clients.zendesk.tickets.update(zen.zenpy_ticket)


def sync_fields_from_monday(main_board_item: BaseItem = None, eric_ticket=None):
    """This function will accept a Main Board Monday Item and/or an EricTicket and sync IMEI, passcode, device,
    repairs, clients, service, type

    Args:
        eric_ticket (EricTicket): the eric ticket to sync with
        main_board_item (BaseItem): the main board item to sync"""

    # validate and format input
    if not main_board_item and not eric_ticket:  # no inputs
        raise Exception('Zendesk Sync Function not provided with any objects')
    elif main_board_item and eric_ticket:  # items already instantiated
        main = main_board_item
        zen = eric_ticket
        main.log(f"Syncing Fields Main[{main.mon_id}] | Zen[{zen.id}]")
    elif main_board_item:  # monday item supplied only
        main = main_board_item
        main.log(f"Syncing Zen Fields Main[{main.mon_id}]: Acquiring Zendesk Ticket")
        if not main.zendesk_id.value:  # check for zendesk ID
            main.log(f"Unable to Sync to Zendesk: No ID on Mon[{main.mon_id}]")
            main.logger.soft_log()
            raise SyncErrorNoZendeskID()
        else:
            zen = EricTicket(main.logger, main.zendesk_id.value)
    elif eric_ticket:
        eric_ticket.logger.log(f"Syncing Fields Zen[{eric_ticket.id}]")
        eric_ticket.logger.log("Zendesk Sync From an EricTicket has not yet been developed")
        eric_ticket.logger.hard_log()
        raise Exception("Zendesk Sync From an EricTicket has not yet been developed")
    else:
        # Should not be logically possible
        raise Exception("sync_fields_from_monday else route")

    # list and get syncable attributes - text values
    text_atts = ['imeisn', 'passcode']

    for attribute in text_atts:
        mon_col = getattr(main, attribute)
        field = getattr(zen, attribute)
        field.adjust(mon_col.value)

    zen = EricTicket(main.logger, zen.commit())

    # list and get syncable attributes - tag values
    tag_atts_dropdown = ['device', 'repairs']
    tag_atts_status = ['repair_status', 'client', 'service', 'repair_type']
    current_tags = [item for item in zen.zenpy_ticket.tags]
    new_tags = [item for item in current_tags]

    # remove currently set multi/dropdown tags
    for attribute in tag_atts_dropdown + tag_atts_status:
        to_remove = [item for item in current_tags if f"{attribute}-" in item]
        new_tags = list(set(new_tags) - set(to_remove))

    # generate new tags from monday dropdown columns
    for attribute in tag_atts_dropdown:
        mon_col = getattr(main, attribute)
        for dd_id in mon_col.ids:
            new_tags.append(f"{attribute}-{dd_id}")

    # generate new tags from monday status columns
    for attribute in tag_atts_status:
        mon_col = getattr(main, attribute)
        new_tags.append(f"{attribute}-{mon_col.index}")

    clients.zendesk.tickets.set_tags(zen.id, new_tags)


class RefurbishedDevicesHelper:

    def __init__(self):
        pass

    @staticmethod
    def sync_i_a_and_w_values(refurb_item):
        """Without committing, syncs the -i, -a and -w values for refurb phones, to be used during the initial checks

        Args:
            refurb_item (BaseItem): Refurb Devices Board Item
        """
        refurb_item.logger.log("Syncing -A, -W and -I values")

        condition_values = ["face_id", "lens", "rear", "charging", "wireless"]
        for attribute in condition_values:
            refurb_item.logger.log(f"Syncing: {attribute}")
            actual = getattr(refurb_item, "a_" + attribute)
            init = getattr(refurb_item, "i_" + attribute)
            working = getattr(refurb_item, "w_" + attribute)
            init.label = actual.label
            if actual.label == "No Repair Required":
                refurb_item.logger.log("-No Repair Required")
                working.label = "No Repair Required"
            else:
                refurb_item.logger.log("-Repair Required")
                working.label = "Repair Required"

    @staticmethod
    def set_device_specific_info_from_initial_pc_report(refurb_item, report_info):
        """Sets -A values for Colour, Model and Memory"""

        refurb_item.logger.log("Adding Initial Device Specific Info")

        colour = report_info["Color"]
        model = report_info["Model"]
        storage = report_info["Memory"]

        refurb_item.logger.log(f"Setting Colour: {colour}")
        refurb_item.a_colour.label = colour

        refurb_item.logger.log(f"Setting Model: {model}")
        refurb_item.a_model.label = model

        refurb_item.logger.log(f"Setting Storage: {storage}")
        refurb_item.a_storage.label = storage

    @staticmethod
    def process_battery_data(refurb_item, battery_health, initial=False):
        """Extracts Battery Health Data and Requisitions a Replacement if Possible"""

        refurb_item.logger.log(f"Processing Phonecheck Battery Data | Initial={initial}")
        if initial:
            refurb_item.i_battery_health.value = battery_health
        refurb_item.w_battery_health.value = battery_health
        refurb_item.logger.log(f"Battery Health: {battery_health}")
        if int(battery_health) < 85:
            refurb_item.logger.log("Replacing Battery")
            if initial:
                refurb_item.i_battery.label = "Repair Required"
            refurb_item.w_battery.label = "Repair Required"
        else:
            refurb_item.logger.log("Battery Health Sufficient")
            if initial:
                refurb_item.i_battery.label = "No Repair Required"
            refurb_item.w_battery.label = "No Repair Required"

    @staticmethod
    def sync_pc_to_status_values(refurb_item, report_info, summary):
        """Checks through the provided PC report and converts the required repairs into Refurb Board status columns"""

        failures = []
        refurb_item.logger.log("Assessing Failures")
        for defect in report_info["Failed"].split(","):
            refurb_item.logger.log(f"Assessing {defect}")
            if defect:
                summary += defect + "\n"
                try:
                    converted = phonecheck.DEFECTS_DICT[defect]
                    refurb_item.logger.log(f"Converted {defect} to {converted}")
                except KeyError:
                    refurb_item.logger.log(f"Failed to convert {defect} Defect to eric attribute reference")
                    failures.append(defect)
                    continue

                if converted:
                    refurb_item.logger.log(f"Eric Atttribute {converted} -> Repair Required")
                    initial = getattr(refurb_item, "i_" + converted)
                    working = getattr(refurb_item, "w_" + converted)
                    initial.label = "Repair Required"
                    working.label = "Repair Required"
                else:
                    refurb_item.logger.log(f'{defect} does not have an applicable column on the refurbs board')

        summary += "\n===== PASSED =====\n"
        refurb_item.logger.log("Assessing Passes")
        for func in report_info["Passed"].split(","):
            refurb_item.logger.log(f"Assessing {func}")
            if func:
                summary += func + "\n"
                try:
                    converted = phonecheck.DEFECTS_DICT[func]
                    refurb_item.logger.log(f"Converted {func} to {converted}")
                except KeyError:
                    refurb_item.logger.log(f"Failed to convert {func} Passed Test to eric attribute reference")
                    failures.append(func)
                    continue
                if converted:
                    refurb_item.logger.log(f"Eric Attribute {converted} -> No Repair Required")
                    initial = getattr(refurb_item, "i_" + converted)
                    working = getattr(refurb_item, "w_" + converted)
                    initial.label = "No Repair Required"
                    working.label = "No Repair Required"
                else:
                    refurb_item.logger.log(f'{func} does not have an applicable column on the refurbs board')


class SyncErrorNoZendeskID(Exception):

    def __init__(self):
        pass


def generate_column_id_list(board_id):
    """Takes a Board ID and spits out a List of Column IDs vs Title"""

    board = clients.monday.system.get_board_by_id(board_id)

    columns = []
    for column in board.columns:
        if column.id in ["item_id", "name"]:
            continue
        columns.append(f"""'{column.id}': '{column.title.replace(" ", "_").lower()}',  # {column.type}""")

    formatted_columns = "\n".join(columns)

    result = f"""'{board_id}': {{
    'name': '{board.name}',
    'columns': {{{formatted_columns}
    }}
}}"""

    print(result)


def settings_list(board_id, column):
    item = BaseItem(CustomLogger(), board_id=board_id)
    settings = getattr(item, column).settings
    p(settings)
    return True


refurbs = RefurbishedDevicesHelper()

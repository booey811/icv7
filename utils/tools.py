from application import BaseItem, EricTicket, clients, CustomLogger
from application.monday import mappings


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
    tag_atts_status = []
    current_tags = [item for item in zen.zenpy_ticket.tags]
    new_tags = [item for item in current_tags]
    
    for attribute in tag_atts_dropdown + tag_atts_status:
        # remove currently set multi/dropdown tags
        to_remove = [item for item in current_tags if f"{attribute}-" in item]
        new_tags = list(set(new_tags) - set(to_remove))

    # generate new tags from monday dropdown columns
    for attribute in tag_atts_dropdown:
        mon_col = getattr(main, attribute)
        for dd_id in mon_col.ids:
            new_tags.append(f"{attribute}-{dd_id}")



    clients.zendesk.tickets.set_tags(zen.id, new_tags)


class SyncErrorNoZendeskID(Exception):

    def __init__(self):
        pass

from application import clients, BaseItem, CustomLogger, zen_help


def sync_zendesk_fields():
    """

    Args:
        field (str): which zendesk field to update (device, repair)

    Returns:
        prints 'Success' or 'Failure'
    """

    keys = {  # contains Zendesk Ticket Field IDs to adjust
        'repairs': 360008842297,
        'device': 4413411999249,
        'client': 360010408778,
        'service': 360010444117,
        'repair_type': 360010444077
    }


    fields = [item for item in keys]

    # get Eric item for column info
    mon_item = BaseItem(CustomLogger(), item_id_or_mon_item=1290815635)

    for attribute in fields:

        url = f"https://icorrect.zendesk.com/api/v2/ticket_fields/{keys[attribute]}"

        ids_with_names = []
        col = getattr(mon_item, attribute)
        for setting in col._settings:
            try:
                ids_with_names.append([str(int(setting)), str(col._settings[setting])])
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

        print()




sync_zendesk_fields()

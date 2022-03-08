from datetime import datetime, timedelta


def multi_select_refurb_options():
    """returns a formatted Slack message block that quotes data regarding the repair in question and the stock available,
    with the response queuing actions within Eric"""

    return {'blocks': [
        {
            "type": "input",
            "element": {
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Can we Refurb This In Time?",
                    "emoji": True
                },
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Part Can Be Refurbed In Time",
                            "emoji": True
                        },
                        "value": "value-0"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Cannot Be Refurbed",
                            "emoji": True
                        },
                        "value": "value-1"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Do Not Have the Required Components",
                            "emoji": True
                        },
                        "value": "value-2"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Refurb Is Possible, but Do Not Have The Time",
                            "emoji": True
                        },
                        "value": "value-2"
                    }
                ],
                "action_id": "static_select-action"
            },
            "label": {
                "type": "plain_text",
                "text": "Reply:",
                "emoji": True
            }
        }
    ]
    }


def multi_select_refurb_message(main_item, list_of_parts):
    mon_id = main_item.mon_id
    name = main_item.name
    b_date = main_item.booking_date.value
    if b_date:
        dt_ob = datetime.strptime(b_date, '%Y-%m-%d %H:%M')
        change = timedelta(hours=2)
        d_date = dt_ob - change
        d_date = d_date.strftime("%d %b %y %H:%M")
    else:
        b_date = 'Not Provided'
        d_date = 'No Booking Date - Cannot Provide Refurb Deadline'

    parts_formatted = "\n".join(f'{item.name}: {item.stock_level.value}' for item in list_of_parts)

    response_blocks = multi_select_refurb_options()

    message = f"*Low Stock Notification*\nWe have received a repair for " \
              f"<https://icorrect.monday.com/boards/349212843/pulses/{mon_id}|{name}> that we do " \
              f"not have the stock for.\n\n*Refurbishment Deadline*:\n{d_date}\n*Booking Date/Time*:\n{b_date}\n\n" \
              f"*Required Parts*:\n{parts_formatted} "

    header = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": message
        }
    }

    response_blocks.insert(0, header)

    return response_blocks


def resp_test():
    dct = {
        "blocks": [{
            "type": "actions",
            "elements": [{
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select an item",
                    "emoji": True
                },
                "options": [{
                    "text": {
                        "type": "plain_text",
                        "text": "Option1",
                        "emoji": True
                    },
                    "value": "value-0"
                },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Option2",
                            "emoji": True
                        },
                        "value": "value-1"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Option3",
                            "emoji": True
                        },
                        "value": "value-2"
                    }
                ],
                "action_id": "actionId-3"
            }
            ]
        }
        ]
    }
    return dct
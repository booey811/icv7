import json
import base64
import os
import requests

from application import BaseItem


def send_direct_request(data, url, method, as_json=True):
    def encode_to_64(string):
        string_bytes = string.encode("ascii")
        b64_bytes = base64.b64encode(string_bytes)
        b64_string = b64_bytes.decode("ascii")

        return b64_string

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + encode_to_64(f"admin@icorrect.co.uk/token:{os.environ['ZENDESKADMIN']}")
    }

    if as_json:
        data = json.dumps(data)

    r = requests.request(method, url, headers=headers, data=data)

    return r


def sync_fields(main_board_item:BaseItem):
    """This function will accept a Main Board Monday Item and sync IMEI, passcode, device, repairs, clients, service,
    type

    Args:
        main_board_item (BaseItem): the main board item to sync"""

    pass

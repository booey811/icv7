import json
import base64
import os
import requests

from zenpy.lib.api_objects import User

from application import clients


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


def user_search(eric_object_with_email, logger, name=None):

    def create_user(name, email, phone, logger):

        if phone:
            logger.log(f"Creating Zen User with {name} {email} {phone}")
            user_temp = User(
                name=name,
                email=email,
                phone=phone
            )
        else:
            logger.log(f"Creating Zen User with {name} {email}")
            user_temp = User(
                name=name,
                email=email
            )
        zen_user = clients.zendesk.users.create(user_temp)
        return zen_user

    # extract data from eric object
    name = eric_object_with_email.name
    phone = 0
    try:
        email = eric_object_with_email.email.value
    except AttributeError:
        logger.log(f"Eric Item[{eric_object_with_email.mon_id}] has no email attribute")
        logger.hard_log()
        raise Exception("User Search Hard Log")
    try:
        phone = eric_object_with_email.phone.value
    except AttributeError:
        logger.log(f"Eric Item[{eric_object_with_email.mon_id}] has no email attribute")
        logger.soft_log()

    # begin user search

    logger.log(f"Searching for Zendesk user: {email}")
    results = clients.zendesk.search(user=email)
    logger.log(f"Found {len(results)} Users")

    if len(results) == 1:
        user = [item for item in results][0]
        logger.log(f"Found user {user.id}")
    elif len(results) > 1:
        logger.log("Found Too Many Users - Raising Exception")
        logger.hard_log()
        raise Exception
    elif len(results) == 0 and name:
        logger.log("No results found")
        user = create_user(name, email, phone, logger)
    else:
        raise Exception
    return user

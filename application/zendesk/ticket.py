import os
from typing import Union
import base64
import json

import requests
import zenpy.lib.api_objects
from zenpy.lib.exception import RecordNotFoundException

from application.utilities import clients
from . import exceptions


class EricTicket:

    def __init__(self, logger, ticket_id_or_obj):
        self.logger = logger

        if type(ticket_id_or_obj) is str or type(ticket_id_or_obj) is int:
            self.zenpy_ticket = get_zenpy_ticket(logger, ticket_id_or_obj)
        elif type(ticket_id_or_obj) is zenpy.lib.api_objects.Ticket:
            self.zenpy_ticket = ticket_id_or_obj
        else:
            raise Exception(
                f'EricTicket Instantiated with {type(ticket_id_or_obj)} - should be str, int or Zenpy Ticket')

        self.id = self.zenpy_ticket.id

        self.user = process_requester_data(self.logger, self.zenpy_ticket)

        self.organisation = process_organisation_data(self.logger, self.zenpy_ticket)


def get_zenpy_ticket(logger, ticket_id: Union[str, int]):
    """
    Gets Zenpy Ticket object from Zendesk when supplied with a ticket ID, raises exception if cannot find
    Args:
        logger: CustomLogger object
        ticket_id: Zendesk Ticket ID

    Returns:
        zenpy.lib.api_objects.Ticket: Zenpy ticket Object
    """
    try:
        logger.log(f"Searching for ticket[{ticket_id}]")
        zenpy_ticket = clients.zendesk.tickets(id=ticket_id)
        return zenpy_ticket
    except RecordNotFoundException:
        logger.log("Could not find ticket")
        logger.hard_log()
        raise exceptions.TicketNotFound(ticket_id)


def process_requester_data(logger, zenpy_ticket_obj: zenpy.lib.api_objects.Ticket):
    """
    Processes requetser data into Eric friendly values
    Args:
        logger: CustomLogger Object
        zenpy_ticket_obj: Zenpy Ticket Object

    Returns:
        dict: Dict of requester data
    """
    if zenpy_ticket_obj.requester:
        logger.log("Requester Data Found")
        basic = {
            "name": zenpy_ticket_obj.requester.name,
            "id": zenpy_ticket_obj.requester.id,
            "email": zenpy_ticket_obj.requester.email,
            "phone": zenpy_ticket_obj.requester.phone,
            "pickup_instructions": zenpy_ticket_obj.requester.user_fields["company_flat_number"],
            "street_address": zenpy_ticket_obj.requester.user_fields["street_address"],
            "post_code": zenpy_ticket_obj.requester.user_fields["post_code"],
            "tags": list(zenpy_ticket_obj.requester.tags)
        }

        return basic

    else:
        logger.log("No Requester Data Found")
        return {}


def process_organisation_data(logger, zenpy_ticket_obj: zenpy.lib.api_objects.Ticket):
    """takes organisation info from Zenpy Object and returns nicely formatted dictionary

    Args:
        logger: CustomLogger Object
        zenpy_ticket_obj: Zenpy Object

    Returns:
        dict: organisation info (if any) or empty dictionary
    """

    if zenpy_ticket_obj.organization:
        logger.log("Organisation Data found")
        return {
            "name": zenpy_ticket_obj.organization.name,
            "id": zenpy_ticket_obj.organization.id,
            "pickup_instructions": zenpy_ticket_obj.organization.organization_fields["company_flat_number"],
            "street_address": zenpy_ticket_obj.organization.organization_fields["street_address"],
            "post_code": zenpy_ticket_obj.organization.organization_fields["postcode"],
            "terms": zenpy_ticket_obj.organization.organization_fields["billing_terms"],
            "payment_method": zenpy_ticket_obj.organization.organization_fields["payment_method"],
            "account_status": zenpy_ticket_obj.organization.organization_fields["account_status"]
        }
    else:
        logger.log("No Organisation Data found")
        return {}


def update_custom_field():

    def encode_to_64(string):

        string_bytes = string.encode("ascii")
        b64_bytes = base64.b64encode(string_bytes)
        b64_string = b64_bytes.decode("ascii")

        return b64_string



    url = "https://icorrect.zendesk.com/api/v2/ticket_fields/4413411999249"  # 4413411999249 ID for device field

    method = "PUT"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + encode_to_64(f"admin@icorrect.co.uk/token:{os.environ['ZENDESKADMIN']}")
    }

    data = {"ticket_field": {
                "custom_field_options": [
                    {"name": "Apple Pie", "value": "apple"},
                    {"name": "Pecan Pie", "value": "pecan"}
                ]
            }
        }

    r = requests.request(method, url, headers=headers, data=json.dumps(data))

    print()


update_custom_field()
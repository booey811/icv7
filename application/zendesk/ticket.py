import os
from typing import Union

from zenpy.lib.api_objects import CustomField, Ticket
from zenpy.lib.exception import RecordNotFoundException

from application.utilities import clients
from . import exceptions, config


class EricTicket:

    def __init__(self, logger, ticket_id_or_obj):
        self.logger = logger

        if type(ticket_id_or_obj) is str or type(ticket_id_or_obj) is int:
            self.zenpy_ticket = get_zenpy_ticket(logger, ticket_id_or_obj)
        elif type(ticket_id_or_obj) is Ticket:
            self.zenpy_ticket = ticket_id_or_obj
        else:
            raise Exception(
                f'EricTicket Instantiated with {type(ticket_id_or_obj)} - should be str, int or Zenpy Ticket')

        self.id = self.zenpy_ticket.id

        self.user = process_requester_data(self.logger, self.zenpy_ticket)

        self.organisation = process_organisation_data(self.logger, self.zenpy_ticket)

        for field in self.zenpy_ticket.custom_fields:
            try:
                eric_field = TicketField(field, self.zenpy_ticket)
                setattr(self, eric_field.attribute, eric_field)
            except KeyError:
                pass

    def add_tags(self, list_of_tags: list):
        self.logger.log(f"Adding Tags: {list_of_tags}")
        self.zenpy_ticket.tags.extend(list_of_tags)

    def set_tags(self, list_of_tags: list):
        self.logger.log(f"Setting Tags: {list_of_tags}")
        self.zenpy_ticket.set_tags(list_of_tags)

    def commit(self):
        self.logger.log("Committing Ticket Changes")
        audit = clients.zendesk.tickets.update(self.zenpy_ticket)
        return audit.ticket


class TicketField:

    def __init__(self, zenpy_custom_field_dict, zenpy_ticket):
        self.id = zenpy_custom_field_dict["id"]
        self.zenpy_ticket = zenpy_ticket
        self.attribute = config.TICKET_FIELDS[str(self.id)][0]
        self.value = zenpy_custom_field_dict["value"]
        self.type = config.TICKET_FIELDS[str(self.id)][1]

    def adjust(self, value):
        if self.type == "text":
            return self._adjust_text(value)
        elif self.type == "dropdown":
            self._adjust_select(value)
        elif self.type == "multi":
            self._adjust_select(value)
        else:
            raise Exception("Unexpected Zendesk Ticket Field Type Received")

    def _adjust_text(self, value):
        if type(value) is not str:
            raise Exception("Cannot Adjust Text Value with anything but string")
        self.zenpy_ticket.custom_fields.append(CustomField(id=self.id, value=value))

    def _adjust_select(self, value_tag):
        self.zenpy_ticket.tags.extend([value_tag])


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


def process_requester_data(logger, zenpy_ticket_obj: Ticket):
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


def process_organisation_data(logger, zenpy_ticket_obj: Ticket):
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

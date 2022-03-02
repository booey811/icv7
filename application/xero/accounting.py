import base64
import os
import json
from urllib.parse import quote_plus
from typing import Union
import datetime

import requests

import settings
from . import exceptions
from application import BaseItem, EricTicket

COURIER_PRICES = {
    "Courier": {
        "Standard": 14,  # ex VAT
        "Expedited": 24,  # ex VAT
    },
    "Mail-In": 24  # ex VAT
}


class Authorizer:
    def __init__(self):
        self.id = os.environ["XEROCCID"]
        self.secret = os.environ["XEROCCSECRET"]
        self._access = ""

    @property
    def access(self):
        if self._access:
            return self._access
        else:
            self.request_token()
            return self._access

    @access.setter
    def access(self, value):
        self._access = value

    def request_token(self):

        def encode_secret_to_64():

            string = f"{self.id}:{self.secret}"
            string_bytes = string.encode("ascii")
            b64_bytes = base64.b64encode(string_bytes)
            b64_string = b64_bytes.decode("ascii")

            return b64_string

        url = "https://identity.xero.com/connect/token"

        headers = {
            "Authorization": f"Basic {encode_secret_to_64()}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        body = {
            "grant_type": "client_credentials",
            "scope": "accounting.transactions accounting.contacts"
        }

        response = requests.request(url=url, method="POST", headers=headers, data=body)

        if response.status_code == 200:
            info = json.loads(response.text)
            self.access = info["access_token"]
            return response
        else:
            raise Exception(f"Xero Authorisation Returned non-200 Response: {response.text}")


_auth = Authorizer()


def _send_request(url, method, body: dict = None, params=None):
    headers = {
        "Authorization": f"Bearer {_auth.access}",
        "Accept": "application/json"
    }

    if body:
        response = requests.request(method=method, url=url, headers=headers, data=json.dumps(body))
    elif params:
        response = requests.request(method=method, url=url, headers=headers, params=params)
    else:
        response = requests.request(method=method, url=url, headers=headers)

    return response


def get_contact(contact_id_or_zendesk_organisation_number, limit=None):
    """Takes Xero COntact ID or Zendesk Orgabnisation ID and gets the relevant Xero entities, returning a list

    Args:
        limit (int): the maximum number of contacts to return, starting from the first
        contact_id_or_zendesk_organisation_number (str): xero contact ID or Zendesk organisation ID
    """

    # Construct and Send Request
    url = f"https://api.xero.com/api.xro/2.0/Contacts/{contact_id_or_zendesk_organisation_number}"
    method = "GET"
    result = _send_request(url, method)

    # Analyse response
    if result.status_code == 200:
        contact = json.loads(result.text)
    else:
        raise Exception('xero.get_contact returned non-200 response')

    # Construct & return desired return value
    if limit:
        index = limit - 1
        return contact["Contacts"][:index]
    else:
        return contact["Contacts"]


def edit_contact(edited_contact_object):
    """Commits local changes of contact to Xero Contact entity"""

    url = "https://api.xero.com/api.xro/2.0/Contacts"
    method = "POST"

    result = _send_request(url=url, method=method, body=edited_contact_object)


def get_invoice(invoice_id):
    """Gets a Xero invoice via the specified ID"""
    url = f"https://api.xero.com/api.xro/2.0/Invoices/{invoice_id}"
    method = "GET"

    result = _send_request(url, method)

    if result.status_code == 200:
        info = json.loads(result.text)
    else:
        raise Exception('xero.get_invoice returned a non-200 response')

    return info


def get_draft_invoices_for_contact(contact_id_or_zendesk_organisation_number):
    url = f"https://api.xero.com/api.xro/2.0/Invoices?ContactIDs={contact_id_or_zendesk_organisation_number}&Statuses=DRAFT"
    method = "GET"

    result = _send_request(url, method)

    if result.status_code == 200:
        info = json.loads(result.text)
    else:
        raise Exception('xero.get_drafts returned a non-200 response')
    return info


def update_invoice(invoice):
    url = f"https://api.xero.com/api.xro/2.0/Invoices"
    method = 'POST'

    for item in invoice["LineItems"]:
        try:
            if item["ItemCode"] == "placeholder":
                invoice["LineItems"].remove(item)
        except KeyError:
            pass

    result = _send_request(url, method, body=invoice)

    if result.status_code == 200:
        info = json.loads(result.text)
    else:
        raise Exception('xero.update_invoice returned a non-200 response')
    return info["Invoices"][0]


def generate_line_item_dict(values_list):
    """takes data genrated by construct liune item functions and formats to Xero friendly Line item dict"""

    dct = {
        "Description": values_list[0],
        "Quantity": 1,
        "UnitAmount": values_list[1],
        "AccountCode": values_list[2]
    }

    return dct


def construct_repair_line_item(financial_item, subitems: list, main, ticket):
    """constructs the description and price of a financial board entry through amalgamation of subitems"""

    if not subitems:
        raise exceptions.FinancialError(financial_item, "No Repair Profile")

    device = f"{str(main.device.labels[0])} "
    repairs = ", ".join(main.repairs.labels)

    description1 = device + repairs + " Repair"
    description2 = f"IMEI/SN: {main.imeisn.value}"
    description3 = f"Arranged By: {ticket.user['name']}"
    description4 = f"Date of Repair: {main.repaired_date.value}"

    line_total = 0
    for subitem in subitems:
        line_amount = subitem.sale_price.value
        line_total += line_amount
        if not line_amount:
            raise exceptions.FinancialError(financial_item, "No Sale Price")

    full_desc = "\n".join([description1, description2, description3, description4])

    line_total = line_total * 0.8

    return generate_line_item_dict([full_desc, line_total, 203])


def construct_courier_line_item(main_item, corporate_item):
    service = main_item.service.label
    service_level = corporate_item.courier_service_level.label

    if service == "Courier":
        try:
            cost = COURIER_PRICES[service][service_level]
            description = f"{corporate_item.courier_service_level.label} London Courier Service"
        except KeyError:
            raise Exception(f"Construct Courier Costs Received Unexpected Service Level: {service_level}")
    elif service == "Mail-In":
        cost = COURIER_PRICES[service]
        description = "National Courier Service"
    else:
        raise Exception(f"Construct Courier Costs Received Unexpected Service Type: {service}")

    return generate_line_item_dict([description, cost, 220])


def create_invoice(corporate_item, line_items=(), monthly=False):
    url = f"https://api.xero.com/api.xro/2.0/Invoices"
    method = "POST"

    line_items = list(line_items)

    issue_date = datetime.datetime.now()

    issue_day = issue_date.strftime("%d")
    issue_month = issue_date.strftime("%m")
    issue_year = issue_date.strftime("%Y")

    if monthly:
        issue_date = datetime.datetime(int(issue_year), int(issue_month), 31)
        issue_day = issue_date.strftime("%d")
        issue_month = issue_date.strftime("%m")
        issue_year = issue_date.strftime("%Y")

    due_date = issue_date + datetime.timedelta(days=30)

    due_day = due_date.strftime("%d")
    due_month = due_date.strftime("%m")
    due_year = due_date.strftime("%Y")

    month_str = issue_date.strftime("%B")

    dct = {
        "Type": "ACCREC",
        "Contact": {
            "ContactID": corporate_item.xero_contact_id.value
        },
        "Date": f"{issue_year}-{issue_month}-{issue_day}",
        "DueDate": f"{due_year}-{due_month}-{due_day}",
        "LineAmountTypes": "Exclusive",
        "Reference": f"Apple Device Repairs {month_str} {issue_year}",
        "LineItems": []
    }

    if line_items:
        dct["LineItems"] = line_items
    else:
        dct["LineItems"] = [{
            "ItemCode": 'placeholder'
        }]

    result = _send_request(url, method, body=dct)

    if result.status_code == 200:
        info = json.loads(result.text)
    else:
        raise Exception('xero.create_invoice returned a non-200 response')

    return info["Invoices"][0]

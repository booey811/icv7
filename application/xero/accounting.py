import base64
import os
import json
from urllib.parse import quote_plus

import requests

import settings


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
            self._access = self.request_token()
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
            return info["access_token"]
        else:
            raise Exception(f"Xero Authorisation Returned non-200 Response: {response.text}")


_auth = Authorizer()


def _send_request(url, method, body=None, params=None):
    headers = {
        "Authorization": f"Bearer {_auth.access}",
        "Accept": "application/json"
    }

    if body:
        response = requests.request(method=method, url=url, headers=headers, data=body)
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


def get_invoice(invoice_id):
    url = f"https://api.xero.com/api.xro/2.0/Invoices/{invoice_id}"
    method = "GET"
    result = _send_request(url, method)
    return result

def get_draft_invoices_for_contact(contact_id_or_zendesk_organisation_number):

    url_base = f"https://api.xero.com/api.xro/2.0/Invoices?ContactIDs={contact_id_or_zendesk_organisation_number}&Statuses=DRAFT"
    method = "GET"

    result = _send_request(url_base, method)

    if result.status_code == 200:
        info = json.loads(result.text)
    else:
        raise Exception('xero.get_drafts returned a non-200 response')
    return info

get_draft_invoices_for_contact("496881b2-956b-4ec2-a4e4-201628e3a0e0")
import os

import moncli.api_v2
from moncli.entities import MondayClient
from zenpy import Zenpy

from . import BaseItem, EricTicket


def create_monday_client(user: str = 'system') -> MondayClient:
    """
Function to create and return a moncli client relating to the specified user

    :param user: the user to create the client as (default 'system')
    :return: MondayClient created with requested user credentials
    """
    if user == 'error':
        key = os.getenv('MONV2ERR')
    elif user == 'email':
        key = os.getenv('MONV2EML')
    elif user == 'system':
        key = os.getenv('MONV2SYS')
    else:
        raise Exception(f'"{user}" provided as user for Moncli client, not valid')

    client = MondayClient()
    client.api_key_v2 = key
    return client


def create_zendesk_client():
    creds = {
        "email": 'admin@icorrect.co.uk',
        "token": os.environ["ZENDESKADMIN"],
        "subdomain": "icorrect"
    }
    client = Zenpy(
        email='admin@icorrect.co.uk',
        token=os.environ["ZENDESKADMIN"],
        subdomain="icorrect"
    )
    return client


class MondayClientCollection:

    def __init__(self):
        self._system = None
        self._error = None
        self._email = None

    @property
    def system(self) -> MondayClient:
        """
Used to access the Monday Client acting as the 'System' User
This is the default client to be used for Monday interactions
        :return: Monday 'System' Client
        """
        if self._system:
            return self._system
        else:
            self.system = create_monday_client()
            return self._system

    @system.setter
    def system(self, monday_client):
        """
Used to set the Monday Client for the 'System' User
        :param monday_client: The 'System' Monday Client
        """
        self._system = monday_client

    @property
    def email(self) -> MondayClient:
        """
Used to access the Monday Client acting as the 'Email' User
        :return: Monday 'Email' Client
        """
        if self._email:
            return self._email
        else:
            self.email = create_monday_client('email')
            return self._email

    @email.setter
    def email(self, monday_client):
        """
    Used to set the Monday Client for the 'Email' User
        :param monday_client: The 'Email' Monday Client
        """
        self._email = monday_client

    @property
    def error(self) -> MondayClient:
        """
Used to access the Monday Client acting as the 'Error' User
        :return: Monday 'Email' Client
        """
        if self._error:
            return self._error
        else:
            self._error = create_monday_client('error')
            return self._error

    @error.setter
    def error(self, monday_client):
        """
    Used to set the Monday Client for the 'Error' User
        :param monday_client: The 'Error' Monday Client
        """
        self._error = monday_client


class ClientsObject:
    def __init__(self):
        self.monday = MondayClientCollection()
        self.zendesk = create_zendesk_client()


def sync_fields(main_board_item: BaseItem = None, eric_ticket=None):
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
        main.log(f"Syncing Fields Main[{main.id}] | Zen[{zen.id}]")
    elif main_board_item:  # monday item supplied only
        main = main_board_item
        main.log(f"Syncing Zen Fields Main[{main.id}]: Acquiring Zendesk Ticket")
        if not main.zendesk_id.value:  # check for zendesk ID
            main.log(f"Unable to Sync to Zendesk: No ID on Mon[{main.id}]")
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
        raise Exception("sync_fields else route")

    # list and get syncable attributes
    attributes = ['imeisn', 'device', 'repairs', '']


class SyncErrorNoZendeskID(Exception):

    def __init__(self):
        pass


clients = ClientsObject()

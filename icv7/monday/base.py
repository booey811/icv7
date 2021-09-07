import os

from moncli.entities import MondayClient

import settings


def create_client(user: str = 'system') -> MondayClient:
    """
Function to create and return a moncli client relating to the specified user

    :param user: the user to create the client as (default 'system')
    :return: MondayClient created with requested user credentials
    """
    print(f'creating {user} client')
    if user == 'error':
        key = os.getenv('MONV2ERR')
    elif user == 'email':
        key = os.getenv('MONV2EML')
    elif user == 'system':
        key = os.getenv('MONV2SYS')
    else:
        raise Exception(f'{user} provided as user for Moncli client, not valid')

    client = MondayClient()
    client.api_key_v2 = key
    return client


class ClientForMonday:

    def __init__(self):
        print('init')
        self._system = None
        self._error = create_client('error')
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
            self.system = create_client()
            return self._system

    @system.setter
    def system(self, monday_client):
        """
Used to set the Monday Client for the 'System' User
        :param monday_client: The 'System' Monday Client
        """
        print('setting system')
        self._system = monday_client

    @property
    def email(self) -> MondayClient:
        """
Used to access the Monday Client acting as the 'Email' User
        :return: Monday 'Email' Client
        """
        print('getting email')
        if self._email:
            return self._email
        else:
            self.email = create_client('email')
            return self._email

    @email.setter
    def email(self, monday_client):
        """
    Used to set the Monday Client for the 'Email' User
        :param monday_client: The 'Email' Monday Client
        """
        print('setting email')
        self._email = monday_client

    @property
    def error(self) -> MondayClient:
        """
Used to access the Monday Client acting as the 'Error' User
        :return: Monday 'Email' Client
        """
        print('getting error')
        if self._error:
            return self._error
        else:
            self.error = create_client('error')

    @error.setter
    def error(self, monday_client):
        """
    Used to set the Monday Client for the 'Error' User
        :param monday_client: The 'Error' Monday Client
        """
        print('setting error')
        self._error = monday_client


test = ClientForMonday()

test.email.get_board_by_id('349212843')

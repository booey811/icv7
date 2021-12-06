import pytest

from application.utilities import ClientsObject

from moncli.entities import MondayClient
from zenpy import Zenpy


@pytest.fixture(scope='function')
def clients_object():
    return ClientsObject()


@pytest.mark.parametrize('client_name', ['system', 'error', 'email'])
def test_monday_clients_are_instantiated_correctly(client_name, clients_object):
    assert type(getattr(clients_object.monday, client_name)) == MondayClient


@pytest.mark.parametrize('client_name', ['system', 'error', 'email'])
def test_monday_clients_are_authorised(client_name, clients_object):
    client = getattr(clients_object.monday, client_name)
    test_item = client.get_items('id', ids=[1649471278])[0]
    assert test_item.id == '1649471278'


def test_zendesk_client_is_instantiated_correctly(clients_object):
    assert type(clients_object.zendesk) is Zenpy

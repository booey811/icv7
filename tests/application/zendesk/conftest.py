import pytest

from application.zendesk.ticket import get_zenpy_ticket, EricTicket


@pytest.fixture(scope="module")
def zenpy_ticket(logger):
    ticket = get_zenpy_ticket(logger, 13421)
    return ticket


@pytest.fixture(scope="module")
def eric_ticket(logger, zenpy_ticket):
    return EricTicket(logger, zenpy_ticket)


def test_zenpy_ticket_fixture(zenpy_ticket):
    assert zenpy_ticket.id == 13421  # Test ticket ID
    assert zenpy_ticket.requester_id == 1904191859233  # Test User (Luong Huang) ID

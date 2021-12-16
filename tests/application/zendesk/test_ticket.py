import pytest


def test_eric_ticket_is_instantiated(eric_ticket):
    assert eric_ticket.id == 13421  # Test ticket ID
    assert eric_ticket.user["id"] == 1904191859233  # Test User (Luong Huang) ID


def test_organisation_data_is_pulled_correctly(eric_ticket):
    org_data = eric_ticket.organisation

    assert org_data["id"] == 1900073690753  # Test Company 1 ID
    assert org_data["name"] == "Test Company 1"


def test_user_data_is_pulled_correctly(eric_ticket):

    user_data = eric_ticket.user

    assert user_data["name"] == "Luong Huang"
    assert user_data["id"] == 1904191859233

import pytest

from application.xero import accounting


@pytest.fixture
def xero_authenticator():
    return accounting.Authorizer()


@pytest.fixture(scope='module')
def xero_test_company_1():
    contact = accounting.get_contact("e0ec5aa1-557f-4e67-8822-3dd031c94a77")[0]  # Xero contact ID for Test Company 1
    yield contact

    contact["ContactNumber"] = 1900073690753  # Zendesk Organisation ID for Test Company 1
    accounting.edit_contact(contact)


def test_xero_test_company_1_fixture_works(xero_test_company_1):
    assert xero_test_company_1[
               'ContactID'] == "e0ec5aa1-557f-4e67-8822-3dd031c94a77"  # Xero contact ID for Test Company 1


def test_authorization_returns_200_response(xero_authenticator):
    result = xero_authenticator.request_token()
    assert result.status_code == 200


def test_get_contact_fetches_one_contact_by_id():
    contacts = accounting.get_contact("e0ec5aa1-557f-4e67-8822-3dd031c94a77")  # Xero contact ID for Test Company 1
    assert len(contacts) == 1



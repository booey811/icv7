import pytest

from application.xero import accounting


@pytest.fixture
def xero_authenticator():
    return accounting.Authorizer()


def test_authorization_returns_200_response(xero_authenticator):
    result = xero_authenticator.request_token()

    assert result == 200

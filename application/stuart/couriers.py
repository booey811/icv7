import requests
import os
import json

import settings

if os.environ["FORCE_STUART_PROD"] == "true":
	_BASE_URL = "https://api.stuart.com"
	_CLIENT_ID = os.environ["STUART_ID_PROD"]
	_CLIENT_SECRET = os.environ["STUART_SECRET_PROD"]

elif os.environ["ENV"] != 'devlocal':
	_BASE_URL = "https://api.stuart.com"
	_CLIENT_ID = os.environ["STUART_ID_PROD"]
	_CLIENT_SECRET = os.environ["STUART_SECRET_PROD"]

else:
	_BASE_URL = "https://api.sandbox.stuart.com"
	_CLIENT_ID = os.environ["STUART_ID_SAND"]
	_CLIENT_SECRET = os.environ["STUART_SECRET_SAND"]


class AuthObject:

	def __init__(self):
		self._token = None
		self._refresh_token()

	def _refresh_token(self):
		url = _BASE_URL + "/oauth/token"
		headers = {'content-type': 'application/x-www-form-urlencoded'}
		body_raw = {
			"client_id": _CLIENT_ID,
			"client_secret": _CLIENT_SECRET,
			"scope": "api",
			"grant_type": "client_credentials"
		}
		result = requests.request("POST", url=url, data=body_raw, headers=headers)
		self._token = json.loads(result.text)["access_token"]
		return self._token

	def get_token(self):
		result = self.test_auth()
		if result.status_code == 200:
			return self._token
		elif result.status_code == 422:
			self._refresh_token()
			with_new_token = self.test_auth()
			if with_new_token.status_code != 200:
				raise Exception(f"Stuart Auth Failed Repeatedly: {with_new_token.status_code} | {with_new_token.text}")
			return self._token
		else:
			raise Exception(
				f"Stuart Authorization Failed with Unexpected Status Code: {result.status_code} | {result.text}")

	def test_auth(self):
		url = _BASE_URL + "/health"
		headers = {'Authorization': f"Bearer {self._token}"}
		response = requests.request(
			method="GET",
			url=url,
			headers=headers
		)
		return response


auth = AuthObject()


def _get_token():
	return auth.get_token()


def _send_request(url, body_dict: dict = None, method="POST", additional_headers: dict = None):
	headers = {"Authorization": f"Bearer {_get_token()}"}

	if additional_headers is None:
		headers = headers
	else:
		headers = headers | additional_headers

	if body_dict is None:
		body_dict = {}
		body = body_dict
	else:
		body = json.dumps(body_dict)

	response = requests.request(
		method=method,
		url=url,
		data=body,
		headers=headers
	)

	if response.status_code == 401:
		headers = {"Authorization": f"Bearer {_get_token()}"}
		response = requests.request(
			method=method,
			url=url,
			data=body,
			headers=headers
		)

	return response


def get_job_data(job_id):
	url = _BASE_URL + f"/v2/jobs/{job_id}"
	result = _send_request(url, method="GET")
	return json.loads(result.text)

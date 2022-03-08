import requests
import json
import os

BASE_URL = "https://slack.com/api/"

HEADERS = {
    "Authorization": f"Bearer {os.environ['SLACKBOT']}",
    "Content-Type": "application/json"
}

TEST_CHANNEL = "C036M43NBR6"


def _test_auth():
    url = "auth.test"
    method = 'POST'

    info = _send_request(method, url)

    return info


def _send_request(method, url_end, json_data=None):
    """base function for sending Slack requests - attaches url_end to BASEURL, converts data (if supplied) and
    analyses response"""

    url = BASE_URL + url_end

    if json_data:
        data = json.dumps(json_data)
    else:
        data = None

    if data:
        response = requests.request(method=method, url=url, headers=HEADERS, data=data)
    else:
        response = requests.request(method=method, url=url, headers=HEADERS)

    if response.status_code == 200:
        print("success")
        result = json.loads(response.text)
        return result

    else:
        print('failure')
        print(json.loads(response.text))
        return False


def list_conversations():
    url = "conversations.list"
    method = "GET"

    info = _send_request(method, url)

    return info


def post_message(list_of_blocks, channel=TEST_CHANNEL):
    url = 'chat.postMessage'
    method = 'POST'

    body = {
        'channel': channel,
        'blocks': list_of_blocks,
        'unfurl_media': False
    }

    info = _send_request(method, url, json_data=body)

    return info

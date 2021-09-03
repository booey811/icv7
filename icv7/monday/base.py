import os

from moncli import client

import settings

my_key = os.getenv('MONV2SYS')

client.api_key_v2 = my_key


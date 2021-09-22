from icv7 import create_app
from icv7.monday import BaseItem
from icv7.utilities import clients

test_board_id = 1139943160

test_item_id = 1139943185

test_mon_item = clients.monday.system.get_items(ids=[1139943185])[0]

b_item = BaseItem(board_id=test_board_id)

id_item = BaseItem(test_item_id)

i_item = BaseItem(test_mon_item)
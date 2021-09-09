from icv7.utilities import clients
from .columns import BaseColumnCollection

system = clients.monday.system

test_board_id = 1139943160

board = system.get_boards('name', 'items.name', ids=[test_board_id])[0]

test_item_id = 1139943185


def create_column_collection(board_id) -> BaseColumnCollection:
    pass


class BaseItem:
    def __init__(self, item_id):
        self.moncli_obj = clients.monday.system.get_items(get_column_values=True, ids=[item_id])[0]
        self.id = str(item_id)

        self.columns = create_column_collection(self.moncli_obj)

    def stage_changes(self, changes_list: list[str, (int,str)]):

        # Validate input and convert to list of lists (if not provided in this format)
        if len(changes_list) == 2:
            to_change = [changes_list]
        elif len(changes_list) == 1:
            raise Exception(f'stage_changes provided with only list of length 1: {changes_list[0]} - requires column '
                            f'AND value to change to')
        else:
            to_change = changes_list

        for column_pair in to_change:
            column_id = column_pair[0]
            desired_value = column_pair[1]
            self.columns.stage_change(column_id, desired_value)


    def commit_changes(self):
        pass



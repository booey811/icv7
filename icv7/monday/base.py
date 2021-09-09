from icv7.utilities import clients
from icv7.monday.columns import BaseColumnCollection

system = clients.monday.system

test_board_id = 1139943160

board = system.get_boards('name', 'items.name', ids=[test_board_id])[0]

test_item_id = 1139943185


class BaseItemStructure:
    def __init__(self, item_id: str = None, board_id: str = None):
        self.moncli_obj = None
        self.name = ''
        self.id = ''
        self.columns = BaseColumnCollection


class BaseItem(BaseItemStructure):

    def __init__(self, item_id: str = None, board_id: str = None):
        super().__init__(item_id, board_id)

        if not item_id and not board_id:
            raise Exception('Cannot Instantiate BaseItem without item_id or board_id')
        elif item_id:
            self.moncli_obj = clients.monday.system.get_items(get_column_values=True, ids=[item_id])[0]
            self.id = str(item_id)
            self.name = self.moncli_obj.name
            self.columns = BaseColumnCollection(self.moncli_obj.board['id'])
        elif board_id:
            self.columns = BaseColumnCollection(board_id)
        else:
            raise Exception('Unexpected Inputs for BaseItem.__init__')

    def stage_changes(self, changes_list: list[str, (int, str)]):

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


class ModuleTest:
    def __init__(self, monday_id):
        self.create_item(monday_id)

    def create_item(self, monday_id):
        item = BaseItem(monday_id)
        return item


ModuleTest(1649471278)

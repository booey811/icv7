from typing import Union

from icv7.utilities import clients
from icv7.monday.columns import BaseColumnCollection
from mappings import MappingObject
import config

system = clients.monday.system

test_board_id = 1139943160

board = system.get_boards('name', 'items.name', ids=[test_board_id])[0]

test_item_id = 1139943185


class BaseItemStructure:
    def __init__(self, item_id: Union[str, int] = '', board_id: Union[str, int] = ''):
        self._moncli_obj = None
        self._moncli_board_obj = None
        self._board_id = board_id

        self._id = item_id
        self.name = ''


class BaseItem(BaseItemStructure):

    def __init__(self, item_id: (str, int) = None, board_id: (str, int) = None, get_column_values=True):
        super().__init__(item_id, board_id)

        if not item_id and not board_id:
            raise Exception('Cannot Instantiate BaseItem without item_id or board_id')
        elif item_id:
            # Set basic info and private variables
            self._moncli_obj = clients.monday.system.get_items(get_column_values=get_column_values, ids=[item_id])[0]
            self._id = str(item_id)
            self._board_id = str(self._moncli_obj.board.id)
            self._moncli_board_obj = self._moncli_obj.board
            self.name = self._moncli_obj.name

            # Initialise mapping object for relevant board
            self._mapper = MappingObject(self._board_id)

            for mon_col in self._moncli_obj.column_values:
                try:
                    name = config.BOARD_MAPPING_DICT[self._board_id]['columns'][mon_col.id]
                    column = self._mapper.process_column(mon_col)
                    setattr(self, name, column)
                except KeyError:
                    print(f'Column ID "{mon_col.id}" not found in config.COLUMN_MAPPINGS[{self._board_id}]')


        elif board_id:
            self._board_id = str(board_id)
        else:
            raise Exception('Unexpected Inputs for BaseItem.__init__')

        def _process_column_value(moncli_col_val=None):
            """
            Returns an eric column value that can is assigned to the item during init
            :param moncli_col_val: column value to imprint the value of, providing column name and value
            :return: eric_col_val: eric's column value that provides column specific functionality
            """
            pass



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


item = BaseItem(1649471278)

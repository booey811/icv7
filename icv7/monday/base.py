from typing import Union

from icv7.utilities import clients
from .mappings import MappingObject
from .config import BOARD_MAPPING_DICT

system = clients.monday.system

test_board_id = 1139943160

test_item_id = 1139943185


class BaseItemStructure:
    def __init__(self, item_id: Union[str, int] = '', board_id: Union[str, int] = ''):
        self._moncli_obj = None
        self._moncli_board_obj = None
        self._board_id = board_id
        self._staged_changes = {}

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

            # Iterate through moncli columns with mapping object to instantiate columns on BaseItem
            for mon_col in self._moncli_obj.column_values:
                try:
                    print(f'from loop - column {mon_col.title}:{mon_col.id}')
                    name = BOARD_MAPPING_DICT[self._board_id]['columns'][mon_col.id]
                    column = self._mapper.process_column(mon_col, self._staged_changes)
                    setattr(self, name, column)
                except KeyError:
                    print(f'Column ID "{mon_col.id}" not found in config.COLUMN_MAPPINGS[{self._board_id}]')

        elif board_id:
            self._board_id = str(board_id)

        else:
            raise Exception('Unexpected Inputs for BaseItem.__init__')

    def commit(self):

        if not self._staged_changes:
            raise Exception('Attempting to Commit Changes with no Staged Changes')

        result = self._moncli_obj.change_multiple_column_values(self._staged_changes)

        return result

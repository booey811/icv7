from typing import Union, Callable
from datetime import datetime

import moncli.entities
from moncli.api_v2.exceptions import MondayApiError as moncli_error

from icv7.utilities import clients
from .mappings import MappingObject
from .config import BOARD_MAPPING_DICT
from icv7.monday import exceptions


class CustomLogger:

    def __init__(self, eric_item):
        self._log_file_path = None
        self._eric = eric_item
        self._log_name = self._generate_log_file_name()

    def _generate_log_file_name(self):
        now = datetime.now()
        date_time = now.strftime("%d%b|%H-%M-%S")
        name = f'{self._eric.id}|{date_time}.txt'
        return name

    @property
    def log_file_path(self):
        if not self._log_file_path:
            self._log_file_path = f'tmp/logs/{self._log_name}'
        return self._log_file_path

    def write_to_log(self, lines_to_write):
        with open(self.log_file_path, 'w+') as log:
            log.writelines(lines_to_write)

        return True


class BaseItemStructure:
    def __init__(self, item_id_or_mon_item: Union[str, int] = '', board_id: Union[str, int] = ''):
        self._moncli_obj = None
        self._moncli_board_obj = None
        self._board_id = board_id
        self.staged_changes = {}

        self.id = None
        self.name = ''


class BaseItem(BaseItemStructure):
    """This item is the main interface for the entire application"""

    def __init__(self,
                 item_id_or_mon_item: Union[str, int, moncli.entities.Item] = None,
                 board_id: Union[str, int] = None,
                 get_column_values=True):
        super().__init__(item_id_or_mon_item, board_id)

        # Check input is correct
        if not item_id_or_mon_item and not board_id:
            raise Exception('Cannot Instantiate BaseItem without item_id or mon_item or board_id')

        # Check instantiation type via input keywords
        elif item_id_or_mon_item:
            # Check if input is mon_item or item_id via try/except
            try:
                # Set basic info and private variables from item_id
                self._moncli_obj = \
                    clients.monday.system.get_items(get_column_values=get_column_values, ids=[item_id_or_mon_item])[0]
            except TypeError:
                # Set basic info and private variables from mon_item, triggers if input is not int or str
                self._moncli_obj = item_id_or_mon_item

            # Set derived basic info
            self.id = str(self._moncli_obj.id)
            self._moncli_board_obj = self._moncli_obj.board
            self.name = self._moncli_obj.name

            # Set columns
            columns = self._moncli_obj.column_values

        elif board_id:
            # Set basic info that can be taken from Board, columns
            self._moncli_board_obj = clients.monday.system.get_boards(ids=[self._board_id])[0]

            # Set columns
            columns = self._moncli_board_obj.columns

        else:
            raise Exception('Unexpected Inputs for BaseItem.__init__')

        self._board_id = str(self._moncli_board_obj.id)
        self._convert_column_data_to_eric_values(columns)

        # Setup Logger
        self.logger = CustomLogger(self)

    def _convert_column_data_to_eric_values(self, columns):
        """
        Processes column data taken from monday item or board IDs and sets up the eric item accordingly
        Prints out columns that are defined in the config file but not used
        :param columns:
        :return:
        """

        # Initialise mapping object for relevant board
        self._mapper = MappingObject(self._board_id)
        board_data = BOARD_MAPPING_DICT[self._board_id]

        # Iterate through moncli columns with mapping object to instantiate columns on BaseItem
        completed_columns = []
        for mon_col in columns:
            try:
                name = board_data['columns'][mon_col.id]
                column = self._mapper.process_column(mon_col, self)
                setattr(self, name, column)
                completed_columns.append(column.id)
            except KeyError:
                # Occurs when id is not found in the config file
                if mon_col.id == 'name':
                    # Ignore the 'name' column as this would be the name of the item
                    pass
                else:
                    print(f'Column ID "{mon_col.id}" not found in config: ""{board_data["name"]}""')

        # Compares successfully mapped columns with those listed in config, prints out the excess to keep clutter down
        if len(completed_columns) < len(board_data['columns'].keys()):
            print(f'Surplus Columns: Config: {board_data["name"]}')
            for column in list(set(board_data['columns'].keys()) - set(completed_columns)):
                print(column)
            print('!!!!!!!!! CLEAN UP ON AISLE CONFIG !!!!!!!!!')

    def commit(self):
        if not self.staged_changes:
            raise Exception('Attempting to Commit Changes with no Staged Changes')
        try:
            result = self._moncli_obj.change_multiple_column_values(self.staged_changes)
            self.staged_changes = {}
            return result

        except moncli_error as error:
            raise Exception('NEED TO WRITE THIS')


class MondaySubmissionError(moncli_error):
    def __init__(self, staged_changes: dict, moncli_obj: moncli.entities.Item, logger: CustomLogger):
        print('Error Submitting Changes to Monday, attempting individually')
        moncli_obj = moncli_obj
        for item in staged_changes:
            submit_dict = {item: staged_changes[item]}
            print(f'Adjusting')

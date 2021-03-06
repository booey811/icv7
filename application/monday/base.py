from typing import Union
from datetime import datetime

import moncli.entities
from moncli.api_v2.exceptions import MondayApiError as moncli_error

from application.utilities import clients
from application.exceptions import HardLog
from .mappings import MappingObject
from .config import BOARD_MAPPING_DICT


class BaseItemStructure:
    def __init__(self, logger, board_id: Union[str, int] = ''):
        self.moncli_obj = None
        self.moncli_board_obj = None
        self.board_id = board_id

        self.staged_changes = {}
        self.mon_id = None
        self.zen_id = None
        self.name = ''

        self.logger = logger


class BaseItem(BaseItemStructure):
    """This item is the main interface for the entire application"""

    def __init__(self,
                 logger,
                 item_id_or_mon_item: Union[str, int, moncli.entities.Item] = None,
                 board_id: Union[str, int] = None,
                 get_column_values=True):
        super().__init__(logger, board_id)

        # Check input is correct
        if not item_id_or_mon_item and not board_id:
            raise Exception('Cannot Instantiate BaseItem without item_id or mon_item or board_id')

        # Check instantiation type via input keywords
        elif item_id_or_mon_item:
            # Check whether input is int or str (meaning it is the item's ID) and act accordingly
            if type(item_id_or_mon_item) in (str, int):
                self.log(f'Instantiate BaseItem from Monday ID: {item_id_or_mon_item}')
                self.moncli_obj = \
                    clients.monday.system.get_items(get_column_values=get_column_values, ids=[item_id_or_mon_item])[0]
            elif type(item_id_or_mon_item) == moncli.entities.Item:
                self.log(f'Instantiate BaseItem from moncli.Item Object: {item_id_or_mon_item.id}')
                self.moncli_obj = item_id_or_mon_item
            else:
                raise Exception(f'BaseItem supplied with item_id_or_object that is not str, int, or moncli.Item: {str(item_id_or_mon_item)} ({type(item_id_or_mon_item)})')

            # Set derived basic info
            self.mon_id = str(self.moncli_obj.id)
            self.moncli_board_obj = clients.monday.system.get_board_by_id(self.moncli_obj.board.id)
            self.name = self.moncli_obj.name

            # Set columns
            columns = self.moncli_obj.column_values

        elif board_id:
            # Set basic info that can be taken from Board, columns
            self.log(f'Insantiate Empty BaseItem from Board ID {board_id}')
            self.moncli_board_obj = clients.monday.system.get_boards(ids=[self.board_id])[0]

            # Set columns
            columns = self.moncli_board_obj.columns

        else:
            self.log('Unexpected Inputs for BaseItem.__init__')
            raise HardLog(self)

        self.board_id = str(self.moncli_board_obj.id)
        self._convert_column_data_to_eric_values(columns)

    def __str__(self):
        return f"BaseItem[{self._mapper.eric_name}]"

    def __repr__(self):
        return f"BaseItem[{self._mapper.eric_name}]"

    def _convert_column_data_to_eric_values(self, columns):
        """
        Processes column data taken from monday item or board IDs and sets up the eric item accordingly
        Prints out columns that are defined in the config file but not used
        :param columns:
        :return:
        """

        # Initialise mapping object for relevant board
        self._mapper = MappingObject(self.board_id)
        board_data = BOARD_MAPPING_DICT[self.board_id]
        self.log(f'Board[{board_data["name"]}]')

        # Iterate through moncli columns with mapping object to instantiate columns on BaseItem
        completed_columns = []
        for mon_col in columns:
            try:
                name = board_data['columns'][mon_col.id]
                self.log(f'Processing Column[{name}|{mon_col.id}|{mon_col.title}]')
                column = self._mapper.process_column(mon_col, self)
                setattr(self, name, column)
                completed_columns.append(column.id)
                self.log('Column Processing Finished\n')

            except KeyError as e:
                # Occurs when id is not found in the config file
                if mon_col.id == 'name':
                    # Ignore the 'name' column as this would be the name of the item
                    self.log('Skipping "name" Column')
                else:
                    self.log(f'ColumnID[{mon_col.id}] not found in monday.config[{board_data["name"]}] '
                             f'- skip processing')

        # Compares successfully mapped columns with those listed in config, prints out the excess to keep clutter down
        if len(completed_columns) < len(board_data['columns'].keys()):
            self.log(f'Surplus Columns: Config: {board_data["name"]}')
            for column in list(set(board_data['columns'].keys()) - set(completed_columns)):
                self.log(f'    {column}')
            self.logger.soft_log()

    def commit(self):
        # Check whether item has staged changes waiting to be pushed
        if not self.staged_changes:
            raise Exception('Attempting to Commit Changes with no Staged Changes')

        self.log('Commit Requested')

        # Try to apply the changes
        try:
            result = self.moncli_obj.change_multiple_column_values(self.staged_changes)
            self.staged_changes = {}
            self.log('Commit Completed Successfully')
            return result

        except moncli_error as error:
            # This occurs on a submission error (data supplied to moncli does not match the schema)
            self.log('Commit Failed - Attempting Incremental Change')
            for item in self.staged_changes:
                col_id = item
                value = self.staged_changes[col_id]
                try:
                    self.log(f'Changing Column[{col_id}] to {value}')
                    self.moncli_obj.change_multiple_column_values({col_id: value})
                    self.log('Success!')
                except moncli_error:
                    self.log(f'Failure - {item} -> {value}')
                    self.logger.soft_log()

    def new_item(self, name: str, convert_eric=False) -> moncli.entities.Item:
        """
        creates a new monday item on the board related by this eric item
        :param convert_eric: whether the eric item creating this will replace it's current moncki_obj property
        :param name: the desired item name
        :return: new moncli_item, if converted returns self
        """
        # Check input
        if type(name) != str:
            raise Exception('New Item Name Must Be A String')
        else:
            name = name.replace('"', "in").replace("'", "")

        self.log(f'Creating New Item for Board[{self.moncli_board_obj.name}]')

        # Create new item
        try:
            new_item = self.moncli_board_obj.add_item(name, column_values=self.staged_changes)
        except moncli_error:
            # This occurs on a submission error (data supplied to moncli does not match the schema)
            self.log('Item Creation Failed - Attempting Incremental Change')
            new_item = self.moncli_board_obj.add_item(name)
            for item in self.staged_changes:
                try:
                    col_id = item
                    value = self.staged_changes[col_id]
                    self.log(f'Changing Column[{col_id}] to {value}')
                    new_item.change_multiple_column_values({col_id: value})
                    self.log('Success!')
                except moncli_error:
                    self.log('Failure - Terminating Process')
                    raise HardLog(self)

        # Set ID
        self.mon_id = new_item.id

        if convert_eric:
            self.moncli_obj = new_item
            self._convert_column_data_to_eric_values(self.moncli_obj.column_values)

        self.log(f'Item[{self.mon_id}] Created')

        return new_item

    def add_update(self, message_body, client=None):
        message_body = message_body.replace('"', '')
        message_body = message_body.replace("/", '')
        message_body = message_body.replace("-", ' ')
        message_body = message_body.replace("'", '')

        self.moncli_obj.add_update(message_body)

    def log(self, log_line):
        self.logger.log(log_line)


class MondaySubmissionError(moncli_error):
    def __init__(self, staged_changes: dict, moncli_obj: moncli.entities.Item):
        print('Error Submitting Changes to Monday, attempting individually')
        moncli_obj = moncli_obj
        for item in staged_changes:
            submit_dict = {item: staged_changes[item]}
            print(f'Adjusting')

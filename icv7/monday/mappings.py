from typing import Union
import json

import moncli.entities
from moncli.entities import column_value

from .config import BOARD_MAPPING_DICT
from icv7.monday import exceptions


class MappingObject:
    def __init__(self, board_id):

        if str(board_id) not in BOARD_MAPPING_DICT:
            raise Exception(f'Board ID {board_id} does not exist in config MAPPING_DICT')

        self._raw_mapping_dict = BOARD_MAPPING_DICT[str(board_id)]

    @staticmethod
    def process_column(moncli_col_val, staged_changes):
        """
        Returns the appropriate column value from the supplied moncli column value
        :param staged_changes: changes dictionary from Item instance
        :param moncli_col_val: moncli_column_value to be processed
        :return: eric_col_val: eric col_val to be assigned as item attribute
        """

        # Check whether the column supplied is from an item (i.e. has a value) or from the board (has no value)
        if type(moncli_col_val) == moncli.entities.Column:
            try:
                eric_col_val = COLUMN_TYPE_MAPPINGS[moncli_col_val.type](moncli_col_val, staged_changes,
                                                                         from_item=False)
            except KeyError:
                eric_col_val = ReadOnlyColumn(moncli_col_val, staged_changes, from_item=False)
        else:
            try:
                eric_col_val = COLUMN_TYPE_MAPPINGS[type(moncli_col_val)](moncli_col_val, staged_changes)
            except KeyError:
                eric_col_val = ReadOnlyColumn(moncli_col_val, staged_changes)

        return eric_col_val


class BaseColumnValue:
    def __init__(self, moncli_column_value, staged_changes):
        self._staged_changes = staged_changes
        self._moncli_value = moncli_column_value
        self.id = moncli_column_value.id
        self.title = moncli_column_value.title
        self._value = None

    @property
    def value(self):
        print('getting value')
        return self._value

    @value.setter
    def value(self, value):
        print(f'setting value :: {self.id} to {value}')
        self._value = value

    def stage(self, new_value: (str, int)) -> list:
        pass


class TextColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)
        if from_item:
            self._value = moncli_column_value.text

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: Union[str, int]):
        # Check column hasn't already had a change staged
        if self.id in self._staged_changes:
            raise Exception(f'Attempted to stage a change in a column ({self.id}) that has already got a change staged')

        # Check Input Type is Allowed (str and int only)
        if type(value) in [str, int]:
            to_set = str(value)
        else:
            # TODO: Add 'soft_log' for this error then allow the exception
            raise ValueError(f'TextColumn ({self.title}) value setter supplied with incorrect type ({type(value)})')

        # Adjust eric object value
        self._value = to_set
        # Add change to staged changes
        self._stage_change(self._value)

    def _stage_change(self, value):
        if type(value) not in [int, str]:
            raise TypeError(f'TextColumn._stage_change ({self.title}) supplied with incorrect type: {type(value)}')
        self._staged_changes[self.id] = value
        return {self.id: value}


class LongTextColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)


class StatusColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)
        if from_item:
            # Take basic column info from the moncli value & set up value attribute to return the label
            self._label = str(moncli_column_value.label)
            self._index = moncli_column_value.index
            self._value = self._label

            # Set up the _settings attribute (dict), which is used to convert label inputs into index and vice versa
            simple_settings = json.loads(moncli_column_value.settings_str)['labels']
            self._settings = {}
            for item in simple_settings:
                self._settings[item] = simple_settings[item]
                self._settings[simple_settings[item]] = item

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, to_set: Union[str, int]):
        # Check column hasn't already had a change staged
        if self.id in self._staged_changes:
            raise Exception(f'Attempted to stage a change in a column ({self.id}) that has already got a change staged')

        # Check input is either int or string
        if type(to_set) not in (int, str):
            raise ValueError(f'StatusColumn ({self.title}) value setter supplied with incorrect type ({type(to_set)})')

        # Check input is valid for column settings through try/except
        try:
            key = str(to_set)
            val = str(self._settings[key])
        except KeyError as e:
            # TODO Add softlog for this exception
            raise ValueError(f'StatusColumn ({self.title}) value setter supplied with input that does not show '
                             f'in settings ("{to_set}")')

        # Work out whether an index or a label has been provided
        try:
            input_index = str(int(to_set))
            input_label = str(self._settings[input_index])
        except ValueError as e:
            input_label = str(to_set)
            input_index = str(self._settings[input_label])
        else:
            raise Exception(f'Unknown Error in StatusColumn.value.setter ({self.title}) - could not convert index to'
                            'label or vice versa')

        # Set private attributes
        self._label = input_label
        self._index = input_index
        self._value = input_label

        # Stage change
        self._stage_change(to_set)

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, to_set: str):
        # Check input is correct
        if type(to_set) is not str:
            raise ValueError(f'StatusColumn.label.setter supplied with non-string input: {to_set}')

        # Pass new value to value setter, which sets index and label as well
        self.value = to_set

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, to_set: Union[str, int]):
        # Check input is correct
        if type(to_set) not in (str, int):
            raise ValueError(f'StatusColumn.label.setter supplied with non-string input: {to_set}')

        # Pass new value to value setter, which sets index and label as well
        self.value = to_set

    def _stage_change(self, value: Union[int, str]):
        # Check Input is the right type
        if type(value) not in (str, int):
            raise TypeError(f'StatusColumn._stage_change ({self.title}) supplied with incorrect type: {type(value)}')

        # Check if input is the index (integer) and convert from string if so
        if type(value) == str:
            try:
                index = int(value)
            except ValueError:
                index = int(self._settings[value])
        elif type(value) == int:
            index = int(value)
        else:
            raise Exception('An Unknown Error Occurred')

        # Check index is still in column _settings
        try:
            conversion = self._settings[str(index)]
        except KeyError:
            raise Exception(f'StatusColumn._stage_change ({self.title}) supplied with value not in _settings ({value})')

        self._staged_changes[self.id] = {'index': index}


class DropdownColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)


class NumberColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)
        if from_item:
            if moncli_column_value.text:
                self._value = moncli_column_value.text
            else:
                self._value = 0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: Union[str, int]):
        # Check column hasn't got a staged change already
        if self.id in self._staged_changes:
            raise Exception(
                f'Attempted to stage a change in a column ({self.id}) that has already got a change staged')

        # Check input is correct via try/except (int, str or float only)
        try:
            value = float(value)  # Has to be float as moncli struggles to convert
            # Adjust eric value
            self._value = str(value)
            # Stage change
            self._stage_change(self._value)
        except ValueError:
            raise ValueError(f'NumberColumn ({self.title}) value setter supplied with incorrect type ({type(value)})')

    def _stage_change(self, value: Union[str, int]):
        if type(value) not in (str, int):
            raise TypeError(f'NumberColumn._stage_change ({self.title}) supplied with incorrect type: {type(value)}')
        self._staged_changes[self.id] = value


class DateColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)


class LinkColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)


class FileColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)


class CheckboxColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)


class HourColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)


class PeopleColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)


class ReadOnlyColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)


# Dictionary to convert moncli column values to Eric column values
COLUMN_TYPE_MAPPINGS = {
    column_value.TextValue: TextColumn,
    'text': TextColumn,
    column_value.LongTextValue: LongTextColumn,
    'long-text': LongTextColumn,
    column_value.StatusValue: StatusColumn,
    'color': StatusColumn,
    column_value.DropdownValue: DropdownColumn,
    'dropdown': DropdownColumn,
    column_value.NumberValue: NumberColumn,
    'numeric': NumberColumn,
    column_value.DateValue: DateColumn,
    'date': DateColumn,
    column_value.LinkValue: LinkColumn,
    'link': LinkColumn,
    column_value.FileValue: FileColumn,
    'file': FileColumn,
    column_value.CheckboxValue: CheckboxColumn,
    'boolean': CheckboxColumn,
    column_value.HourValue: HourColumn,
    'hour': HourColumn,
    column_value.PeopleValue: PeopleColumn,
    'multiple-person': PeopleColumn
}

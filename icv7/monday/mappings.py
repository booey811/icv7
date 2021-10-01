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
    def __init__(self, moncli_column_value, eric_item):
        self._eric = eric_item
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

        # Check Input Type is Allowed (str and int only)
        if type(value) in [str, int]:
            to_set = str(value)
        else:
            # TODO: Add 'soft_log' for this error then allow the exception
            raise ValueError(f'TextColumn ({self.title}) value setter supplied with incorrect type ({type(value)})')

        # Adjust eric object value
        self._value = to_set
        # Add change to staged changes
        self._stage_change()

    def _stage_change(self):
        self._eric.staged_changes[self.id] = self._value
        return {self.id: self._value}


class LongTextColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)
        if from_item:
            self._value = moncli_column_value.text

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, to_set: Union[str, int]):
        # Check input is correct
        if type(to_set) not in (str, int):
            raise ValueError(
                f'LongTextColumn ({self.title}) value setter supplied with incorrect type ({type(to_set)})')

        # Adjust eric value
        self._value = str(to_set)

        # Add change to _staged_changes
        self._stage_change()

    def _stage_change(self):
        self._eric.staged_changes[self.id] = self._value
        return {self.id: self._value}


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

        # Check input is either int or string
        if type(to_set) not in (int, str):
            raise ValueError(f'StatusColumn ({self.title}) value setter supplied with incorrect type ({type(to_set)})')

        # Check input is valid for column settings through try/except
        try:
            key = str(to_set)
            val = str(self._settings[key])
        except KeyError as e:
            # TODO Add softlog for this exception
            raise ValueError(f'StatusColumn ({self.title}) value setter supplied with a label or index that does not '
                             f'show in settings ("{to_set}")')

        # Work out whether an index or a label has been provided
        try:
            input_index = str(int(to_set))
            input_label = str(self._settings[input_index])
        except ValueError as e:
            input_label = str(to_set)
            input_index = str(self._settings[input_label])

        # Set private attributes
        self._label = input_label
        self._index = input_index
        self._value = input_label

        # Stage change
        self._stage_change()

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

    def _stage_change(self):

        # Check if input is the index (integer) and convert from string if so
        if type(self._value) == str:
            try:
                index = int(self._value)
            except ValueError:
                index = int(self._settings[self._value])
        elif type(self._value) == int:
            index = int(self._value)
        else:
            raise Exception('An Unknown Error Occurred')

        # Check index is still in column _settings
        try:
            conversion = self._settings[str(index)]
        except KeyError:
            raise Exception(
                f'StatusColumn._stage_change ({self.title}) supplied with value not in _settings ({self._value})')

        self._eric.staged_changes[self.id] = {'index': index}


class DropdownColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)
        if from_item:
            # Take basic info from column value and set up _value to return labels
            self._ids = [item.id for item in moncli_column_value.labels]
            self._labels = [item.name for item in moncli_column_value.labels]

            # Set up _settings attribute containing all labels and associated ids
            self._settings = {}
            simple_settings = json.loads(moncli_column_value.settings_str)['labels']
            for item in simple_settings:
                self._settings[str(item['id'])] = item['name']
                self._settings[item['name']] = str(item['id'])





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

        # Check input is correct via try/except (int, str or float only)
        try:
            value = float(value)  # Has to be float as moncli struggles to convert
            # Adjust eric value
            self._value = str(value)
            # Stage change
            self._stage_change()
        except ValueError:
            raise ValueError(f'NumberColumn ({self.title}) value setter supplied with incorrect type ({type(value)})')

    def _stage_change(self):
        if type(self._value) not in (str, int):
            raise TypeError(f'NumberColumn._stage_change ({self.title}) supplied with incorrect type: {type(self._value)}')
        self._eric.staged_changes[self.id] = self._value


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

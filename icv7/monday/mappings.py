import datetime
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
        self._index = int(input_index)
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
        # if type(self._value) == str:
        #     try:
        #         index = int(self._value)
        #     except ValueError:
        #         index = int(self._settings[self._value])
        # elif type(self._value) == int:
        #     index = int(self._value)
        # else:
        #     raise Exception('An Unknown Error Occurred')

        # Check index is still in column _settings
        try:
            conversion = self._settings[str(self._index)]
        except KeyError:
            raise Exception(
                f'StatusColumn._stage_change ({self.title}) supplied with value not in _settings ({self._value})')

        self._eric.staged_changes[self.id] = {'index': self._index}


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

    @property
    def value(self):
        return self._value

    @property
    def labels(self):
        return self._labels

    @property
    def ids(self):
        return self._ids

    @value.setter
    def value(self, ids_to_set: list):

        # Set private variables
        self._ids = [int(item) for item in ids_to_set]
        self._labels = [self._settings[str(item)] for item in self._ids]

        # Adjust value
        self._value = self._labels

        # Stage Change
        self._stage_change()

    @staticmethod
    def _check_input_and_convert_to_list(to_set) -> list:
        """Checks input for changing values is of the correct type and converts it to a list for processing"""
        # Check input is correct
        if type(to_set) not in (str, int, list):
            raise ValueError(f'DropDownColumn.label.setter supplied with non-string or int input: {to_set}')

        # Convert input to list if it is not already one
        if type(to_set) is not list:
            to_set = [to_set]

        # Check all values in list are correct
        for item in to_set:
            if type(item) not in (str, int):
                raise ValueError(f'DropdownColumn supplied with {type(item)} - Should be int or string')

        return to_set

    def _id_and_label_conversion(self, list_of_values):
        """converts list of labels or ids to list of ids, ready for submission to value.setter"""
        ids_list = []
        for item in list_of_values:
            # Check that value is present in _settings to see if change is possible
            try:
                key = item
                val = self._settings[str(key)]
            except KeyError:
                raise ValueError(
                    f'DropDownColumn ({self.title}) value setter supplied with a label or index that does not '
                    f'show in settings ("{item}")')

            # Work out whether an id or a label has been provided & add relevant id to results list
            try:
                input_id = str(int(item))
            except ValueError as e:
                input_label = str(item)
                input_id = str(self._settings[input_label])

            ids_list.append(input_id)

        return ids_list

    def remove(self, to_remove: Union[str, int, list]):
        """Removes the given id(s) or label(s) from the column value"""
        # Check inputs
        to_remove = self._check_input_and_convert_to_list(to_remove)
        # Convert labels to ids if necessary
        ids_to_remove = [int(item) for item in self._id_and_label_conversion(to_remove)]
        # State new ids
        new_ids = list(set(self._ids) - set(ids_to_remove))
        # Adjust value
        self.value = new_ids

    def add(self, to_add: Union[str, int, list]):
        """Adds the given id(s) or label(s) to the column value"""
        # Check inputs
        to_add = self._check_input_and_convert_to_list(to_add)
        # Convert labels to ids if necessary
        ids_to_add = self._id_and_label_conversion(to_add)
        # State new ids
        new_ids = list(set(self._ids + ids_to_add))
        # Adjust value
        self.value = new_ids

    def replace(self, to_replace: Union[str, int, list]):
        """Replaces the item's currents ids and labels with the one(s) provided"""
        # Check inputs
        to_replace = self._check_input_and_convert_to_list(to_replace)
        # Convert labels to ids if necessary
        replacement_ids = self._id_and_label_conversion(to_replace)
        # State new ids
        new_ids = replacement_ids
        # Adjust value
        self.value = new_ids

    def _stage_change(self):
        self._eric.staged_changes[self.id] = {'ids': self._ids}


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
        self._eric.staged_changes[self.id] = self._value


class DateColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)
        if from_item:
            # Set private attributes
            self._value = moncli_column_value.text
            self._date = self._value.split()[0]
            self._time = moncli_column_value.time

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, date: str):
        if date and date is not str:
            raise ValueError(
                f'DateColumn "date" ({self.title}) value setter supplied with incorrect type ({type(date)})')

        if date.capitalize() == 'TODAY':
            self._date = datetime.datetime.today().strftime('%Y-%m-%d')
        else:
            raise Exception('DateColumn Setting to non-today Date has not yet been developed')

        # Stage change
        self._stage_change()

    def _stage_change(self):
        self._eric.staged_changes[self.id] = {'date': self._date}


class LinkColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)
        if from_item:
            # Set private variables
            self._value = moncli_column_value.text
            self._text = moncli_column_value.url_text
            self._url = moncli_column_value.url

    @property
    def value(self):
        return self._value

    @property
    def text(self):
        return self._text

    @property
    def url(self):
        return self._url

    @value.setter
    def value(self, url_then_text: list):
        # Check inputs
        if type(url_then_text) is not list:
            raise ValueError(
                f'LinkColumn ({self.title}) value setter supplied with incorrect type ({type(url_then_text)})')
        if len(url_then_text) > 2:
            raise ValueError(f'LinkColumn ({self.title}) value setter supplied with list of len > 2 {url_then_text}')
        for item in url_then_text:
            if type(item) is not str:
                raise ValueError(f'LinkColumn ({self.title}) value setter supplied with incorrect list containing '
                                 f'non-strings')

        # Set private variables
        self._url = url_then_text[0]
        self._text = url_then_text[1]
        self._value = f'{self._text} - {self._url}'

        # Stage changes
        self._stage_change()

    @text.setter
    def text(self, to_set: str):
        # Check inputs
        if to_set is not str:
            raise ValueError(f'LinkColumn ({self.title}) value setter supplied with incorrect type ({type(to_set)})')

        # Set value
        self.value = [self._url, to_set]

    @url.setter
    def url(self, to_set: str):
        # Check inputs
        if to_set is not str:
            raise ValueError(f'LinkColumn ({self.title}) value setter supplied with incorrect type ({type(to_set)})')

        # Set value
        self.value = [to_set, self._text]

    def _stage_change(self):
        self._eric.staged_changes[self.id] = {'url': self._url, 'url_text': self._text}


class FileColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)
        if from_item:
            try:
                self._files = [item['name'] for item in moncli_column_value.files]
            except TypeError:
                self._files = []

    @property
    def files(self):
        return self._files

    @files.setter
    def files(self, value):
        raise Exception('FilesColumn.setter has not yet been developed')


class CheckboxColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)
        if from_item:
            if not moncli_column_value.checked:
                self._value = False
            else:
                self._value = True

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, to_set: bool):
        # Check input
        if type(to_set) is not bool:
            raise ValueError(
                f'CheckBoxColumn ({self.title}) value setter supplied with incorrect type ({type(to_set)})')

        # Set private attributes
        self._value = to_set

        # Stage Change
        self._stage_change()

    def _stage_change(self):
        if self._value:
            submit = 'true'
        else:
            raise Exception('Cannot Currently Set CheckBoxValue to "False" - Not Developed')
        self._eric.staged_changes[self.id] = {'checked': submit}


class HourColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)
        if from_item:
            self._hour = moncli_column_value.hour
            self._minute = moncli_column_value.minute
            self._value = f'{self._hour}:{self._minute}'

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, to_set: Union[str, int]):
        """accepts 'military time' input (int or str) - 4 digits with the first two referring to the hour and
        the second two, the minutes"""

        if type(to_set) not in (str, int):
            raise ValueError(f'HourColumn ({self.title}) value.setter supplied with incorrect type ({type(to_set)})')

        if len(str(to_set)) != 4:
            raise ValueError(f'HourColumn ({self.title}) value.setter supplied with non-4-digit input {to_set}')

        # Set private variables
        self._hour = int(str(to_set)[:2])
        self._minute = int(str(to_set)[2:])
        self._value = f'{self._hour}:{self._minute}'

        # Stage change
        self._stage_change()

    @property
    def hour(self):
        return self._hour

    @hour.setter
    def hour(self, to_set: Union[int, str]):
        """accepts a two digit input in 24 hour clock format"""
        # Check inputs
        if type(to_set) not in (str, int):
            raise ValueError(f'HourColumn ({self.title}) hour.setter supplied with incorrect type ({type(to_set)})')
        if len(str(to_set)) != 2:
            raise ValueError(f'HourColumn ({self.title}) hour.setter supplied with non-4-digit input {to_set}')

        # Set private variables and adjust value
        self._hour = int(to_set)
        self.value = f'{self._hour}{self._minute}'

    @property
    def minute(self):
        return self._minute

    @minute.setter
    def minute(self, to_set: Union[int, str]):
        """accepts a two digit input in 24 hour clock format"""
        # Check inputs
        if type(to_set) not in (str, int):
            raise ValueError(f'HourColumn ({self.title}) minute.setter supplied with incorrect type ({type(to_set)})')
        if len(str(to_set)) != 2:
            raise ValueError(f'HourColumn ({self.title}) minute.setter supplied with non-4-digit input {to_set}')

        # Set private variables and adjust value
        self._minute = int(to_set)
        self.value = f'{self._hour}{self._minute}'

    def _stage_change(self):
        self._eric.staged_changes[self.id] = {'hour': self._hour, 'minute': self._minute}


class PeopleColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)
        if from_item:
            self._ids = [item['id'] for item in moncli_column_value.persons_and_teams]
            self._value = self._ids

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, to_set: Union[str, int, list]):
        # Check inputs
        if type(to_set) not in (str, int, list):
            raise ValueError(f'PeopleColumn ({self.title}) minute.setter supplied with incorrect type ({type(to_set)})')

        # Convert input to list
        if type(to_set) is not list:
            to_set = [to_set]

        raise Exception('Not Yet Developed - PeopleValue.value.setter')

    @property
    def ids(self):
        return self._ids

    @ids.setter
    def ids(self, to_set):
        raise Exception('Not Yet Developed - PeopleValue.ids.setter')


class ReadOnlyColumn(BaseColumnValue):
    """ReadOnly Columns will simply make the moncli_value more readily available (non-private) for more literal
    access """

    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)
        self.moncli_value = self._moncli_value


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

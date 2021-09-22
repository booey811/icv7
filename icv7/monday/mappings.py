import moncli.entities
from moncli.entities import column_value

from .config import BOARD_MAPPING_DICT


class MappingObject:
    def __init__(self, board_id):

        if str(board_id) not in BOARD_MAPPING_DICT:
            raise Exception(f'Board ID {board_id} does not exist in MAPPING_DICT')

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
                raise Exception(f'COLUMN_TYPE_MAPPINGS does not contain a key for {moncli_col_val.type}')
        else:
            try:
                eric_col_val = COLUMN_TYPE_MAPPINGS[type(moncli_col_val)](moncli_col_val, staged_changes)
            except KeyError:
                raise Exception(f'COLUMN_TYPE_MAPPINGS does not contain a key for {type(moncli_col_val)}')

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
        """
Returns a list: [COLUMN_ID, COLUMN_VALUE]
COLUMN_VALUE may be a string (text column), an integer (number column), a dictionary (status, dropwdown columns)
        :param new_value: the value to set the column to
        """
        pass


class TextColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)
        if from_item:
            self._value = moncli_column_value.text

    @property
    def value(self):
        print('getting text value')
        return self._value

    @value.setter
    def value(self, value):
        print(f'setting text value :: {self.id} to {value}')
        if self.id in self._staged_changes:
            raise Exception(f'Attempted to stage a change in a column ({self.id}) that has already got a change staged')
        self._value = str(value)
        self._stage_change(value)

    def _stage_change(self, value):
        self._staged_changes[self.id] = str(value)


class LongTextColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)


class StatusColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)


class DropdownColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)


class NumberColumn(BaseColumnValue):
    def __init__(self, moncli_column_value, staged_changes, from_item=True):
        super().__init__(moncli_column_value, staged_changes)


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

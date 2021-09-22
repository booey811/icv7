from moncli.entities import column_value

from icv7.utilities import clients
from .config import BOARD_MAPPING_DICT

class MappingObject:
    def __init__(self, board_id):

        if str(board_id) not in BOARD_MAPPING_DICT:
            raise Exception(f'Board ID {board_id} does not exist in MAPPING_DICT')

        self._raw_mapping_dict = BOARD_MAPPING_DICT[str(board_id)]

    @staticmethod
    def process_column(moncli_col_val):
        """
        Returns the appropriate column value from the supplied moncli column value
        :param moncli_col_val: moncli_column_value to be processed
        :return: eric_col_val: eric col_val to be assigned as item attribute
        """

        try:
            eric_col_val = COLUMN_TYPE_MAPPINGS[type(moncli_col_val)](moncli_col_val)
            return eric_col_val

        except KeyError:
            raise Exception(f'COLUMN_TYPE_MAPPINGS does not contain a key for {type(moncli_col_val)}')


class BaseColumnValue:
    def __init__(self, moncli_column_value):
        self._moncli_value = moncli_column_value
        self.id = moncli_column_value.id
        self.title = moncli_column_value.title
        self.value = None

    @property
    def value(self):
        print('getting value')
        return self._value

    @value.setter
    def value(self, value):
        print('setting value')
        self._value = value

    def stage(self, new_value: (str, int)) -> list:
        """
Returns a list: [COLUMN_ID, COLUMN_VALUE]
COLUMN_VALUE may be a string (text column), an integer (number column), a dictionary (status, dropwdown columns)
        :param new_value: the value to set the column to
        """
        pass


class TextColumn(BaseColumnValue):
    def __init__(self, moncli_column_value):
        super().__init__(moncli_column_value)

        self.value = moncli_column_value.text

    @property
    def value(self):
        print('getting text value')
        return self._value

    @value.setter
    def value(self, value):
        print('setting text value')
        self._value = value


class LongTextColumn(BaseColumnValue):
    def __init__(self, moncli_column_value):
        super().__init__(moncli_column_value)


class StatusColumn(BaseColumnValue):
    def __init__(self, moncli_column_value):
        super().__init__(moncli_column_value)


class DropdownColumn(BaseColumnValue):
    def __init__(self, moncli_column_value):
        super().__init__(moncli_column_value)


class NumberColumn(BaseColumnValue):
    def __init__(self, moncli_column_value):
        super().__init__(moncli_column_value)


class DateColumn(BaseColumnValue):
    def __init__(self, moncli_column_value):
        super().__init__(moncli_column_value)


class LinkColumn(BaseColumnValue):
    def __init__(self, moncli_column_value):
        super().__init__(moncli_column_value)


class FileColumn(BaseColumnValue):
    def __init__(self, moncli_column_value):
        super().__init__(moncli_column_value)


class CheckboxColumn(BaseColumnValue):
    def __init__(self, moncli_column_value):
        super().__init__(moncli_column_value)


class HourColumn(BaseColumnValue):
    def __init__(self, moncli_column_value):
        super().__init__(moncli_column_value)


class PeopleColumn(BaseColumnValue):
    def __init__(self, moncli_column_value):
        super().__init__(moncli_column_value)


# Dictionary to convert moncli column values to Eric column values
COLUMN_TYPE_MAPPINGS = {
    column_value.TextValue: TextColumn,
    column_value.LongTextValue: LongTextColumn,
    column_value.StatusValue: StatusColumn,
    column_value.DropdownValue: DropdownColumn,
    column_value.NumberValue: NumberColumn,
    column_value.DateValue: DateColumn,
    column_value.LinkValue: LinkColumn,
    column_value.FileValue: FileColumn,
    column_value.CheckboxValue: CheckboxColumn,
    column_value.HourValue: HourColumn,
    column_value.PeopleValue: PeopleColumn
}

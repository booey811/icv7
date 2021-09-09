from moncli.entities import column_value

from icv7.utilities import clients


class MappingObject:
    def __init__(self, board_id):

        if board_id not in MAPPING_DICT:
            raise Exception(f'Board ID {board_id} does not exist in MAPPING_DICT')

        self.board_id = str(board_id)
        self._raw_mapping_dict = MAPPING_DICT[self.board_id]

    def unpack_properties(self, eric_item_object):

        for item in self._raw_mapping_dict['columns']:

            name = self._raw_mapping_dict['columns'][item]

            moncli_column = eric_item_object.moncli_obj.get_column_value()


MAPPING_DICT = {
    '1139943160': {
        'name': 'devtest',
        'columns': {
            'text': 'text',
            'numbers6': 'numbers',
            'status4': 'status',
            'dropdown3': 'dropdown',
            'date': 'date',
            'people': 'people',
            'subitems': 'subitems',
            'checkbox': 'checkbox',
            'connect_boards': 'connect_boards',
            'status49': 'linked_status',
            'dup__of_status': 'linked_dropdown',
            'dup__of_dup__of_status': 'linked_text',
            'long_text': 'longtext',
            'hour': 'hour',
            'link': 'link'
        }
    }
}


class BaseColumnValue:
    def __init__(self, moncli_column_value):
        self.moncli_value = moncli_column_value
        self.id = moncli_column_value.id
        self.title = moncli_column_value.title

    def change_value(self, new_value: (str, int)) -> list:
        """
Returns a list: [COLUMN_ID, COLUMN_VALUE]
COLUMN_VALUE may be a string (text column), an integer (number column), a dictionary (status, dropwdown columns)
        :param new_value: the value to set the column to
        """
        pass


class TextColumn(BaseColumnValue):
    def __init__(self, moncli_column_value):
        super().__init__(moncli_column_value)

    def change_value(self, new_value):
        changes = [self.id, new_value]
        return changes


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

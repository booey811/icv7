from moncli.entities import column_value


class BaseColumnCollection:
    def __init__(self):
        self.column_id_mappings = {}

        self.staged_changes = {}

    def stage_change(self, column_id: str, new_value: (str, int)):
        # Produce change list representing the column change
        changes = getattr(self, self.column_id_mappings[column_id]).change_value(new_value)
        # Check change has not already been attempted for this column
        if changes[0] in self.staged_changes:
            # TODO Map column_id back to column_ref and raise exception to explain a staged changes clash
            raise Exception('Column INSERTNAME has already been changed and not committed')
        else:
            # Add changes to this column collection's staged changes
            self.staged_changes[changes[0]] = self.staged_changes[changes[1]]


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
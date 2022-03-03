class UnMappedColumnType(Exception):

    def __init__(self, moncli_col_type):
        print(f'Unable to map {moncli_col_type} column, it is not accounted for in moncli.entities.column_value')


class RepairDoesNotExist(Exception):

    def __init__(self, repair_item):
        print("Selected Repair Does Not Exist")
        self.repair = repair_item
        self.error_message = self._calculate_error_message()

    def _calculate_error_message(self):
        return f"Repair Does Not Exist: {self.repair.name}"


class ExternalDataImportError(Exception):

    def __init__(self, external_item, desired_data: list):
        """raised when external board data is missing"""

        self.error_message = self._calculate_error_message(external_item, desired_data)

    def _calculate_error_message(self, external, data):
        message = f"{external} board item is missing data:\n\n{' | '.join([data])}"
        self.error_message = message
        return message

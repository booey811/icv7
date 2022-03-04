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


class NoCorporateItemFound(Exception):

    def __init__(self, company):
        self.error_message = f"No corporate item found for: {company}"


class TagsOnPartsNotAvailableOnMovements(Exception):

    def __init__(self, repair_tags):
        self.error_message = f"Tags Present on Parts Board But Not inventory Movements:\n\n{str(repair_tags)}"


class IndexOrIDConversionError(Exception):
    """raised when a status or dropdown column is changed with an invalid ID or label"""
    def __init__(self, column, index_or_id, eric_item):
        self.error_message = f"Could Not Convert {index_or_id} for {eric_item.moncli_board_obj.name}[{eric_item.mon_id}]: {column.title}"


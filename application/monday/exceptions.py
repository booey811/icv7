class UnMappedColumnType(Exception):

    def __init__(self, moncli_col_type):
        print(f'Unable to map {moncli_col_type} column, it is not accounted for in moncli.entities.column_value')
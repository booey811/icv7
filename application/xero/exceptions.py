class FinancialError(Exception):
    def __init__(self, finance_item, error_type):

        finance_item.finance_errors.label = error_type

        if error_type == "No Sale Price":
            pass
        elif error_type == "No Repair Profile":
            pass
        elif error_type == "Repair Creation":
            pass
        else:
            raise Exception("FinancialError Exception Supplied with Unexpected Error")

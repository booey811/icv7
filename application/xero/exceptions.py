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


class FinancialAndCorporateItemIncompatible(Exception):

    def __init__(self, corporate):

        self.corporate = corporate

        self.corp_requirements = self._generate_requirements()

    def _generate_requirements(self):

        """generates a string of requirements for the relevant corporate item"""

        requires = []

        for req_col in [self.corporate.req_po, self.corporate.req_store, self.corporate.req_user]:
            if req_col.value:
                requires.append(f'Requires {req_col.title.replace("?", "")}')

        if requires:
            return "\n".join(requires)
        else:
            raise Exception("xero_ex Financial Exception should not occur")

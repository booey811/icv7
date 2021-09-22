# from moncli.entities import column_value
#
# from mappings import MappingObject
#
#
# class BaseColumnCollection:
#     def __init__(self, board_id):
#
#         self._mapper = MappingObject(board_id)
#
#         self.staged_changes = {}
#
#     # def stage_change(self, column_id: str, new_value: (str, int)):
#     #     # Produce change list representing the column change
#     #     changes = getattr(self, self.column_id_mappings[column_id]).change_value(new_value)
#     #     # Check change has not already been attempted for this column
#     #     if changes[0] in self.staged_changes:
#     #         # TODO Map column_id back to column_ref and raise exception to explain a staged changes clash
#     #         raise Exception('Column INSERTNAME has already been changed and not committed')
#     #     else:
#     #         # Add changes to this column collection's staged changes
#     #         self.staged_changes[changes[0]] = self.staged_changes[changes[1]]
#
#
#
#
#

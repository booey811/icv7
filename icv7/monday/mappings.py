from icv7.utilities import clients


class MappingObject:
    def __init__(self, board_id):

        if board_id not in MAPPING_DICT:
            raise Exception(f'Board ID {board_id} does not exist in MAPPING_DICT')

        self.board_id = str(board_id)
        self._raw_mapping_dict = MAPPING_DICT[self.board_id]


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

BOARD_MAPPING_DICT = {
    '1139943160': {
        'name': 'devtest',
        'columns': {
            'text': 'text',
            'numbers6': 'numbers',
            'status4': 'status',
            'dropdown3': 'dropdown',
            'date': 'date',
            'people': 'people',
            'subitems9': 'subitems',
            'checkbox': 'checkbox',
            # 'connect_boards': 'connect_boards',           ====== NOT YET DEVELOPED
            # 'status49': 'linked_status',
            # 'dup__of_status': 'linked_dropdown',
            # 'dup__of_dup__of_status': 'linked_text',      ====== NOT YET DEVELOPED
            'long_text': 'longtext',
            'hour': 'hour',
            'link7': 'link',
            'button': 'button',
            'item_id': 'item_id',
            'files': 'files'
        }
    },
    '1776299869': {
        'name': 'repairs-safron',
        'columns': {
            'connect_boards': 'connect_main',
            'connect_boards2': 'connect_review',
            'status4': 'pc_reports_status',
            'status8': 'diag_status',
            'status': 'repair_status',
            'mirror8': 'device',
            'mirror9': 'requested_repairs',
            'mirror1': 'passcode',
            'long_text': 'repair_notes',
            'mirror67': 'parts',
            'files8': 'pc_reports',
            'mirror69': 'imeisn'
        }
    },
    '349212843': {
        'name': 'main',
        'columns': {
            'status4': 'repair_status',
            'service': 'service',
            'status': 'client',
            'status24': 'repair_type',
            'repair': 'repairs',
            "device0": "device",
            'text4': 'imeisn',
            'status_18': "notifications_status",
            "text5": 'email',
            "text00": "phone",
            "status8": "device_colour",
            "text8": "passcode",
            "text6": "zendesk_id"
        },
        "zendesk": [
            'status4',  # Status
            'text4',  # IMEI/SN
            'text8',  # Passcode
            'device0',  # Device
            'repair'  # Repair
        ]
    },
    "984924063": {
        'name': "repairs",
        'columns': {
            "combined_id": 'combined_id',
            "connect_boards5": "connect_parts"
        }
    },
    '985177480': {
        'name': 'parts',
        'columns': {
            'combined_id': 'combined_id',
            'device_id': 'device_id',
            'repair_id': 'repair_id',
            'colour_id': 'colour_id',
            'numbers45': 'count_num',
            'quantity': 'stock_level',
            'numbers37': 'reorder_point',
            'status3': 'low_stock_status',
            'connect_boards18': 'connect_supplier_orders'
        }
    },
    '1008986497': {
        'name': 'stock_counts',
        'columns': {
            'status4': 'count_status',
            'parts_id': 'part_id',
            'numbers0': 'count_num',
            'numbers08': 'expected_num'
        }
    }
}

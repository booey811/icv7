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
            "dual_only_id": "dual_id",

            "repair_id": "r_id",
            "colour_id": "c_id",
            "device_id": "d_id",

            "colour_label": "c_label",
            "repair_label": "r_label",
            "device_label": "d_label",

            "connect_boards5": "connect_parts",

            "quantity": "stock_level",
            "sale_price": "sale_price",
            "status6": "device_type",
            "partboard_id": "parts_id"
        }
    },
    '985177480': {
        'name': 'parts',
        'columns': {
            'combined_id': 'combined_id',
            'device_id': 'device_id',
            'repair_id': 'repair_id',
            'colour_id': 'colour_id',
            "tags": "tags",
            'numbers45': 'count_num',
            'quantity': 'stock_level',
            'numbers37': 'reorder_point',
            'status3': 'low_stock_status',
            'connect_boards18': 'connect_supplier_orders'
        }
    },
    "989490856": {
        "name": "movements",
        "columns": {
            "movement_type": "mov_type",
            "dup__of_movement_type": "mov_dir",
            "quantity_before": "before",
            "quantity_after": "after",
            "numbers9": "difference",
            "mainboard_id": "source_id",
            "link2": "source_url",
            "text4": "parts_id",
            "part_url": "part_url",
            "dropdown": "tags"
        }
    },
    '989883897': {
        'name': 'financial',
        'columns': {
            'be_generator': 'be_generator',
            'client': 'client',
            'colour': 'colour',
            'company2': 'company',
            'date3': 'date_of_finance',
            'date_created': 'date_created',
            'device': 'device',
            'diagnostic_time': 'diagnostic_time',
            'diagnostic_time3': 'diagnostic_time',
            'dup__of_stock_adjustment': 'invoice_generation',
            'formula7': '£/hour',
            'mainboard_id6': 'mainboard_id',
            'mainboard_link': 'mainboard_link',
            'margin': 'margin_backend',
            'margin_frontend': 'margin',
            'mirror1': 'ticket',
            'mirror96': 'user_errors',
            'net_profit': 'net_profit_backend',
            'net_profit_frontend': 'net_profit',
            'numbers': 'repair_counter',
            'numbers3': 'courier_charge_ex',
            'numbers9': 'max_cost_inc',
            'order_id4': 'order_id',
            'parts_status': 'repair_profile',
            'payment_status': 'payment_status',
            'refurb_id1': 'refurb_id',
            'repair_credits': 'total_repair_credits',
            'repair_time': 'repair_time',
            'repair_time2': 'repair_time',
            'repaired_date': 'repaired_date',
            'repairs': 'repairs',
            'sale_price': 'sale_price_backend',
            'sale_price_frontend': 'revenue',
            'service': 'service',
            'status25': 'sales_status',
            'stock_adjustment': 'stock_adjustment',
            'subitems': 'repairs',
            'subitems_supply_price': 'supply_price_backend',
            'technician': 'technician_mirror',
            'text': 'po_number',
            'text1': '--force_company',
            'text3': 'store/cost_centre',
            'text5': 'external_board_id',
            'text6': 'invoice_number',
            'total_time': 'total_time',
            'type': 'type'
        }
    },
    '989906488': {
        'name': 'sub_financial',
        'columns': {
            'margin': 'margin',
            'movement_url': 'movement_url',
            'movementboard_id': 'movement_id',
            'net_sale_price': 'net_sale_price',
            'part_url': 'part_url',
            'partboard_id': 'parts_id',
            'profit': 'net_profit',
            'quantity_used': 'quantity_used',
            'repair_credits': 'repair_credits',
            'sale_price': 'raw_price',
            'status2': 'eod_status',
            'status8': 'vat_margin',
            'supply_price': 'supply_price',
            'vat': 'vat'
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
    },
    '1967127282': {
        'name': 'pc_reports',
        'columns': {
            'text': 'imeisn'
        }
    },
    '1967142485': {
        'name': 'pc_reports_sub',
        'columns': {
            'files': 'pc_report',
            'text': 'date_text',
            'date': 'date_date'
        }
    },
    '2066318731': {
        'name': 'enq_bookings',
        'columns': {
            'date': 'date_date',
            'text': 'email',
            'text4': 'device_type',
            "long_text": "message",
            "text1": "zen_id",
            "text0": "model"
        }
    },
    "2066698364": {
        "name": "enq_diagnostics",
        "columns": {
            "date4": "date_date",
            "long_text": "message",
            "text": "email",
            "text3": "device_type"
        }
    },
    "2066891548": {
        "name": "enq_contact",
        "columns": {
            "date4": "date_date",
            "long_text": "message",
            "text": "email"
        }
    },
    "2126488977": {
        "name": "refurb_phones",
        "columns": {
            "status9": "overall_status",
            "status4": "v_model",
            "status6": "v_storage",
            "dup__of_vendor_storage": "a_storage",
            "status2": "v_colour",
            "dup__of_vendor_colour": "a_colour",
            "status1": "v_network",
            "long_text": "v_remarks",
            'numbers11': "unit_cost",
            "status_16": "target_grade",
            "dup__of_target_grade": "final_grade",
            "dup__of_vendor_model": "a_model",
            "dup__of_init_face_id8": "a_face_id",
            "status0": "a_lens",
            "status69": "a_rear",
            "dup__of_lens_condition7": "a_charging",
            "dup__of_charging_port0": "a_wireless",
            "text3": "imeisn",
            "text": "pc_report_id",
            "status": "pc_report_status_pre",
            "dup__of_pc_report_status__pre_": "pc_report_status_post",
            "dup__of_face_id_condition": "i_face_id",
            "status_1": "i_screen",
            "dup__of_init_front_screen": "w_screen",
            "dup__of_rear_condition": "i_rear",
            "dup__of_charging_port": "w_rear",
            "haptic2": "i_battery",
            "dup__of_init_battery": "w_battery",
            "numbers17": "i_battery_health",
            "dup__of_init_batt__health": "w_battery_health",
            "rear_housing": "i_mic",
            "dup__of_init_microphone": "w_mic",
            "microphone": "i_charging",
            "dup__of_init_charging_port3": "w_charging",
            "charging_port40": "i_wireless",
            "dup__of_init_wireless_charging9": "w_wireless",
            "charging_port8": "i_mute_vol",
            "dup__of_init_mute_vol_buttons": "w_mute_vol",
            "charging_port": "i_power",
            "dup__of_init_power_button": "w_power",
            "charging_port4": "i_earpiece",
            "dup__of_init_earpiece___mesh": "w_earpiece",
            "power_button": "i_loudspeaker",
            "dup__of_init_loudspeaker": "w_loudspeaker",
            "power_button9": "i_wifi",
            "dup__of_init_wifi": "w_wifi",
            "wifi": "i_bluetooth",
            "dup__of_init_bluetooth": "w_bluetooth",
            "bluetooth": "i_rear_cam",
            "dup__of_init_rear_camera": "w_rear_cam",
            "rear_camera": "i_front_cam",
            "dup__of_init_front_camera": "w_front_cam",
            "dup__of_lens_condition5": "i_lens",
            "dup__of_lens_condition3": "w_lens",
            "rear_lens": "i_siri",
            "dup__of_init_siri": "w_siri",
            "siri": "i_haptic",
            "dup__of_init_haptic": "w_haptic",
            "haptic3": "i_nfc",
            "dup__of_init_nfc": "w_nfc",
            "date55": "last_search_date",
            "date1": "last_report_date",
            "dup__of_nfc8": "w_face_id",
            "date13": "purchase_date",
            "date11": "received_date",
            "date10": "repairs_begun_date",
            "date90": "repairs_complete_date",
            "date3": "listing_date",
            "date36": "sale_date",
            "status692": "sale_platform",
            "text847": "sale_id",
            "numbers95": "sale_price",
            "status11": "repair_status",
            "dup__of_nfc": "w_flashlight",
            "dup__of_flashlight": "i_flashlight",
            "long_text5": "report_summary",
            "files8": "inter_report",
            "files2": "sale_report",
            "files": "pre_report"
        }
    }
}

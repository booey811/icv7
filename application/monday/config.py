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
			"text6": "zendesk_id",
			"collection_date": "repaired_date",
			"status_183": "user_errors",
			'date6': 'booking_date',
			'date36': 'deadline_date',
			'date4': 'received_date',
			'link1': 'ticket_url',
			"text15": "company_name",
			"numbers5": "repair_phase",
			"text3": "intake_notes",
			"text05": "device_eric_id",
			"text21": "device_eric_name"
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
			"partboard_id": "parts_id",
			"mirror0": "refurb_poss"
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
			'connect_boards18': 'connect_supplier_orders',
			"status13": "function",
			"sale_price": 'sale_price',
			'supply_price': "supply_price",
			'link_to_products___pricing': 'connect_products'
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
			"part_url": "parts_url",
			"dropdown": "tags",
			"status7": "void_status"
		}
	},
	'989883897': {
		'name': 'financial',
		'columns': {
			'subitems': 'repairs',  # subtasks
			'repair_credits': 'total_repair_credits',  # lookup
			'subitems_supply_price': 'supply_price_backend',  # lookup
			'sale_price': 'sale_price_backend',  # lookup
			'net_profit': 'net_profit_backend',  # lookup
			'sale_price_frontend': 'revenue',  # formula
			'net_profit_frontend': 'net_profit',  # formula
			'margin_frontend': 'margin',  # formula
			'numbers9': 'max_cost',  # numeric
			'margin': 'margin_backend',  # lookup
			'service': 'service',  # lookup
			'client': 'client',  # lookup
			'type': 'type',  # lookup
			'technician': 'technician_mirror',  # lookup
			'device': 'device',  # lookup
			'repairs': 'repairs',  # lookup
			'colour': 'colour',  # lookup
			'repaired_date': 'repaired_date',  # lookup
			'total_time': 'total_time',  # lookup
			'diagnostic_time': 'diagnostic_time',  # lookup
			'repair_time': 'repair_time',  # lookup
			'diagnostic_time3': 'diagnostic_time',  # formula
			'repair_time2': 'repair_time',  # formula
			'company2': 'company',  # text
			'refurb_id1': 'refurb_id',  # text
			'payment_status': 'payment_status',  # lookup
			'order_id4': 'order_id',  # text
			'mainboard_id6': 'main_id',  # text
			'mainboard_link': 'mainboard_link',  # board-relation
			'parts_status': 'repair_profile',  # color
			'date_created': 'date_created',  # pulse-log
			'stock_adjustment': 'stock_adjust',  # color
			'dup__of_stock_adjustment': 'invoice_generation',  # color
			'date3': 'date_of_finance',  # date
			'numbers': 'repair_counter',  # numeric
			'be_generator': 'be_generator',  # boolean
			'formula7': '£/hour',  # formula
			'numbers3': 'courier_charge',  # numeric
			'text': 'po_number',  # text
			'text3': 'store',  # text
			'text6': 'invoice_number',  # text
			'text1': 'shortcode',  # text
			'text5': 'external_board_id',  # text
			'mirror1': 'ticket',  # lookup
			'status25': 'sales_status',  # color
			'mirror96': 'user_errors',  # lookup
			"status47": "finance_errors",  # status
			"text4": "username"
		}
	},
	'989906488': {
		'name': 'sub_financial',
		'columns': {
			'quantity_used': 'quantity_used',  # numeric
			'sale_price': 'sale_price',  # numeric
			'net_sale_price': 'net_sale_price',  # formula
			'supply_price': 'supply_price',  # numeric
			'vat': 'vat',  # formula
			'profit': 'net_profit',  # formula
			'margin': 'margin',  # formula
			'part_url': 'parts_url',  # link
			'movement_url': 'movement_url',  # link
			'movementboard_id': 'movement_id',  # text
			'partboard_id': 'parts_id',  # text
			'status2': 'eod_status',  # color
			'repair_credits': 'repair_credits',  # numeric
			'status8': 'vat_margin'  # color
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
	'1031579094': {
		'name': 'stuart_data',
		'columns': {
			'stuart_job_id': 'stuart_job_id',  # text
			'booking_time6': 'booking_time',  # hour
			'collection_time4': 'collection_time',  # hour
			'delivery_time': 'delivery_time',  # hour
			'cost__ex_vat_': 'cost_inc',  # numeric
			'vat': 'vat',  # numeric
			'collection_postcode5': 'collection_postcode',  # text
			'delivery_postcode': 'delivery_postcode',  # text
			'distance': 'distance',  # numeric
			'assignment_code': 'assignment_code',  # text
			'estimated_time__mins_': 'estimated_time_mins',  # numeric
			'date': 'date',  # date
			'booking____delivery': 'booking_delivery',  # formula
			'booking____collection': 'booking_collection',  # formula
			'collection____delivery': 'collection_delivery',  # formula
			'tracking_url': 'tracking_url',  # link
			'creation_log': 'creation_log',  # pulse-log
			'formula2': 'pp_mile',  # formula
			'status': 'status',  # color
			'text6': 'mainboard_id',  # text
			'status_19': 'historical_data',  # color
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
	},
	'1973442389': {
		'name': 'corporates',
		'columns': {
			'subitems': 'subitems',  # subtasks
			'status2': 'account_status',  # color
			'text9': 'zendesk_org_id',  # text
			'text0': 'shortcode',  # text
			'text': 'xero_contact_id',  # text
			'status8': 'courier_service_level',  # color
			'status0': 'payment_method',  # color
			'status7': 'payment_terms',  # color
			'link': 'zendesk_org_link',  # link
			"status1": "create_invoice",
			"link7": "invoice_link",
			"text1": "invoice_id",
			"checkbox6": "req_po",
			"checkbox_1": "req_store",
			"checkbox_2": "req_user",
			"text2": "global_po",
			"text3": "ref_start",
			"text12": "ref_end"
		}
	},
	'113568054': {
		'name': 'zara_ext',
		'columns': {
			'text97': 'ref',  # text
			'status1': 'repair_status',  # color
			'text33': 'issue',  # text
			'long_text': 'repair_notes',  # long-text
			'date': 'returned_date',  # date
			'text8': 'serial_number',  # text
			'text9': 'store',  # text
			'numbers': 'quote',  # numeric
			'status3': 'company',  # color
			'status4': 'invoiced?',  # color
			'status8': 'previously_repaired?',  # color
			'time_tracking8': 'repair_time',  # duration
			'status80': 'push_to_main',  # color
			'connect_boards': 'icorrect_main_board',  # board-relation
			'status05': 'shipment_status',  # color
			'status23': 'destination',  # color
			'mirror': 'device',  # lookup
			'mirror7': 'repairs',  # lookup
			'item_id6': 'item_id',  # pulse-id
			'date8': 'shipment_date',  # date
			'date6': 'delivery_date',  # date
			'mirror4': 'add_to_finance',  # lookup
			'date0': 'last_report_date',  # date
		}
	},
	"2477606931": {
		"name": "staff",
		"columns": {
			"text": "mon_user_id",
			"text8": "slack_user_id",
			"text1": "mainboard_group_id"
		}
	},
	'1985628314': {
		'name': 'events',
		'columns': {
			'status1': 'event_type',  # color
			'long_text': 'description',  # long-text
			'date': 'timestamp',  # date
			'long_text2': 'json_actions',  # long-text
			'status0': 'actions_status',  # color
			'connect_boards': 'related_items',  # board-relation
			'numbers': 'repair_minutes',  # numeric,
			"text": "parent_id",  # text
			"connect_boards9": "bricks_link",  # board-relation
			"people": "owner"  # people
		}
	},
	'2593044634': {
		'name': 'bricks',
		'columns': {
			'person': 'person',  # multiple-person
			'status': 'status',  # color
			'date4': 'date',  # date
			'link_to_subitems_of_icorrect_main_board': 'events_link',  # board-relation
		}
	},
	'2477699024': {
		'name': 'products',
		'columns': {
			'numbers': 'web_price',  # numeric
			'text': 'panrix_price',  # text
			'text7': 'jll',  # text
			'text9': 'oktra',  # text
			'connect_boards8': 'parts',  # board-relation
			'mirror': 'price_from_parts',  # lookup
			'mirror2': 'stock_level',  # lookup
			'text4': 'device_eric_id',  # text
		}
	}
}

STANDARD_REPAIR_OPTIONS = {
	"iPhone": [133, 74, 71, 54, 70, 7, 65, 73, 99, 76, 66, 88, 75, 83, 84],
	"Apple Watch": [133, 69, 138],
	"iPad": [133, 30, 69, 54, 99],
	"MacBook": [133, 71, 54, 119, 32, 38, 33, 117]
}
REPAIR_COLOURS = {
	'STANDARD_REPAIR_COLOURS': [
		"Black",
		"White",
		"Space Grey"
	],
	'MacBook': [
		"Silver",
		"Space Grey",
		"Gold",
		"Rose Gold"
	]
}
ACCOUNT_SHORTCODES = [
	"axaxl",
	"blackstone",
	"fourfront",
	"gpe",
	"gs1",
	"zara.uk",
	"zara.bershka",
	"zara.massimo",
	"zara.pb",
	"zara.strad",
	"zara.home",
	"lasalle",
	"lcp",
	"oaktree",
	"oktra",
	"overbury.mp",
	"panasonic",
	"pandora",
	"plum",
	"prada",
	"pret",
	"scotia",
	"test1",
	"universal",
	"vccp",
	"reiss"
]

_USER_IDS = {
	'1034434': 'meesha',
	'11140118': 'mike',
	'1034414': 'ricky',
	'25304513': 'safan',
	'27932864': 'seb',
	'4251271': 'gabe',
	'12304876': 'systems'
}

_MAINBOARD_GROUP_IDS = {
	'safan': 'new_group95376',
	'meesha': 'new_group15927',
	'mike': 'new_group38737',
	'ricky': 'new_group80898',
	'seb': 'new_group6580',  # client services group
	'gabe': 'new_group6580',  # client services group
	'dev': 'new_group49546'  # Dev/Admin Group
}


class TwoWayDict(dict):

	def __setitem__(self, key, value):
		# Remove any previous connections with these values
		if key in self:
			del self[key]
		if value in self:
			del self[value]
		dict.__setitem__(self, key, value)
		dict.__setitem__(self, value, key)

	def __delitem__(self, key):
		dict.__delitem__(self, self[key])
		dict.__delitem__(self, key)

	def __len__(self):
		"""Returns the number of connections"""
		return dict.__len__(self) // 2

	def __init__(self, dictionary):
		super().__init__()
		for item in dictionary:
			self[item] = dictionary[item]


MAINBOARD_GROUP_IDS = TwoWayDict(_MAINBOARD_GROUP_IDS)
USER_IDS = TwoWayDict(_USER_IDS)

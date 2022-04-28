import os

from application import clients

_MAIN_REPAIRS = {
	'10': 'Audio IC',
	'101': 'Wireless Charging',
	'102': 'Siri',
	'104': 'Repair',
	'107': 'Proximity Sensor',
	'11': 'Apple Boot',
	'111': 'HB',
	'112': 'Other (See Notes)',
	'113': 'Charger Cable',
	'114': 'Charging Cable',
	'115': 'TouchBar',
	'117': 'Keyboard (US)',
	'119': 'Keyboard',
	'120': 'TEST Screen',
	'121': 'Antenna',
	'123': 'TEST Battery',
	'124': 'FPC Connector',
	'126': 'Bottom Board Swap',
	'127': 'SSD Replacement',
	'128': 'Wifi',
	'132': 'Mesh',
	'133': 'Front Screen',
	'134': 'FlexGate',
	'138': 'Crown',
	'140': 'Tempered Glass',
	'141': 'CPU',
	'142': 'Rear Microphone',
	'143': 'Front Screen Generic',
	'144': 'Touch Screen',
	'145': 'TEST ToBeDeleted',
	'146': 'Front Screen (OLED)',
	'147': 'Front Screen (LCD)',
	'148': 'After Market Screen (LCD)',
	'149': 'After Market Screen',
	'18': 'Wifi Module',
	'19': 'Baseband',
	'20': 'Service',
	'21': 'Tri-Star',
	'22': 'Network Search',
	'23': 'No SIM',
	'24': 'Error 9',
	'25': 'Error 4013',
	'26': 'Error 4014',
	'27': 'Wifi IC',
	'28': 'Data',
	'30': 'LCD',
	'32': 'TrackPad',
	'33': 'Keyboard (UK)',
	'34': 'NAND',
	'35': 'Hydrogel Protector',
	'36': 'Power Button',
	'37': 'Logic Board',
	'38': 'Express Diagnostic',
	'41': 'No Fault Found',
	'42': 'Backlight',
	'43': 'Software',
	'45': 'Power IC',
	'49': 'Clean Out',
	'54': 'Charging Port',
	'55': 'See Notes',
	'58': 'Reshaping',
	'61': 'Logic Board',
	'63': 'No Parts Used',
	'65': 'Rear Housing',
	'66': 'Microphone',
	'67': 'Headphone Jack',
	'68': 'Home Button',
	'69': 'Front Screen Universal',
	'7': 'Rear Lens',
	'70': 'Rear Camera',
	'71': 'Battery',
	'72': 'Liquid Damage Treatment',
	'73': 'Earpiece',
	'74': 'After Market Screen (OLED)',
	'75': 'Volume Button',
	'76': 'Front Camera',
	'77': 'Mute Button',
	'78': 'Haptic',
	'79': 'Touch IC',
	'82': 'Rear Glass',
	'83': 'Front Screen (LG)',
	'84': 'Front Screen (Tosh)',
	'85': 'NFC Module',
	'86': 'Couriers',
	'87': 'No Service',
	'88': 'Loudspeaker',
	'89': 'Front Screen GPS',
	'90': 'Front Screen LTE',
	'91': 'Has Case',
	'93': 'Bluetooth Module',
	'94': 'USB Port',
	'95': 'Charging IC',
	'96': 'Screen (Please Specify)',
	'97': 'Charging Port (Please Specify)',
	'98': 'Home Button (Please Specify)',
	'99': 'Face ID',
	'After Market Screen': '149',
	'After Market Screen (LCD)': '148',
	'After Market Screen (OLED)': '74',
	'Antenna': '121',
	'Apple Boot': '11',
	'Audio IC': '10',
	'Backlight': '42',
	'Baseband': '19',
	'Battery': '71',
	'Bluetooth Module': '93',
	'Bottom Board Swap': '126',
	'CPU': '141',
	'Charger Cable': '113',
	'Charging Cable': '114',
	'Charging IC': '95',
	'Charging Port': '54',
	'Charging Port (Please Specify)': '97',
	'Clean Out': '49',
	'Couriers': '86',
	'Crown': '138',
	'Data': '28',
	'Earpiece': '73',
	'Error 4013': '25',
	'Error 4014': '26',
	'Error 9': '24',
	'Express Diagnostic': '38',
	'FPC Connector': '124',
	'Face ID': '99',
	'FlexGate': '134',
	'Front Camera': '76',
	'Front Screen': '133',
	'Front Screen (LCD)': '147',
	'Front Screen (LG)': '83',
	'Front Screen (OLED)': '146',
	'Front Screen (Tosh)': '84',
	'Front Screen GPS': '89',
	'Front Screen Generic': '143',
	'Front Screen LTE': '90',
	'Front Screen Universal': '69',
	'HB': '111',
	'Haptic': '78',
	'Has Case': '91',
	'Headphone Jack': '67',
	'Home Button': '68',
	'Home Button (Please Specify)': '98',
	'Hydrogel Protector': '35',
	'Keyboard': '119',
	'Keyboard (UK)': '33',
	'Keyboard (US)': '117',
	'LCD': '30',
	'Liquid Damage Treatment': '72',
	'Logic Board': '61',
	'Loudspeaker': '88',
	'Mesh': '132',
	'Microphone': '66',
	'Mute Button': '77',
	'NAND': '34',
	'NFC Module': '85',
	'Network Search': '22',
	'No Fault Found': '41',
	'No Parts Used': '63',
	'No SIM': '23',
	'No Service': '87',
	'Other (See Notes)': '112',
	'Power Button': '36',
	'Power IC': '45',
	'Proximity Sensor': '107',
	'Rear Camera': '70',
	'Rear Glass': '82',
	'Rear Housing': '65',
	'Rear Lens': '7',
	'Rear Microphone': '142',
	'Repair': '104',
	'Reshaping': '58',
	'SSD Replacement': '127',
	'Screen (Please Specify)': '96',
	'See Notes': '55',
	'Service': '20',
	'Siri': '102',
	'Software': '43',
	'TEST Battery': '123',
	'TEST Screen': '120',
	'TEST ToBeDeleted': '145',
	'Tempered Glass': '140',
	'Touch IC': '79',
	'Touch Screen': '144',
	'TouchBar': '115',
	'TrackPad': '32',
	'Tri-Star': '21',
	'USB Port': '94',
	'Volume Button': '75',
	'Wifi': '128',
	'Wifi IC': '27',
	'Wifi Module': '18',
	'Wireless Charging': '101'}

_MAIN_DEVICE = {
	'1': 'iPhone 5',
	'10': 'iPhone 8',
	'100': 'MacBook A1297(2009)',
	'101': 'MacBook A1297(2010)',
	'102': 'MacBook A1297(Early2011)',
	'103': 'MacBook A1297(2012)',
	'104': 'MacBook A1398(Early 2013)',
	'105': 'MacBook A1398(2014)',
	'106': 'MacBook A1398(2015)',
	'107': 'MacBook A1502(2013)',
	'108': 'MacBook A1502(2014)',
	'109': 'MacBook A1502(2015)',
	'11': 'iPhone 8 Plus',
	'110': 'MacBook A1425(2013)',
	'111': 'MacBook A1706(2017)',
	'112': 'MacBook A1707(2017)',
	'113': 'MacBook A1708(2016)',
	'114': 'MacBook A1708(2017)',
	'115': 'MacBook A1989(2019)',
	'116': 'MacBook A1990(2018)',
	'117': 'MacBook A1990(2019)',
	'118': 'MacBook A1534(2016)',
	'119': 'MacBook A1534(2017)',
	'12': 'iPhone X',
	'120': 'iPad Pro 12.9" (4G)',
	'122': 'MacBook A1278(2012)',
	'13': 'iPhone XS',
	'134': 'MacBook A1278(Late2011)',
	'135': 'iPhone 5C',
	'14': 'iPhone XS Max',
	'147': 'MacBook A1932(2020)',
	'148': 'Apple Watch S5 40mm',
	'149': 'Apple Watch S5 44mm',
	'15': 'iPhone XR',
	'150': 'MacBook A2159(All Years)',
	'151': 'iPad Pro 11" (2G)',
	'152': 'MacBook A1466(2016)',
	'154': 'iPod Touch 7th Gen',
	'155': 'Device',
	'156': 'iPad 8',
	'157': 'MacBook A1398(All Years)',
	'158': 'MacBook A1534(All Years)',
	'159': 'MacBook A1370(All Years)',
	'16': 'iPad 2',
	'160': 'MacBook A1465(All Years)',
	'161': 'MacBook A1369(All Years)',
	'162': 'MacBook A1466(All Years)',
	'163': 'MacBook A1932(All Years)',
	'164': 'MacBook A1425(All Years)',
	'165': 'MacBook A1502(All Years)',
	'166': 'MacBook A1706(All Years)',
	'167': 'MacBook A1708(All Years)',
	'168': 'MacBook A1989(All Years)',
	'169': 'MacBook A1707(All Years)',
	'17': 'iPad 3',
	'170': 'Apple Watch SE 40mm',
	'171': 'Apple Watch SE 44mm',
	'172': 'MacBook A2179(2020)',
	'173': 'TEST DEVICE',
	'174': 'iPad Air 4',
	'175': 'iPhone 12 Mini',
	'176': 'iPhone 12',
	'177': 'iPhone 12 Pro',
	'178': 'iPhone 12 Pro Max',
	'179': 'iMac 27"',
	'18': 'iPad 4',
	'182': 'MacBook A2338(2020)',
	'183': 'i phone 7',
	'187': 'Apple Watch S6 44mm',
	'188': 'Apple Watch S6 40mm',
	'189': 'Samsung A41',
	'19': 'iPad 5',
	'190': 'Samsung J5 (2017)',
	'192': 'MacBook A2251(2020)',
	'194': 'iPhone 4s',
	'195': 'Samsung A310',
	'198': 'MacBook A2237 (2020)',
	'199': 'iPad 9',
	'2': 'iPhone 6',
	'20': 'iPad 6',
	'200': 'MacBook A2237 (All Years)',
	'201': 'Zebra PDA',
	'202': 'MacBook A2337',
	'203': 'iPad Pro 11" (3G)',
	'204': 'MacBook',
	'205': 'MacBook A2289 (2020)',
	'206': 'iPhone 13',
	'207': 'iPhone 13 Mini',
	'208': 'iPhone 13 Pro',
	'209': 'iPhone 13 Pro Max',
	'21': 'iPad Air',
	'210': 'Apple Watch S7 41mmm',
	'211': 'Apple Watch S7 45mm',
	'212': 'iPad Pro 12.9" (5G)',
	'213': 'iPad Mini 6',
	'214': 'A1707(All Years)',
	'215': 'A1466(All Years)',
	'217': 'MacBook A1990 (All Years)',
	'218': 'MacBook A1398(Late 2013)',
	'219': 'A1990(2018)',
	'22': 'iPad Air 2',
	'23': 'iPad Air 3',
	'24': 'iPad Pro 9.7"',
	'25': 'iPad Pro 10.5"',
	'26': 'iPad Pro 12.9" (1G)',
	'27': 'iPad Pro 12.9" (2G)',
	'28': 'iPad Pro 12.9" (3G)',
	'29': 'iPad Pro 11"',
	'3': 'iPhone 7',
	'30': 'MacBook A1425(2012)',
	'31': 'MacBookA1706(2016)',
	'32': 'MacBook A1398(2012)',
	'33': 'MacBook A1707(2016)',
	'34': 'MacBook A1534(2015)',
	'35': 'MacBook A1370(2010)',
	'36': 'MacBook A1369(2010)',
	'37': 'Apple Watch S1 38mm',
	'38': 'Apple Watch S1 42mm',
	'39': 'Apple Watch S2 38mm',
	'4': 'iPhone 5S',
	'40': 'Apple Watch S2 42mm',
	'41': 'Apple Watch S3 38mm',
	'42': 'Apple Watch S3 42mm',
	'43': 'iPod Touch 5th Gen',
	'44': 'iPod Touch 6th Gen',
	'45': 'iPad Mini',
	'46': 'iPad Mini 2',
	'47': 'iPad Mini 3',
	'48': 'iPad Mini 4',
	'49': 'Other (See Notes)',
	'5': 'iPhone SE',
	'50': 'Samsung A320',
	'51': 'MacBook A1278(2009)',
	'53': 'Samsung Galaxy A3',
	'56': 'Samsung A510',
	'57': 'Zara iPods',
	'58': 'iPhone 4',
	'59': 'Apple Watch S4 40mm',
	'6': 'iPhone 6S',
	'7': 'iPhone 6 Plus',
	'70': 'iPad Mini 5',
	'72': 'MacBook A1932(2018)',
	'73': 'MacBook A1989 (2018)',
	'74': 'MacBook A1286(All Years)',
	'75': 'Apple Watch S4 44mm',
	'76': 'iPhone 11',
	'77': 'iPhone 11 Pro',
	'78': 'iPhone 11 Pro Max',
	'79': 'iPad 7',
	'8': 'iPhone 6S Plus',
	'80': 'MacBook A2141(2019)',
	'81': 'iPhone SE2',
	'83': 'MacBook A1370(2011)',
	'84': 'MacBook A1369',
	'85': 'MacBook A1369(2011)',
	'86': 'MacBook A1369(2012)',
	'87': 'MacBook A1465(2012)',
	'88': 'MacBook A1465(2013)',
	'89': 'MacBook A1465(2014)',
	'9': 'iPhone 7 Plus',
	'90': 'MacBook A1465(2015)',
	'91': 'MacBook A1466(2012)',
	'92': 'MacBook A1466(2013)',
	'93': 'MacBook A1466(2014)',
	'94': 'MacBook A1466(2015)',
	'95': 'MacBook A1466(2017)',
	'96': 'MacBook A1932(2019)',
	'97': 'MacBook A1278(2010)',
	'98': 'MacBook A1278(2011)',
	'A1466(All Years)': '215',
	'A1707(All Years)': '214',
	'A1990(2018)': '219',
	'Apple Watch S1 38mm': '37',
	'Apple Watch S1 42mm': '38',
	'Apple Watch S2 38mm': '39',
	'Apple Watch S2 42mm': '40',
	'Apple Watch S3 38mm': '41',
	'Apple Watch S3 42mm': '42',
	'Apple Watch S4 40mm': '59',
	'Apple Watch S4 44mm': '75',
	'Apple Watch S5 40mm': '148',
	'Apple Watch S5 44mm': '149',
	'Apple Watch S6 40mm': '188',
	'Apple Watch S6 44mm': '187',
	'Apple Watch S7 41mmm': '210',
	'Apple Watch S7 45mm': '211',
	'Apple Watch SE 40mm': '170',
	'Apple Watch SE 44mm': '171',
	'Device': '155',
	'MacBook': '204',
	'MacBook A1278(2009)': '51',
	'MacBook A1278(2010)': '97',
	'MacBook A1278(2011)': '98',
	'MacBook A1278(2012)': '122',
	'MacBook A1278(Late2011)': '134',
	'MacBook A1286(All Years)': '74',
	'MacBook A1297(2009)': '100',
	'MacBook A1297(2010)': '101',
	'MacBook A1297(2012)': '103',
	'MacBook A1297(Early2011)': '102',
	'MacBook A1369': '84',
	'MacBook A1369(2010)': '36',
	'MacBook A1369(2011)': '85',
	'MacBook A1369(2012)': '86',
	'MacBook A1369(All Years)': '161',
	'MacBook A1370(2010)': '35',
	'MacBook A1370(2011)': '83',
	'MacBook A1370(All Years)': '159',
	'MacBook A1398(2012)': '32',
	'MacBook A1398(2014)': '105',
	'MacBook A1398(2015)': '106',
	'MacBook A1398(All Years)': '157',
	'MacBook A1398(Early 2013)': '104',
	'MacBook A1398(Late 2013)': '218',
	'MacBook A1425(2012)': '30',
	'MacBook A1425(2013)': '110',
	'MacBook A1425(All Years)': '164',
	'MacBook A1465(2012)': '87',
	'MacBook A1465(2013)': '88',
	'MacBook A1465(2014)': '89',
	'MacBook A1465(2015)': '90',
	'MacBook A1465(All Years)': '160',
	'MacBook A1466(2012)': '91',
	'MacBook A1466(2013)': '92',
	'MacBook A1466(2014)': '93',
	'MacBook A1466(2015)': '94',
	'MacBook A1466(2016)': '152',
	'MacBook A1466(2017)': '95',
	'MacBook A1466(All Years)': '162',
	'MacBook A1502(2013)': '107',
	'MacBook A1502(2014)': '108',
	'MacBook A1502(2015)': '109',
	'MacBook A1502(All Years)': '165',
	'MacBook A1534(2015)': '34',
	'MacBook A1534(2016)': '118',
	'MacBook A1534(2017)': '119',
	'MacBook A1534(All Years)': '158',
	'MacBook A1706(2017)': '111',
	'MacBook A1706(All Years)': '166',
	'MacBook A1707(2016)': '33',
	'MacBook A1707(2017)': '112',
	'MacBook A1707(All Years)': '169',
	'MacBook A1708(2016)': '113',
	'MacBook A1708(2017)': '114',
	'MacBook A1708(All Years)': '167',
	'MacBook A1932(2018)': '72',
	'MacBook A1932(2019)': '96',
	'MacBook A1932(2020)': '147',
	'MacBook A1932(All Years)': '163',
	'MacBook A1989 (2018)': '73',
	'MacBook A1989(2019)': '115',
	'MacBook A1989(All Years)': '168',
	'MacBook A1990 (All Years)': '217',
	'MacBook A1990(2018)': '116',
	'MacBook A1990(2019)': '117',
	'MacBook A2141(2019)': '80',
	'MacBook A2159(All Years)': '150',
	'MacBook A2179(2020)': '172',
	'MacBook A2237 (2020)': '198',
	'MacBook A2237 (All Years)': '200',
	'MacBook A2251(2020)': '192',
	'MacBook A2289 (2020)': '205',
	'MacBook A2337': '202',
	'MacBook A2338(2020)': '182',
	'MacBookA1706(2016)': '31',
	'Other (See Notes)': '49',
	'Samsung A310': '195',
	'Samsung A320': '50',
	'Samsung A41': '189',
	'Samsung A510': '56',
	'Samsung Galaxy A3': '53',
	'Samsung J5 (2017)': '190',
	'TEST DEVICE': '173',
	'Zara iPods': '57',
	'Zebra PDA': '201',
	'i phone 7': '183',
	'iMac 27"': '179',
	'iPad 2': '16',
	'iPad 3': '17',
	'iPad 4': '18',
	'iPad 5': '19',
	'iPad 6': '20',
	'iPad 7': '79',
	'iPad 8': '156',
	'iPad 9': '199',
	'iPad Air': '21',
	'iPad Air 2': '22',
	'iPad Air 3': '23',
	'iPad Air 4': '174',
	'iPad Mini': '45',
	'iPad Mini 2': '46',
	'iPad Mini 3': '47',
	'iPad Mini 4': '48',
	'iPad Mini 5': '70',
	'iPad Mini 6': '213',
	'iPad Pro 10.5"': '25',
	'iPad Pro 11"': '29',
	'iPad Pro 11" (2G)': '151',
	'iPad Pro 11" (3G)': '203',
	'iPad Pro 12.9" (1G)': '26',
	'iPad Pro 12.9" (2G)': '27',
	'iPad Pro 12.9" (3G)': '28',
	'iPad Pro 12.9" (4G)': '120',
	'iPad Pro 12.9" (5G)': '212',
	'iPad Pro 9.7"': '24',
	'iPhone 11': '76',
	'iPhone 11 Pro': '77',
	'iPhone 11 Pro Max': '78',
	'iPhone 12': '176',
	'iPhone 12 Mini': '175',
	'iPhone 12 Pro': '177',
	'iPhone 12 Pro Max': '178',
	'iPhone 13': '206',
	'iPhone 13 Mini': '207',
	'iPhone 13 Pro': '208',
	'iPhone 13 Pro Max': '209',
	'iPhone 4': '58',
	'iPhone 4s': '194',
	'iPhone 5': '1',
	'iPhone 5C': '135',
	'iPhone 5S': '4',
	'iPhone 6': '2',
	'iPhone 6 Plus': '7',
	'iPhone 6S': '6',
	'iPhone 6S Plus': '8',
	'iPhone 7': '3',
	'iPhone 7 Plus': '9',
	'iPhone 8': '10',
	'iPhone 8 Plus': '11',
	'iPhone SE': '5',
	'iPhone SE2': '81',
	'iPhone X': '12',
	'iPhone XR': '15',
	'iPhone XS': '13',
	'iPhone XS Max': '14',
	'iPod Touch 5th Gen': '43',
	'iPod Touch 6th Gen': '44',
	'iPod Touch 7th Gen': '154'}

_MAIN_SERVICE = {
	"Courier": '0',
	"Walk-In": '1',
	"Mail-In": '14',
	"Unconfirmed": '5',
	"Booking": "16"
}

_MAIN_REPAIR_TYPE = {
	"Repair": '15',
	"Diagnostic": '2',
	"Quote Rejected": '4',
	"Unconfirmed": '5',
	"Board Level": "9",
	"Unrepairable": "18",
	"Booking Cancelled": '102',
	"No Fault Found": '109'
}

_MAIN_CLIENT = {
	"Corporate": '0',
	"Refurb": '3',
	"Unconfirmed": "5",
	"B2B": '9',
	"End User": '16',
	"Warranty": '19'
}

_DEVICE_TYPE = {  # device type, conversion to Repairs Board (Device Type Status Column)
	"iPhone": '16',
	"iPad": '19',
	"MacBook": "1",
	"Apple Watch": '107',
	"iPod": "2",
	"Device": "5"
}


def _get_product_groups():
	basic = {}
	groups = clients.monday.system.get_boards('groups.[id, title]', ids=[2477699024])[0].groups
	for group in groups:
		basic[str(group.id)] = str(group.title)
	return TwoWayDict(basic)


def get_product_repairs(group_id_or_name):
	try:
		if ' ' in group_id_or_name:
			group_id = PRODUCT_GROUPS[group_id_or_name]
		else:
			group_id = group_id_or_name
	except KeyError:
		raise Exception(f"Cannot Find Groups with ID or Name {group_id_or_name}")
	group = clients.monday.system.get_boards(
		'id',
		'groups.items.[id, name]',
		ids=[2477699024],
		groups={"ids": [group_id]})[
		0].groups[0]
	return group


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


class RepairsObject:
	def __init__(self, repair_item, repair_obj_id):

		self.item = repair_item
		self.repair_obj_id = repair_obj_id
		self.display_name = repair_item.name
		self.mon_id = repair_item.id
		self._part_ids = []
		self._parts = []

	@property
	def part_ids(self):
		return self._part_ids

	@part_ids.getter
	def part_ids(self):
		if not self._part_ids:
			self._part_ids = self.item.get_column_value(id='connect_boards8').value
		return self._part_ids


class DeviceRepairsObject:
	def __init__(self, device_group, group_eric_id):

		def _set_device_type():

			if 'iPhone' in device_group.title:
				DEVICE_TYPES['iPhone'].append(self)
				return 'iPhone'
			elif 'iPad' in device_group.title:
				DEVICE_TYPES['iPad'].append(self)
				return 'iPad'
			elif 'Apple Watch' in device_group.title:
				DEVICE_TYPES['Apple Watch'].append(self)
				return 'iPad'
			elif 'Macbook' in device_group.title or 'MacBook' in device_group.title:
				DEVICE_TYPES['MacBook'].append(self)
				return 'MacBook'
			else:
				DEVICE_TYPES['Other Device'].append(self)
				return 'Other Device'

		self.info = {
			"group": device_group,
			"mon_id": device_group.id,
			"eric_id": group_eric_id,
			"device_type": _set_device_type(),
			"display_name": device_group.title
		}

		self._repairs = []

		for repair in self.info['group'].items:
			device_repairs_obj_id = repair.name.replace(device_group.title, '').strip().replace(' ', '_').lower()
			setattr(self, device_repairs_obj_id, RepairsObject(repair, device_repairs_obj_id))
			self._repairs.append(getattr(self, device_repairs_obj_id))

	def get_slack_repair_options_data(self):
		data = []
		for repair in self._repairs:
			data.append({
				"name": repair.display_name,
				"repair_obj_id": repair.repair_obj_id,
				"mon_id": repair.mon_id,
				"part_ids":  repair.part_ids,
				"item": repair.item
			})
		return data

	def get_product_repair_by_id(self, monday_id):
		for repair in self._repairs:
			if repair.mon_id == str(monday_id):
				return repair
		raise Exception(f'Monday ID ({monday_id}) Repair Product Does Not Exist on {self.info["display_name"]}')


def get_device_type_data_for_slack():
	data = []
	for item in DEVICE_TYPES:
		name = item
		devices = DEVICE_TYPES[item]
		data.append([name, devices])
	return data


class RepairOptionsObject:
	def __init__(self):
		self._iphone = []
		self._ipad = []
		self._watch = []
		self._macbook = []
		self._other = []

		for group in _PRODUCT_BOARD.groups:
			if "cts_upl" in group.id or "ew_gro" in group.id:
				from moncli.api_v2.exceptions import MondayApiError as api_err
				print(f"creating {group.title}")
				try:
					items = group.items
				except api_err:
					print(f"archiving {group.title}")
					group.archive()
					continue
				new_group = _PRODUCT_BOARD.add_group(group.title)
				for item in items:
					print(f'moving {item.name}')
					item.move_to_group(new_group.id)
				group.archive('id')

			repair_obj_id = group.title.replace(' ', '_').lower()
			setattr(self, repair_obj_id, DeviceRepairsObject(group, repair_obj_id))

			if "iphone" in repair_obj_id:
				self._iphone.append(getattr(self, repair_obj_id))
			elif "ipad" in repair_obj_id:
				self._ipad.append(getattr(self, repair_obj_id))
			elif "watch" in repair_obj_id:
				self._watch.append(getattr(self, repair_obj_id))
			elif "macbook" in repair_obj_id:
				self._macbook.append(getattr(self, repair_obj_id))
			else:
				self._other.append(getattr(self, repair_obj_id))

	def get_devices(self, device_type):
		if device_type == "iphone":
			return self._iphone
		elif device_type == "ipad":
			return self._ipad
		elif device_type == "watch":
			return self._watch
		elif self._macbook == 'macbook':
			return self._macbook
		elif device_type == "other":
			return self._other
		else:
			raise Exception(f"Unrecognised Device Type: {device_type}")



_PRODUCT_BOARD = clients.monday.system.get_boards(
	'id',
	'groups.[id, title, items]',
	'groups.items.[id, name]',
	ids=[2477699024])[0]

MAIN_DEVICE = TwoWayDict(_MAIN_DEVICE)
MAIN_REPAIRS = TwoWayDict(_MAIN_REPAIRS)
MAIN_SERVICE = TwoWayDict(_MAIN_SERVICE)
MAIN_REPAIR_TYPE = TwoWayDict(_MAIN_REPAIR_TYPE)
DEVICE_TYPE = TwoWayDict(_DEVICE_TYPE)
MAIN_CLIENT = TwoWayDict(_MAIN_CLIENT)
PRODUCT_GROUPS = _get_product_groups()
BLOCKS_BOARD = clients.monday.system.get_board_by_id("2593044634")

DEVICE_TYPES = {
	'iPhone': [],
	'iPad': [],
	'Apple Watch': [],
	'MacBook': [],
	'Other Device': []
}

repairs = RepairOptionsObject()

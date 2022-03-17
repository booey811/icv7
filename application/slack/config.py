CHANNELS = {
	'general': 'C024H7518J3',
	'devtest': 'C036M43NBR6',
	'refurb-request': 'C0366HVGJMT'
}

USER_IDS = {
	'U024YN88KR9': 'meesha',
	'U025NA4UB96': 'mike',
	'U0254LU0CRJ': 'ricky',
	'U02KY1GTC10': 'safan',
	'U034UTKPG3S': 'seb',
	'U024H79546T': 'gabe'
}

PART_SELECTION_OPTIONS = {
	"General": [
		'Liquid Damage Treatment',
		'Software',
		'Hydrogel Protector',
		'Reshaping',
		'Logic Board'
	],
	"iPhone": [
		'Front Screen',  # will need to check for LCD/OLED variant and Manufacturer requirements
		'After Market Screen',
		'Battery',
		'Charging Port',
		'Rear Camera',
		'Front Camera',
		'Rear Lens',
		'Rear Housing',
		'Microphone',
		'Bluetooth Module',
		'Face ID',
		'Proximity Sensor',
		'Earpiece',
		'Home Button',
		'Power Button',
		'Volume Button',
		'Mute Button',
		'Loudspeaker'
	],
	"iPad": [
		'Touch Screen',
		'LCD',
		'Battery',
		'Power Button',
		'Charging Port'
	],
	"MacBook": [
		'Front Screen',
		'Battery',
		'Face ID',
		'Home Button',
		'USB Port',
		'Charging Port',
		'Keyboard',  # Requires variant: UK/US
		'Touchbar',
		'Trackpad'
	],
	"Apple Watch": [
		'Front Screen',
		'Battery',
		'Crown',
	]
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




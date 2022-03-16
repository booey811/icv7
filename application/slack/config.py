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

_ACTIONS = {
	'refurb_request': ''
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


ACTIONS = TwoWayDict(_ACTIONS)


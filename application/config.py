import settings


class Config:
	"""Base configuration"""
	pass


class ProdConfig(Config):
	ENV = 'production'
	DEBUG = False
	TESTING = False


class DevConfig(Config):
	ENV = 'development'
	DEBUG = True
	TESTING = True


class MondayUIStaffConfig:

	def __init__(self):
		self._meesha = 2477606944
		self._safan = 2477606948
		self._michael = 2477606955
		self._sebastian = 2477621450
		self._ricky = 2477621813

	def _add_properties(self):
		for key in self.__dict__:

			att = getattr(self, key)

			if type(att) is int:
				# instantiate attribute
				pass
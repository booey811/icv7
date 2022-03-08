class InvalidTypeSet(Exception):
	def __init__(self, builder, input_type, options):
		options_str = ", ".join(options)
		self.error_message = f'Invalid "type" supplied to {builder.__name__}: {input_type}\nOptions Are: {options_str}'

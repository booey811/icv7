class InvalidTypeSet(Exception):
	def __init__(self, builder, input_type, options):
		options_str = ", ".join(options)
		self.error_message = f'Invalid "type" supplied to {builder.__name__}: {input_type}\nOptions Are: {options_str}'


class CouldNotPostMessage(Exception):
	def __init__(self, response_obj):
		self.response = response_obj
		self.summary = f'Slack: {response_obj.text}'


class CannotGetChannel(Exception):
	def __init__(self, channel_input, channels):
		stri = ",".join([item for item in channels])
		self.summary = f'Cannot Find Channel: {channel_input} in slack.config.CHANNELS. Available channels: '
		print(self.summary)

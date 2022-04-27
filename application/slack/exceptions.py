import os


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


class ProductGroupNameError(Exception):
	def __init__(self, device: str):
		self.error_message = f"Could not find group with title: {device}"


class DeviceProductNotFound(Exception):
	def __init__(self, dict_key):
		self.device = dict_key

		print(f"A Produt Group has not been made for {dict_key}")


class SlackUserError(Exception):

	def __init__(self, client, footnotes='', data_points: list = None):
		if data_points is None:
			data_points = []
		self.footnotes = footnotes,
		self.data_points = data_points

		def generate_view():
			view = {
				"type": "modal",
				"callback_id": "error_report",
				"title": {
					"type": "plain_text",
					"text": "Error Reporting",
					"emoji": True
				},
				"close": {
					"type": "plain_text",
					"text": "Cancel",
					"emoji": True
				},
				"blocks": [
					{
						"type": "header",
						"text": {
							"type": "plain_text",
							"text": "Uh Oh, We Ran Into A Problem",
							"emoji": True
						}
					}
				]
			}
			if footnotes:
				secondary = {
					"type": "context",
					"elements": [
						{
							"type": "mrkdwn",
							"text": footnotes
						}
					]
				}
				# noinspection PyTypeChecker
				view['blocks'].append(secondary)
			return view

		self.view = generate_view()

		if client:

			message = f"Repair Process Aborted\nUser Saw:\n\n{footnotes}\n\nExtra Data:\n\n"

			for item in data_points:
				message += item + "\n"

			if os.environ["ENV"] == 'devlocal':
				channel = "C03D7ET6EFM"
			else:
				channel = "C03D4B8P42H"

			client.chat_postMessage(
				channel=channel,
				text=message
			)

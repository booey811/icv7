SINGLE_SELECT_OPTION = {
	"text": {
		"type": "plain_text",
		"text": "",
		"emoji": True
	},
	"value": ""
}

SINGLE_SELECT_BLOCK_WITH_RESPONSE = {
	"type": "actions",
	"elements": [{
		"type": "static_select",
		"placeholder": {
			"type": "plain_text",
			"text": "Select an item",
			"emoji": True
		},
		"options": [],
		"action_id": "actionId-3"
	}]
}

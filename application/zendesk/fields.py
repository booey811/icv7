from zenpy.lib.api_objects import CustomField


class TicketField:
    def __init__(self, zenpy_custom_field, collection, attribute_name):
        self.id = zenpy_custom_field["id"]
        self.value = zenpy_custom_field["value"]
        self.attribute_name = attribute_name
        self.related_tags = []

        self._collection = collection

    def _process_tag_data(self):
        for tag in self._collection.eric.zenpy_ticket.tags.copy():
            if f"{self.attribute_name}-" in tag:
                self.related_tags.append(tag)


class TextField(TicketField):

    def __init__(self, zenpy_custom_field, collection, attribute_name):
        super().__init__(zenpy_custom_field, collection, attribute_name)

    def adjust(self, value):
        if type(value) not in [str, int]:
            raise Exception(f"Cannot provide TextField adjust with {type(value)}")
        self._collection.eric.zenpy_ticket.custom_fields.append(CustomField(id=self.id, value=value))


class DropdownField(TicketField):

    def __init__(self, zenpy_custom_field, collection, attribute_name):
        super().__init__(zenpy_custom_field, collection, attribute_name)

        self.prefix = self.attribute_name

        self._process_tag_data()

    def adjust(self, new_id):
        if type(new_id) is list:
            new_id = new_id[0]
        try:
            str(int(new_id))
        except ValueError:
            raise Exception(f"Cannot provide TextField adjust with {type(new_id)}")

        self._collection.eric.zenpy_ticket.tags.remove(self.related_tags[0])
        self._collection.eric.zenpy_ticket.tags.extend([f"{self.attribute_name}-{new_id}"])


class MultiSelectField(TicketField):

    def __init__(self, zenpy_custom_field, collection, attribute_name):
        super().__init__(zenpy_custom_field, collection, attribute_name)

        self.prefix = self.attribute_name
        self.ids = []

        self._extract_ids_from_tags()

        self._process_tag_data()

    def _extract_ids_from_tags(self):
        tags = self._collection.eric.zenpy_ticket.tags.copy()
        for tag in tags:
            if self.attribute_name in tag:
                self.ids.append(tag.split("-")[1])

    def adjust(self, list_of_ids):
        for tag in self.related_tags:
            self._collection.eric.zenpy_ticket.tags.remove(tag)

        new_tags = []
        for dd_id in list_of_ids:
            new_tags.append(f"{self.attribute_name}-{dd_id}")
        self._collection.eric.zenpy_ticket.tags.extend(new_tags)


class CheckboxField(TicketField):

    def __init__(self, zenpy_custom_field, collection, attribute_name):
        super().__init__(zenpy_custom_field, collection, attribute_name)


class TicketFieldCollection:
    _ATTRIBUTES = {
        "360004242638": ["imeisn", TextField],
        "360004570218": ["main_id", TextField],
        "360005102118": ["passcode", TextField],
        "360006582758": ["postcode", TextField],
        "360006704157": ["courier_tracking", TextField],
        "4413411999249": ["device", DropdownField],
        "360008842297": ["repairs", MultiSelectField],
        "360005728837": ["repair_status", DropdownField],
        "360010444077": ["repair_type", DropdownField],
        "360010444117": ["service", DropdownField],
        "360010408778": ["client", DropdownField],
        "360010430958": ["on_monday", CheckboxField],
        "360006582778": ["street_address", TextField],
        "360006582798": ["pickup_instructions", TextField],
        "360008842337": ["notifications", MultiSelectField],
        "360008818998": ["device_type", DropdownField],
        "360012686858": ["enquiry_id", TextField]
    }

    def __init__(self, eric_ticket):
        self.eric = eric_ticket

        self.repair_status = TicketField
        self.service = TicketField
        self.client = TicketField
        self.repair_type = TicketField
        self.device_type = TicketField

        self.passcode = TicketField
        self.imeisn = TicketField

        self.pickup_instructions = TicketField
        self.street_address = TicketField
        self.postcode = TicketField
        self.courier_tracking = TicketField

        self.device = TicketField
        self.repairs = TicketField
        self.notifications = TicketField
        self.on_monday = TicketField
        self.main_id = TicketField
        self.enquiry_id = TicketField

        self._initialise_ticket_fields(eric_ticket.zenpy_ticket.custom_fields)

    def _initialise_ticket_fields(self, zenpy_ticket_custom_fields):
        for field in zenpy_ticket_custom_fields:
            name = self._ATTRIBUTES[str(field["id"])][0]
            eric_field = self._ATTRIBUTES[str(field["id"])][1](field, self, name)
            setattr(self, name, eric_field)

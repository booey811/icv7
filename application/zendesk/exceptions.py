class TicketNotFound(Exception):
    def __init__(self, ticket_id):
        print(f"Ticket[{ticket_id}] could not be retrieved - terminating process")

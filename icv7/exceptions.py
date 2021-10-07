class HardLog(Exception):
    def __init__(self, eric_item):
        eric_item.logger.hard_log()
        print('==== HARD LOG REQUESTED =====')

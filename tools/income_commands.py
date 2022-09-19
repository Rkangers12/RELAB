from store.handler import Handler


class IncomeCommands:

    def __init__(self, datastore=None):

        self._datastore = datastore or Handler()

        
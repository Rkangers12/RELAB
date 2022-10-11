from store.handler import Handler
from util.handle_times import HandleTimes


class BillsMonitor:
    def __init__(self, datastore=None):

        self._datastore = datastore or Handler()
        self._ht = HandleTimes()

        if self._datastore.get_value("billsData") is None:
            self._datastore.overwrite(db_key="billsData", db_value={})

    # class getters and setters
    @property
    def get_bills(self):
        """get the bills data from database"""

        return self._datastore.get_value("billsData", {})

    def get_bills_value(self, bill, default=None):
        """get the value of the requested bill data"""

        return self.get_bills.get(bill, default)

    def set_bill_matadata(self, bill, bill_metadata, bills_value):
        """set the value relating to the metadata of the bill"""

        db = self._datastore.get()  # initialise new database for overwrite
        bills_db = db.get("billsData", {})  # get the overall bills data stored

        bill_data = bills_db.get(bill, {})  # get the specific bill for metadata write
        bill_data[bill_metadata] = bills_value

        self._datastore.write_all(db)

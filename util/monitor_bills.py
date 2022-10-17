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

    def get_bills_value(self, bill, bill_metadata=None):
        """get the value of the requested bill data"""

        if bill_metadata is None:
            return self.get_bills.get(bill, {})

        return self.get_bills.get(bill).get(bill_metadata, {})

    def store_bill_metadata(self, bill, bill_metadata, bills_value):
        """store the value relating to the metadata of the bill"""

        db = self._datastore.get()  # initialise new database for overwrite
        bills_db = db.get("billsData", {})  # get the overall bills data stored
        bill_data = bills_db.get(bill, {})  # get the specific bill for metadata write

        try:
            bill_data = bills_db[bill]
        except KeyError:
            bills_db[bill] = {}
            bill_data = bills_db[bill]

        bill_data[bill_metadata] = bills_value
        self._datastore.write_all(db)

    # class helper methods
    def sort_message_content(self, content):
        """sort the content message to retrieve the relevant information"""

        content_listed = content.lower().split(".")[2:]
        content_dict = {}

        for obj_string in content_listed:

            obj_string = obj_string.split("=")
            content_dict[obj_string[0]] = obj_string[1]

        return content_dict

    def process_bill(self, data):
        """method to isolate storing of bill data to one location"""

        bill_store = self.get_bills_value(data["bill"])

        self.store_bill_metadata(
            data["bill"],
            "debit_day",
            min(31, int(data.get("day") or bill_store.get("debit_day", 1))),
        )

        self.store_bill_metadata(
            data["bill"],
            "expense",
            float(data.get("cost") or bill_store.get("expense", 0)),
        )

    # class functional methods
    def set(self, content):
        """set the data for the bill"""

        try:
            bill_dict = self.sort_message_content(content)
        except IndexError:
            return 404

        self.process_bill(bill_dict)
        return 200

    def get(self, content):
        """get the individual data within bills from database"""

        bill_dict = self.sort_message_content(content)

        return self.get_bills_value(
            bill_dict.get("bill"), bill_metadata=bill_dict.get("metadata", None)
        )

    def get_all(self):
        """get all bills within bills from database"""

        bills = self.get_bills
        messages = []

        date_suffix = None

        for bill in bills:
            bill_info = bills.get(bill, {})
            messages.append(
                "{} bill is payable on the {}{} for the amount showing £{}.".format(
                    bill.title(),
                    bill_info.get("debit_day"),
                    self._ht.day_suffix(bill_info.get("debit_day")),
                    bill_info.get("expense"),
                )
            )

        return messages

    def delete(self, content):
        """delete a bill stored within the database"""

        try:
            bill_dict = self.sort_message_content(content)
        except IndexError:
            return 404

        db = self._datastore.get()
        bills_db = db.get("billsData", {})
        bills_db.pop(bill_dict.get("bill"), None)

        self._datastore.write_all(db)

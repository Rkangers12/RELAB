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

    def get_bill_val(self, bill, bill_metadata=None):
        """get the value of the requested bill data"""

        if bill_metadata is None:
            return self.get_bills.get(bill, {})

        return self.get_bills.get(bill, {}).get(bill_metadata, {})

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

        bill_store = self.get_bill_val(data["bill"])

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

    def format_bill(self, data):
        """format the bill data into a message for users"""

        dday = data.get("debit_day", False)
        md_day = True if data.get("debit_day") is not None else False
        md_exp = True if data.get("expense") is not None else False

        bill = "**{}** ".format(data.get("bill")).title()
        bill_day = "is payable on the **{}{}** ".format(dday, self._ht.day_suffix(dday))
        bill_exp = "for the amount £**{}**".format(data.get("expense"))

        return bill + (bill_day if md_day else "") + (bill_exp if md_exp else "") + "."

    # class functional methods
    def set(self, content):
        """set the data for the bill"""

        try:
            bill_dict = self.sort_message_content(content)
        except IndexError:
            return 404

        self.process_bill(bill_dict)
        return 200

    def get_bill(self, content):
        """get the individual data within bills from database"""

        bill_dict = self.sort_message_content(content)
        if bill_dict.get("bill") not in self.get_bills.keys():
            return 404

        bill_dict.pop("metadata", 0)

        return bill_dict | self.get_bill_val(bill_dict.get("bill"))

    def get_bill_meta(self, content):
        """get the individual metadata for a bill from database"""

        bill_dict = self.sort_message_content(content)

        if bill_dict.get("bill") not in self.get_bills.keys():
            return 404

        try:
            bill_dict[bill_dict.pop("metadata")] = self.get_bill_val(
                bill_dict.get("bill"), bill_metadata=bill_dict.get("metadata", None)
            )
        except KeyError:
            return 404

        return bill_dict

    def get_all(self):
        """get all bills within bills from database"""

        bills = self.get_bills
        bills_list = []

        for bill in bills:
            bill_info = bills.get(bill, {})
            bill_info["bill"] = bill
            bills_list.append(bill_info)

        return bills_list

    def delete(self, content):
        """delete a bill stored within the database"""

        try:
            bill_dict = self.sort_message_content(content)
        except IndexError:
            return 404

        db = self._datastore.get()
        bills_db = db.get("billsData", {})
        try:
            bills_db.pop(bill_dict.get("bill"))
        except KeyError:
            return 404

        self._datastore.write_all(db)

        return 200

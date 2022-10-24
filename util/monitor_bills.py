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

    def store_bill_metadata(self, data):
        """store the value relating to the metadata of the bill"""

        bill_store = self._datastore.get_nested_value(
            ["billsData", data["bill"]], default={}
        )

        self._datastore.overwrite_nested(
            keys_list=["billsData", data["bill"]],
            last_key="debit_day",
            db_value=min(31, int(data.get("day") or bill_store.get("debit_day", 1))),
        )

        self._datastore.overwrite_nested(
            keys_list=["billsData", data["bill"]],
            last_key="expense",
            db_value=int(data.get("cost") or bill_store.get("expense", 1)),
        )

    # class helper methods
    def sort_message_content(self, content):
        """sort the content message to retrieve the relevant information"""

        try:
            content_listed = content.lower().split(".")[2:]
            content_dict = {}

            for obj_string in content_listed:

                obj_string = obj_string.split("=")
                content_dict[obj_string[0]] = obj_string[1]
        except IndexError:
            pass

        return content_dict

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

        bdict = self.sort_message_content(content)

        if "bill" not in bdict or ("day" not in bdict and "cost" not in bdict):
            return 404

        self.store_bill_metadata(bdict)
        return 200

    def get_bill(self, content):
        """get the individual data within bills from database"""

        bdict = self.sort_message_content(content)

        if bdict.get("bill") not in self.get_bills.keys() or "bill" not in bdict.keys():
            return 404

        bdict = {"bill": bdict.pop("bill")}
        return bdict | self._datastore.get_nested_value(["billsData", bdict["bill"]])

    def get_bill_meta(self, content):
        """get the individual metadata for a bill from database"""

        bdict = self.sort_message_content(content)

        if bdict.get("bill") not in self.get_bills.keys() or "bill" not in bdict.keys():
            return 404

        if bdict.get("metadata") not in ["debit_day", "expense"]:
            return 404

        bdict[bdict.pop("metadata")] = self._datastore.get_nested_value(
            ["billsData", bdict["bill"], bdict["metadata"]]
        )

        return bdict

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

        bill_dict = self.sort_message_content(content)

        db = self._datastore.get()
        bills_db = db.get("billsData", {})

        try:
            bills_db.pop(bill_dict.get("bill"))
        except KeyError:
            return 404

        self._datastore.write_all(db)

        return 200

from store.handler import Handler
from util.handle_times import HandleTimes


class Monitor:
    def __init__(self, monitor, db_key, datastore=None):

        self._monitor = monitor
        self._key = db_key
        self._datastore = datastore or Handler()
        self._ht = HandleTimes()

        if self._datastore.get_value(self._key) is None:
            self._datastore.overwrite(db_key=self._key, db_value={})

    # class getters and setters
    @property
    def get_data(self):
        """get the data for specified key from database"""

        return self._datastore.get_value(self._key, {})

    def store_data(self, data):
        """store the value relating to the metadata of the monitor"""

        db_store = self._datastore.get_nested_value(
            [self._key, data[self._monitor]], default={}
        )

        self._datastore.overwrite_nested(
            keys_list=[self._key, data[self._monitor]],
            last_key="debit_day",
            db_value=min(31, int(data.get("day") or db_store.get("debit_day", 1))),
        )

        self._datastore.overwrite_nested(
            keys_list=[self._key, data[self._monitor]],
            last_key="expense",
            db_value=int(data.get("cost") or db_store.get("expense", 1)),
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

    def format_message(self, data):
        """format the retrieved data into a message for users"""

        dday = data.get("debit_day", False)
        md_day = True if data.get("debit_day") is not None else False
        md_exp = True if data.get("expense") is not None else False

        obj = "**{}** ".format(data.get(self._monitor)).title()
        obj_day = "is payable on the **{}{}** ".format(dday, self._ht.day_suffix(dday))
        obj_exp = "for the amount £**{}**".format(data.get("expense"))

        return obj + (obj_day if md_day else "") + (obj_exp if md_exp else "") + "."

    # class functional methods
    def set(self, content):
        """set the data for the specified monitor"""

        mdict = self.sort_message_content(content)

        if self._monitor not in mdict or ("day" not in mdict and "cost" not in mdict):
            return 404

        self.store_data(mdict)
        return 200

    def get(self, content):
        """get the individual data within provided monitor from database"""

        mdict = self.sort_message_content(content)

        if (
            mdict.get(self._monitor) not in self.get_data.keys()
            or self._monitor not in mdict.keys()
        ):
            return 404

        mdict = {self._monitor: mdict.pop(self._monitor)}
        return mdict | self._datastore.get_nested_value(
            [self._key, mdict[self._monitor]]
        )

    def get_meta(self, content):
        """get the individual metadata for provided monitor from database"""

        mdict = self.sort_message_content(content)

        if (
            mdict.get(self._monitor) not in self.get_data.keys()
            or self._monitor not in mdict.keys()
        ):
            return 404

        if mdict.get("metadata") not in ["debit_day", "expense"]:
            return 404

        mdict[mdict.pop("metadata")] = self._datastore.get_nested_value(
            [self._key, mdict[self._monitor], mdict["metadata"]]
        )

        return mdict

    def get_all(self):
        """get all records for provided monitor within database"""

        monitor_records = self.get_data
        records = []

        for record in monitor_records:
            record_info = monitor_records.get(self._monitor, {})
            record_info[self._monitor] = record
            records.append(record_info)

        return records

    def delete(self, content):
        """delete a record for monitor stored within the database"""

        mdict = self.sort_message_content(content)

        db = self._datastore.get()
        monitor_db = db.get(self._key, {})

        try:
            monitor_db.pop(mdict.get(self._monitor))
        except KeyError:
            return 404

        self._datastore.write_all(db)

        return 200

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

    def store_data(self, mdict, data, meta_key):
        """store the value relating to the metadata of the monitor"""

        self._datastore.overwrite_nested(
            keys_list=[self._key, data],
            last_key=meta_key,
            db_value=mdict.get(meta_key),
        )

    # class helper methods
    def sort_message_content(self, content):
        """sort the content message to retrieve the relevant information"""

        content_listed = content.lower().split(":")[1:]
        content_dict = {}

        for obj_string in content_listed:
            try:
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
    def set(self, content, pdict=None):
        """set the data for the specified monitor"""

        mdict = pdict or self.sort_message_content(content)

        if self._monitor not in mdict.keys():
            return 404

        if (mdict.get("debit_day") and mdict.get("expense")) is not None:
            try:
                mdict["debit_day"] = min(31, int(mdict["debit_day"]))
                mdict["expense"] = float(mdict["expense"])
            except ValueError:
                return 404

            monitor_val = mdict.pop(self._monitor)

            for meta_key in mdict:
                self.store_data(mdict, monitor_val, meta_key)

            return 200

        return 404

    def update(self, content, pdict=None):
        """update the data for the specific monitor"""

        mdict = pdict or self.sort_message_content(content)
        monitor = self.get_data

        if self._monitor not in mdict.keys() or mdict.get(self._monitor) not in monitor:
            return 404

        if mdict.get("debit_day") is not None:
            try:
                mdict["debit_day"] = min(31, int(mdict["debit_day"]))
            except ValueError:
                return 404

        if mdict.get("expense") is not None:
            try:
                mdict["expense"] = float(mdict["expense"])
            except ValueError:
                return 404

        monitor_val = mdict.pop(self._monitor)

        for meta_key in mdict:
            self.store_data(mdict, monitor_val, meta_key)

        return 200

    def get(self, content):
        """get the individual data within provided monitor from database"""

        mdict = self.sort_message_content(content)
        monitor = self.get_data

        if mdict.get(self._monitor) not in monitor or self._monitor not in mdict.keys():
            return 404

        mdict = {self._monitor: mdict.pop(self._monitor)}

        return mdict | self._datastore.get_nested_value(
            [self._key, mdict[self._monitor]]
        )

    def get_meta(self, content, pdict=None):
        """get the individual metadata for provided monitor from database"""

        mdict = pdict or self.sort_message_content(content)
        monitor = self.get_data

        if mdict.get(self._monitor) not in monitor or self._monitor not in mdict.keys():
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
            record_info = monitor_records.get(record, {})
            record_info[self._monitor] = record
            records.append(record_info)

        return records

    def delete(self, content):
        """delete a record for monitor stored within the database"""

        mdict = self.sort_message_content(content)

        res = self._datastore.delete_nested(
            keys_list=[self._key], last_key=mdict.get(self._monitor)
        )

        return 200 if res is not None else 404

    def delete_meta(self, content, pdict=None):
        """delete the meta key for monitor stored within the database"""

        mdict = pdict or self.sort_message_content(content)
        res = None

        if mdict.get("metadata") not in ["debit_day", "expense"]:
            res = self._datastore.delete_nested(
                keys_list=[self._key, mdict.get(self._monitor)],
                last_key=mdict.get("metadata"),
            )

        return 200 if res is not None else 404

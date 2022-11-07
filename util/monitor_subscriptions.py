from util.monitor import Monitor


class SubscriptionsMonitor(Monitor):
    def register(self, content):
        """register new subscriptions for monitoring"""

        pdict = self.sort_message_content(content)

        self.delete(":subscription=" + pdict.get(self._monitor))
        pdict["active"] = True
        res = self.set(content, pdict=pdict)

        return res

    def extend_update(self, content):
        """update existing subscriptions for monitoring"""

        pdict = self.sort_message_content(content)
        pdict.pop("active", 0)

        res = self.update(content, pdict=pdict)

        return res

    def extend_delete_meta(self, content):
        """delete metadata from subscriptions"""

        pdict = self.sort_message_content(content)

        if pdict.get("metadata") == "active":
            return 404

        return self.delete_meta(content, pdict=pdict)

    def pause(self, content):
        "pause/unpause subscription"

        pdict = self.sort_message_content(content)
        monitor = self.get_data

        if self._monitor not in pdict or pdict.get(self._monitor) not in monitor:
            return {"statusCode": 404}

        active = self._datastore.get_nested_value(
            [self._key, pdict[self._monitor], "active"]
        )

        if active:
            self._datastore.overwrite_nested(
                keys_list=[self._key, pdict[self._monitor]],
                last_key="active",
                db_value=False,
            )
            active = False
        else:
            self._datastore.overwrite_nested(
                keys_list=[self._key, pdict[self._monitor]],
                last_key="active",
                db_value=True,
            )
            active = True

        return {
            "subscription": pdict[self._monitor],
            "statusCode": 200,
            "active": active,
        }

    def extend_get_meta(self, content):
        """extend - get the individual metadata for provided monitor from database"""

        pdict = self.sort_message_content(content)
        pdict["active"] = self._datastore.get_nested_value(
            [self._key, pdict.get(self._monitor), "active"]
        )

        return self.get_meta(content, pdict=pdict)

    def subscription_active(self, sub):
        """check to see if the subscription is active"""

        return self._datastore.get_nested_value([self._key, sub, "active"])

    def format_message(self, data):
        """format the retrieved data into a message for users"""

        md_day = True if data.get("debit_day") is not None else False
        md_exp = True if data.get("expense") is not None else False

        obj = "{} is payable".format(data.get(self._monitor).title())
        obj_day = " on the {}{}".format(
            data.get("debit_day"), self._ht.day_suffix(data.get("debit_day", 0))
        )
        obj_exp = " for the amount £{}".format(data.get("expense"))

        message = obj + (obj_day if md_day else "") + (obj_exp if md_exp else "") + "."

        return "**" + message + "***" if data.get("active") else message

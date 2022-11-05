from util.monitor import Monitor


class SubscriptionsMonitor(Monitor):
    def register(self, content):
        """register new subscriptions for monitoring"""

        pdict = self.sort_message_content(content)
        res = 404

        if pdict.get("active") is not None:
            pdict["active"] = pdict["active"] in ("true", 1)
            res = self.set(content, pdict=pdict)

        return res

    def extend_update(self, content):
        """update existing subscriptions for monitoring"""

        pdict = self.sort_message_content(content)
        res = 404

        if pdict.get("active") is not None:
            pdict["active"] = pdict["active"] in ("true", 1)
            res = self.update(content, pdict=pdict)

        return res

    def extend_delete_meta(self, content):

        pdict = self.sort_message_content(content)

        if pdict.get("metadata") == "active":
            return 404

        return 200 if self.delete_meta(content, pdict=pdict) is not None else 404

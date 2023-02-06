from util.monitor import Monitor


class SubscriptionsMonitor(Monitor):
    def extend_create(self, name, expiration, limit):
        """extend the existing creating objects method"""

        res = self.create(name, expiration, limit)

        if res == 200:
            self._datastore.overwrite_nested([self._monitor, name], "active", True)

        return res

    def toggle_subscription(self, name):
        """toggle the object to active or in-active"""

        if self.check_exists(name):
            active = self.active(name)
            if active:
                self._datastore.overwrite_nested([self._monitor, name], "active", False)
            else:
                self._datastore.overwrite_nested([self._monitor, name], "active", True)

            return active

        return 404

    def active(self, name):
        """check to see if object is active"""

        return self._datastore.get_nested_value([self._monitor, name, "active"])

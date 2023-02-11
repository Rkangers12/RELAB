from util.monitor import Monitor


class SubscriptionsMonitor(Monitor):
    def extend_create(self, name, expiration, limit, user):
        """extend the existing creating objects method"""

        res = self.create(name, expiration, limit, user)

        if res == 200:
            self._datastore.overwrite_nested(
                ["users", user, self._monitor, name], "active", True
            )

        return res

    def toggle_subscription(self, name, user):
        """toggle the object to active or in-active"""

        if self.check_exists(name, user):
            active = self.active(name, user)
            if active:
                self._datastore.overwrite_nested(
                    ["users", user, self._monitor, name], "active", False
                )
            else:
                self._datastore.overwrite_nested(
                    ["users", user, self._monitor, name], "active", True
                )

            return active

        return 404

    def active(self, name, user):
        """check to see if object is active"""

        return self._datastore.get_nested_value(
            ["users", user, self._monitor, name, "active"]
        )

from tools.handler import Handler
from util.handle_times import HandleTimes


class Monitor:
    def __init__(self, monitor, datastore=None):

        self._monitor = monitor
        self._datastore = datastore or Handler()
        self._handletime = HandleTimes()

    def check_exists(self, name):
        """check if the object already exists"""

        if name in self.get_all:
            return True

    def create(self, name, expiration, limit, user):
        """store the object within the database"""

        if not self.check_exists(name):
            try:
                obj = {
                    "expiration": min(31, int(expiration)),
                    "limit": float(limit),
                    "user": user,
                }
            except (IndexError, ValueError):
                return 404
            else:
                self._datastore.overwrite_nested([self._monitor], name, obj)
                return 200

        return 201

    def modify_limit(self, name, limit):
        """change the object limit to new value"""

        if self.check_exists(name):
            try:
                self._datastore.overwrite_nested(
                    [self._monitor, name], "limit", float(limit)
                )
            except ValueError:
                return 404

            return 200

        return 204

    def modify_expiration(self, name, expiration):
        """change the object expiration to new value"""

        if self.check_exists(name):
            try:
                exp = min(31, int(expiration))
                self._datastore.overwrite_nested(
                    [self._monitor, name], "expiration", exp
                )
            except ValueError:
                return 404

            return 200

        return 204

    def get(self, name, user):
        """get the object data from the database"""

        if self.check_exists:
            return self._datastore.get_nested_value([self._monitor, name])

    @property
    def get_all(self):
        """get all of object within the database"""

        return self._datastore.get_nested_value([self._monitor])

    def delete(self, name):
        """delete the object from the database"""

        if self.check_exists(name):
            self._datastore.delete_nested([self._monitor], name)
            return 200
        else:
            return 201

    @property
    def delete_all(self):
        """delete all the objects within the database"""

        names = self.get_all.keys()
        outcome = {"deleted": [], "failed": []}

        for name in names:
            if self.delete(name) == 200:
                outcome["deleted"].append(name)
            else:
                outcome["failed"].append(name)

        return outcome

from util.monitor import Monitor


class NotesMonitor(Monitor):
    def create(self, name, day, desc, user, quick=False):
        """store the object within the database"""

        if not self.check_exists(name, user):
            try:
                obj = {"desc": desc, "day": min(31, int(day))}
            except (IndexError, ValueError):
                return 404
            else:
                obj["repeat"] = True if not quick else False
                self._datastore.overwrite_nested(
                    ["users", user, self._monitor], name, obj
                )
                return 200

        return 201

    def modify_desc(self, name, desc, user):
        """change the object desc to new value"""

        if self.check_exists(name, user):
            self._datastore.overwrite_nested(
                ["users", user, self._monitor, name], "desc", desc
            )
            return 200

        return 204

    def modify_day(self, name, day, user):
        """change the object's alert day to new value"""

        if self.check_exists(name, user):
            try:
                day = min(31, int(day))
                self._datastore.overwrite_nested(
                    ["users", user, self._monitor, name], "day", day
                )
            except ValueError:
                return 404

            return 200

        return 204

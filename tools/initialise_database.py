class DatastoreInit:
    def __init__(self, datastore):

        self._datastore = datastore

        if self._datastore.get() == {}:
            self.init_settings
            self.init_users

    @property
    def init_users(self):
        """initialise the users within the database"""

        self._datastore.overwrite(db_key="users", db_value={})

    @property
    def init_settings(self):
        """initialise the settings within the database"""

        self._datastore.overwrite(db_key="settings", db_value={})
        self._datastore.overwrite_nested(["settings"], "power", True)

    def setup_user(self, user, unique_id):
        """set up the user within the database"""

        # initialise the user
        self._datastore.overwrite_nested(["users"], user, {})

        self._datastore.overwrite_nested(
            ["users", user], "REPORTER", f"REPORTER_{unique_id}"
        )
        self._datastore.overwrite_nested(["users", user], "RELAB", f"RELAB_{unique_id}")

        self.init_sessions(user)
        self.init_monitors(user)
        self.init_payroll(user)
        self.init_budget(user)

    def init_sessions(self, user):
        """initialise the sessions feature into the database"""

        self._datastore.overwrite_nested(["users", user], "sessions", {})
        self._datastore.overwrite_nested(
            ["users", user, "sessions"], "currentSession", {}
        )
        self._datastore.overwrite_nested(["users", user, "sessions"], "gymRecords", {})
        self._datastore.overwrite_nested(
            ["users", user, "sessions"], "studyRecords", {}
        )
        self._datastore.overwrite_nested(["users", user, "sessions"], "studying", False)
        self._datastore.overwrite_nested(["users", user, "sessions"], "gymming", False)

    def init_monitors(self, user):
        """initialise the monitors within the database"""

        self._datastore.overwrite_nested(["users", user], "bill", {})
        self._datastore.overwrite_nested(["users", user], "subscription", {})
        self._datastore.overwrite_nested(["users", user], "note", {})

    def init_payroll(self, user):
        """initialise the payroll within the database"""

        key = "payrollData"
        self._datastore.overwrite_nested(["users", user], key, {})
        self._datastore.overwrite_nested(["users", user, key], "grossSalary", 1)
        self._datastore.overwrite_nested(["users", user, key], "notionals", 1)
        self._datastore.overwrite_nested(["users", user, key], "payDay", 0)
        self._datastore.overwrite_nested(["users", user, key], "activeSL", False)

    def init_budget(self, user):
        """initialise the budget system within the database"""

        key = "budgetData"

        self._datastore.overwrite_nested(["users", user], key, {})
        self._datastore.overwrite_nested(["users", user, key], "budgets", {})
        self._datastore.overwrite_nested(["users", user, key], "archive", {})
        self._datastore.overwrite_nested(["users", user, key], "threshold", {})

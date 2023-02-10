class DatastoreInit:
    def __init__(self, datastore):

        self._datastore = datastore

        if self._datastore.get() == {}:
            self.init_budget
            self.init_monitors
            self.init_payroll
            self.init_sessions
            self.init_settings
            self.init_users

    @property
    def init_sessions(self):
        """initialise the sessions feature into the database"""

        self._datastore.overwrite(db_key="sessions", db_value={})

    def setup_user(self, user):
        """set up the user within the database"""

        # setup within sessions
        self._datastore.overwrite_nested(["sessions"], user, {})
        self._datastore.overwrite_nested(["sessions", user], "currentSession", {})
        self._datastore.overwrite_nested(["sessions", user], "gymRecords", {})
        self._datastore.overwrite_nested(["sessions", user], "studyRecords", {})
        self._datastore.overwrite_nested(["sessions", user], "studying", False)
        self._datastore.overwrite_nested(["sessions", user], "gymming", False)

    @property
    def init_monitors(self):
        """initialise the monitors within the database"""
        self._datastore.overwrite(db_key="bill", db_value={})
        self._datastore.overwrite(db_key="subscription", db_value={})
        self._datastore.overwrite(db_key="note", db_value={})

    @property
    def init_payroll(self):
        """initialise the payroll within the database"""
        self._datastore.overwrite(db_key="patrollData", db_value={})

    @property
    def init_budget(self):
        """initialise the budget system within the database"""

        budget_key = "budgetData"
        self._datastore.overwrite(db_key=budget_key, db_value={})
        self._datastore.overwrite_nested([budget_key], "budgets", {})
        self._datastore.overwrite_nested([budget_key], "archive", {})
        self._datastore.overwrite_nested([budget_key], "thresholds", {})

    @property
    def init_settings(self):
        """initialise the settings within the database"""

        self._datastore.overwrite(db_key="settings", db_value={})
        self._datastore.overwrite_nested(["settings"], "power", True)

    @property
    def init_users(self):
        """initialise the users within the database"""

        self._datastore.overwrite(db_key="users", db_value={})

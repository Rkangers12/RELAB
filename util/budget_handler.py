from datetime import datetime
from uuid import uuid4

from util.handle_times import HandleTimes
from store.handler import Handler


class BudgetHandler:
    def __init__(self, datastore=None):

        self._budgetkey = "budgetData"
        self._datastore = datastore or Handler()
        self._handletime = HandleTimes()

        if self._datastore.get_value(self._budgetkey) is None:
            self._datastore.overwrite(db_key=self._budgetkey, db_value={})
            self.set_threshold()
            self.reset_archive()
            self._datastore.overwrite_nested([self._budgetkey], "budgets", {})

    def set_threshold(self, threshold=0):
        """set the threshold of the budget alert"""

        self._datastore.overwrite_nested([self._budgetkey], "threshold", threshold)

    @property
    def get_threshold(self):
        """get the threshold value for budget alerting"""
        return self._datastore.get_nested_value([self._budgetkey, "threshold"])

    @property
    def reset_archive(self):
        """reset archive store of budgets"""

        self._datastore.overwrite_nested([self._budgetkey], "archive", {})

    def create_budget(self, name, expiration, limit):
        """store the budget within the database"""

        if self.check_budget_exists(name):
            print("DEBUG: Budget exists.")
            return 201

        try:
            budget = {
                "creation": str(self._handletime.format_a_day(datetime.now().day)),
                "expiration": str(self._handletime.format_a_day((expiration))),
                "limit": float(limit),
                "spending": 0.00,
            }
        except ValueError:
            pass
        else:
            self._datastore.overwrite_nested([self._budgetkey, "budgets"], name, budget)

    def check_budget_exists(self, name):
        """check if the budget is already existing"""

        if name in self.get_all_budgets:
            return True

    def modify_budget_limit(self, name, limit):
        """change the budget limit to new value"""

        self._datastore.overwrite_nested(
            [self._budgetkey, "budgets", name], "limit", limit
        )

    def modify_budget_expiration(self, name, expiration):
        """change the budget expiration to new value"""

        self._datastore.overwrite_nested(
            [self._budgetkey, "budgets", name],
            "expiration",
            str(self._handletime.format_a_day((expiration))),
        )

    def get_budget(self, name):
        """get the data of the provided data"""

        return self._datastore.get_nested_value([self._budgetkey, "budgets", name])

    @property
    def get_all_budgets(self):
        """get all budgets within the database"""

        return self._datastore.get_nested_value([self._budgetkey, "budgets"])

    @property
    def get_all_archived(self):
        """get all archived budgets within the database"""

        return self._datastore.get_nested_value([self._budgetkey, "archive"])

    def record_spending(self, name, spending):
        """record spending to existing budget"""

        budget = self.get_budget(name)
        spending = budget["spending"] + spending

        self._datastore.overwrite_nested(
            [self._budgetkey, "budgets", name], "spending", spending
        )

        res = 200
        remaining = self.get_remaining(name)

        if remaining < 0:
            res = 401
        elif remaining < self.get_threshold:
            res = 204

        return res

    def get_remaining(self, name):
        """get the spending remaining for a budget"""

        budget = self.get_budget(name)

        return budget.get("limit") - budget.get("spending")

    def delete_budget(self, name):
        """delete a budget within the database"""

        self._datastore.delete_nested([self._budgetkey, "budgets"], name)

    def archive_budget(self, name):
        """re-locate an existing budget to the archives"""

        budget = self.get_budget(name)
        budget["og_name"] = name
        idify = f"{name}_{uuid4().hex[:6]}"

        self._datastore.overwrite_nested([self._budgetkey, "archive"], idify, budget)
        self.delete_budget(name)

    def check_expired(self, name):
        """compare expiration against today's date"""

        # retrieve today's day to compare against expiration
        today = str(self._handletime.format_a_day(datetime.now().day))
        budget = self.get_budget(name)

        if today == budget.get("expiration"):
            self.archive_budget(name)
            return True

    @property
    def budget_spending(self):
        """identify spending in all budgets"""

        budgets = self.get_all_budgets

        expenditure = 0
        for budget in budgets:
            expenditure += budgets.get(budget, {}).get("spending", 0)

        return expenditure

    @property
    def archive_spending(self):
        """identify spending in all archived budgets"""

        budgets = self.get_all_archived

        expenditure = 0
        for budget in budgets:
            expenditure += budgets.get(budget, {}).get("spending", 0)

        return expenditure
